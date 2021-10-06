import gzip
import pickle
from collections import deque
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
        self._update_visible_chunks()
        if self._player_sprite.center_y < -100:
            self._player_sprite.set_position(self._player_default_x, self._player_default_y)
        self._physics_engine.update()

    def create(self):
        """Create the initial world state"""
        yield from self.setup_world()

    def _update_visible_chunks(self):
        """Detect and update visible chunks"""
        changed = False

        # If we have no active chunks, add the chunk the player is located in
        if not self._active_chunks:
            chunk = self._whole_world.get(self._player_sprite.chunk)
            # If the player is not located in a chunk we have nothing to do
            if not chunk:
                return
            self._active_chunks.append(chunk)
            changed = True

        player_x = self._player_sprite.center_x
        view_dist = config.VISIBLE_RANGE_MAX * 20

        # Fill visible chunks from left side
        while self._active_chunks[0].is_visible(player_x, view_dist):
            index = self._active_chunks[0].index - 1
            new_chunk = self._whole_world.get(index)
            if not new_chunk:
                self._chunk_loader(index)
                new_chunk = self._whole_world[index]
            elif not new_chunk.is_visible(player_x, view_dist):
                break

            self._active_chunks.appendleft(new_chunk)
            changed = True

        # Fill visible chunks from right side
        while self._active_chunks[-1].is_visible(player_x, view_dist):
            index = self._active_chunks[-1].index + 1
            new_chunk = self._whole_world.get(index)
            if not new_chunk:
                self._chunk_loader(index)
                new_chunk = self._whole_world[index]
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

    def setup_world(self) -> None:
        config.DATA_DIR.mkdir(exist_ok=True)
        try:
            print("Attempting to load existing chunks")
            load_timer = Timer("load_world")

            for n in range(int(config.VISIBLE_RANGE_MIN/16), int(config.VISIBLE_RANGE_MAX/16) + 1):
                chunk_timer = self._chunk_loader(n)

                yield  # Report back to loadingscreen

                print(f"Loaded chunk {n} in {chunk_timer.stop()} seconds")

            print(f"Loaded chunks in {load_timer.stop()} seconds")
        except FileNotFoundError:
            print("Failed to load chunks. Generating world...")
            timer = Timer("world_gen")

            # Create empty chunks
            for n in range(-31, 31):
                self._whole_world[n] = HorizontalChunk(n * 16, n)

            yield  # Report back to loadingscreen

            world = gen_world(-496, 496, 0, 320)
            for k, chunk_data in world.items():
                n = int(k[1] / 16)
                self._whole_world[n]['setter'] = chunk_data

            yield  # Report back to loadingscreen

            print(f"Generated world in {timer.stop()} seconds")

            print("Saving world")
            timer = Timer("world_save")
            for n, chunk in self._whole_world.items():
                with gzip.open(config.DATA_DIR / f"pickle{pickle.format_version}_{n}.pickle", "wb") as f:
                    pickle.dump(chunk.data, f)
                    chunk.make_sprite_list()
                yield  # Report back to loadingscreen

            print(f"Saved wold in {timer.stop()} seconds")

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

    def _chunk_loader(self, n):
        chunk_timer = Timer("chunk_load")
        with gzip.open(config.DATA_DIR / f"pickle{pickle.format_version}_{n}.pickle") as f:
            chunk = HorizontalChunk(n * 16, n, pickle.load(f))
            chunk.make_sprite_list()
            self._whole_world[n] = chunk
        return chunk_timer


class ChunkLoader:
    def __init__(self, parent):
        self.parent = parent

        # Queue for incoming and completed work
        self.queue_in = Queue(maxsize=-1)
        self.queue_out = Queue(maxsize=-1)

        # Run as daemon thread. This will terminate with the application.
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.thread.start()

    def run(self):
        while True:
            # Wait for a new chunk loading request
            item = self.queue_in.get(block=True)
            print("Chunkloader: Got chunk to load:", item)
            # Load the chunk here..
            # Send the chunk back
            self.queue_out.put(f"Chunk {item}")

    def get_loaded_chunks(self):
        chunks = deque()
        while True:
            try:
                chunks.append(self.queue_out.get(block=False))
            except Empty:
                break

        return chunks
