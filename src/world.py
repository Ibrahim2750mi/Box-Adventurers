import gzip
import pickle
from collections import deque
from math import atan, pi
import time
from typing import Optional, Tuple, Set
import threading
from queue import Empty, Queue

import arcade
from entities.player import Player, PlayerSpriteList
from block.block import Block
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
        self._player_list: PlayerSpriteList = PlayerSpriteList(self._player_sprite)

        # Initial physics engine with no chunks
        self._physics_engine: arcade.PhysicsEnginePlatformer = arcade.PhysicsEnginePlatformer(
            player_sprite=self._player_sprite,
            walls=[],
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
        self._requested_chunks: Set[int] = set()  # Keep track of requested chunks

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
        self._player_list.update_list()

    def create(self):
        """Create the initial world state"""
        self.setup_world()

    def process_new_chunks(self):
        # Get loaded chunks from threaded chunk loader
        self._chunk_loader.start()
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
            self._physics_engine.walls = [chunk.spritelist for chunk in self._active_chunks]

        return visible_loaded, changed

    def setup_world(self) -> None:
        config.DATA_DIR.mkdir(exist_ok=True)

        if not (config.DATA_DIR / f"pickle{pickle.format_version}_0.pickle").exists():
            print("World not generated. Generating ...")
            timer = Timer("world_gen")

            # Create empty chunks
            for n in range(-31, 31):
                self._whole_world[n] = HorizontalChunk(n * 16, n)

            world = gen_world(-496, 496, config.HEIGHT_MIN, config.HEIGHT_MIN + 320)
            for k, chunk_data in world.items():
                n = int(k[1] / 16)
                self._whole_world[n]['setter'] = chunk_data

            print(f"Generated world in {timer.stop()} seconds")

            print("Saving world")
            timer = Timer("world_save")
            for n, chunk in self._whole_world.items():
                with gzip.open(config.DATA_DIR / f"pickle{pickle.format_version}_{n}.pickle", "wb") as fd:
                    pickle.dump(chunk.data, fd)
                    chunk.make_sprite_list()

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

    def get_chunk_at_world_position(self, x, y) -> Optional[HorizontalChunk]:
        """Get a chunk at a wold position"""
        return self._whole_world.get((x + config.SPRITE_PIXEL_SIZE / 2) // 320)

    def get_block_at_world_position(self, x, y) -> Optional[Block]:
        """Get a block from a world position"""
        chunk = self.get_chunk_at_world_position(x, y)
        if not chunk:
            return None

        blocks = arcade.get_sprites_at_point(point=(x, y), sprite_list=chunk.spritelist)
        if blocks:
            return blocks[0]

        return None

    def place_block(self, x: int, y: int):
        actual_x = config.SPRITE_PIXEL_SIZE * round(x / config.SPRITE_PIXEL_SIZE)
        actual_y = config.SPRITE_PIXEL_SIZE * round(y / config.SPRITE_PIXEL_SIZE)
        block_id = self._player_sprite.inventory.get_selected_item_id_and_remove()
        if not block_id:
            return
        self._whole_world[((x + config.SPRITE_PIXEL_SIZE / 2) // 320)].add(actual_x, actual_y, block_id)

    def remove_block(self, block: Block):
        x = block.center_x
        self._whole_world[((x + config.SPRITE_PIXEL_SIZE / 2) // 320)].remove(block)

    @property
    def whole_world(self):
        return self._whole_world

    def dir_of_mouse_from_player(self, mouse_x, mouse_y):
        player = self._player_sprite
        div = pi / 8
        x = mouse_x - player.center_x
        y = mouse_y - player.eyes
        direction = ""
        if y > 0:
            if div > atan(x / y) >= 0 or -3*div > atan(x/y) >= -4*div:
                direction += "N"
            elif 3 * div > atan(x / y) >= div:
                direction += "NE"

            if direction:
                return direction
        if x > 0:
            if 4 * div > atan(x / y) >= 3 * div or 0 > atan(x / y) >= -div:
                direction += "E"
            elif -div > atan(x / y) >= -3 * div:
                direction += "SE"

            if direction:
                return direction
        if y < 0:
            if -3 * div > atan(x / y) >= -4 * div or div > atan(x / y) >= 0:
                direction += "S"
            elif 3 * div > atan(x / y) >= div:
                direction += "SW"

            if direction:
                return direction
        if x < 0:
            if 4 * div > atan(x / y) >= 3 * div or 0 > atan(x / y) >= -div:
                direction += "W"
            elif -div > atan(x / y) >= -3 * div:
                direction += "NW"

        return direction

    def block_break_check(self, block: Block, mouse_x: int, mouse_y: int) -> bool:
        if not self._player_sprite.distance_to_block(block) < config.PLAYER_BLOCK_REACH:
            return False
        reverse = {"S": "N", "N": "S", "SW": "NE", "NE": "SW", "E": "W", "W": "E", "SE": "NW", "NW": "SE"}
        direction = self.dir_of_mouse_from_player(mouse_x, mouse_y)
        block_neighbours = self.get_chunk_at_world_position(block.center_x, block.center_y)\
            .get_neighbouring_blocks(block)
        if block_neighbours[reverse[direction]]:
            return False
        return True


class ChunkLoader:
    def __init__(self):
        # Queue for incoming and completed work
        self.queue_in = Queue(maxsize=-1)
        self.queue_out = Queue(maxsize=-1)

        # Run as daemon thread. This will terminate with the application.
        self.thread = threading.Thread(target=self._run, daemon=True)

    def start(self):
        """Start the thread if not already started"""
        if not self.thread.is_alive():
            print("Starting chunk loader thread")
            self.thread.start()

    def _run(self):
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
