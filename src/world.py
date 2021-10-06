import gzip
import pickle
from collections import deque
import time
from typing import Tuple
import threading
from queue import Empty, Queue

import arcade
from entities.player import Player
from misc.camera import CustomCamera
from misc.terrain import gen_world
from utils import Timer
from misc.chunk import HorizontalChunk
import config


class World:

    def __init__(self, *, screen_size: Tuple, name: str) -> None:
        """
        :param screen_size: Size of the screen
        :param str name: Name of the world
        """
        self._screen_size = screen_size
        self._name = name
        self._player_default_x = 20 * 8  # 8 block to the right on the first chunk
        self._player_default_y = 20 * 210  # 210 chunks up

        # Player
        # TODO: Find a safe initial spawn position
        self._player_list: arcade.SpriteList = arcade.SpriteList()
        self._player_sprite = Player(
            "player",
            scale=config.PLAYER_SCALING,
            center_x=self._player_default_x,
            center_y=self._player_default_y,
            screen_width=config.SCREEN_WIDTH,
            screen_height=config.SCREEN_HEIGHT,
            movement_speed=config.MOVEMENT_SPEED,
            jump_speed=config.JUMP_SPEED,
            flipped_horizontally=False,
        )
        self._player_list.append(self._player_sprite)

        # Initial physics engine with no chunks
        self._physics_engine: arcade.PhysicsEnginePlatformer = arcade.PhysicsEnginePlatformer(
            self._player_sprite,
            [],
            gravity_constant=config.GRAVITY,
        )
        self._player_sprite.physics_engine = self._physics_engine

        # All chunks
        self._whole_world: dict = dict()
        # Visible chunks
        self._active_chunks: deque = deque()

        self.camera = CustomCamera(*self._screen_size)

        # Chunk loader
        self._chunk_loader = ChunkLoader()
        self._requested_chunks = set()  # Keep track of requested chunks

    @property
    def player(self) -> Player:
        return self._player_sprite

    def draw(self):
        arcade.set_background_color(arcade.color.AMAZON)
        self.camera.use()

        for chunk in self._active_chunks:
            chunk.draw()

        self._player_list.draw(pixelated=True)
        self.debug_draw_chunks()

    def update(self):
        """Called every frame to update the world state"""
        self.camera.center_camera_to_player(self._player_sprite)
        self.update_visible_chunks()
        self.process_new_chunks()

        if self._player_sprite.center_y < -100:
            self._player_sprite.set_position(self._player_default_x, self._player_default_y)
        self._physics_engine.update()

    def create(self):
        """Create the initial world state"""
        yield from self.setup_world()

    def process_new_chunks(self):
        # Get loaded chunks from threaded chunk loader
        new_chunks = self._chunk_loader.get_loaded_chunks(max_results=1)
        for chunk in new_chunks:
            print("New chunk data processed", type(chunk))
            self._requested_chunks.remove(chunk.index)
            self._whole_world[chunk.index] = chunk

    def request_chunk(self, chunk_id: int):
        """Request a new chunk"""
        # Ensure we don't request the same chunk multiple times
        if chunk_id in self._requested_chunks:
            return

        print("Requesting new chunk", chunk_id)
        self._chunk_loader.queue_in.put(chunk_id)
        self._requested_chunks.add(chunk_id)

    def update_visible_chunks(self) -> Tuple[bool, bool]:
        """Detect and update visible chunks"""
        changed = False  # Did visible chunks change?
        visible_loaded = True  # Are all visible chunks loaded?

        # If we have no active chunks, add the chunk the player is located in
        if not self._active_chunks:
            chunk = self._whole_world.get(self._player_sprite.chunk)
            # If the player is not located in a chunk we have nothing to do
            if not chunk:
                self.request_chunk(self._player_sprite.chunk)
                return False, False

            self._active_chunks.append(chunk)
            changed = True

        player_x = self._player_sprite.center_x
        view_dist = config.VISIBLE_RANGE_MAX * 20

        # Fill visible chunks from left side
        while self._active_chunks[0].is_visible(player_x, view_dist):
            index = self._active_chunks[0].index - 1
            new_chunk = self._whole_world.get(index)
            if not new_chunk:
                self.request_chunk(index)
                visible_loaded = False
                break
            elif not new_chunk.is_visible(player_x, view_dist):
                break

            self._active_chunks.appendleft(new_chunk)
            changed = True

        # Fill visible chunks from right side
        while self._active_chunks[-1].is_visible(player_x, view_dist):
            index = self._active_chunks[-1].index + 1
            new_chunk = self._whole_world.get(index)
            if not new_chunk:
                self.request_chunk(index)
                visible_loaded = False
                break
            elif not new_chunk.is_visible(player_x, view_dist):
                break

            self._active_chunks.append(new_chunk)
            changed = True

        # Remove invisible chunks from left side
        while self._active_chunks and not self._active_chunks[0].is_visible(player_x, view_dist):
            chunk = self._active_chunks.popleft()
            changed = True

        # Remove invisible chunks from right side
        while self._active_chunks and not self._active_chunks[-1].is_visible(player_x, view_dist):
            chunk = self._active_chunks.pop()
            changed = True

        # Update chunks for the physics engine
        if changed:
            self._physics_engine.platforms = [chunk.spritelist for chunk in self._active_chunks]

        return visible_loaded, changed

    def setup_world(self) -> None:
        config.DATA_DIR.mkdir(exist_ok=True)
        # try:
        #     load_timer = Timer("load_world")

        #     for n in range(int(config.VISIBLE_RANGE_MIN / 16), int(config.VISIBLE_RANGE_MAX / 16) + 1):
        #         chunk_timer = self._chunk_loader(n)
        #         print(f"Loaded chunk {n} in {chunk_timer.stop()} seconds")

        #     print(f"Loaded chunks in {load_timer.stop()} seconds")
        # except FileNotFoundError:
        #     print("Failed to load chunks. Generating world...")
        #     timer = Timer("world_gen")

        #     # Create empty chunks
        #     for n in range(-31, 31):
        #         self._whole_world[n] = HorizontalChunk(n * 16, n)

        #     world = gen_world(-496, 496, 0, 320)
        #     for k, chunk_data in world.items():
        #         n = int(k[1] / 16)
        #         self._whole_world[n]['setter'] = chunk_data

        #     print(f"Generated world in {timer.stop()} seconds")

        #     print("Saving world")
        #     timer = Timer("world_save")
        #     for n, chunk in self._whole_world.items():
        #         with gzip.open(config.DATA_DIR / f"pickle{pickle.format_version}_{n}.pickle", "wb") as f:
        #             pickle.dump(chunk.data, f)
        #             chunk.make_sprite_list()

        #     print(f"Saved wold in {timer.stop()} seconds")

    def debug_draw_chunks(self):
        """Draw chunk borders with lines"""
        for chunk in self._active_chunks:
            arcade.draw_line(
                chunk.world_x,
                0,
                chunk.world_x,
                config.CHUNK_WIDTH_PIXELS,
                arcade.color.RED,
            )
            arcade.draw_line(
                chunk.world_x + config.CHUNK_WIDTH_PIXELS,
                0,
                chunk.world_x + config.CHUNK_WIDTH_PIXELS,
                config.CHUNK_HEIGHT_PIXELS,
                arcade.color.RED,
            )


class ChunkLoader:
    def __init__(self):
        # Queue for incoming and completed work
        self.queue_in = Queue(maxsize=-1)
        self.queue_out = Queue(maxsize=-1)

        # Run as daemon thread. This will terminate with the application.
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.thread.start()

    def run(self):
        while True:
            # Wait for a new chunk loading request
            chunk_id = self.queue_in.get(block=True)
            # Load the chunk here..
            chunk_timer = Timer("chunk_load")
            with gzip.open(config.DATA_DIR / f"pickle{pickle.format_version}_{chunk_id}.pickle") as f:
                chunk = HorizontalChunk(chunk_id * 16, chunk_id, pickle.load(f))
            print("Loaded chunk in", chunk_timer.stop())

            # Spread load over more time
            sp_timer = Timer("chunk_load")
            i = 0
            for _ in chunk.make_sprite_list():
                if i == 50:
                    time.sleep(0.001)
                    i = 0
                i += 1
            print("Make spritelist in", sp_timer.stop())

            self.queue_out.put(chunk)

            print(f"Loaded chunk {chunk_id} in {chunk_timer.stop()}")

    def get_loaded_chunks(self, max_results=1):
        chunks = deque()
        # Attempt to fetch max_results chunks from the queue
        for _ in range(max_results):
            try:
                chunk = self.queue_out.get(block=False)
                chunks.append(chunk)
            except Empty:
                break

        return chunks
