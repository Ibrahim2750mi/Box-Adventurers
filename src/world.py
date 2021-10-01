import gzip
import pickle
from pathlib import Path
from collections import deque
from typing import Tuple

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

        # Player
        self._player_list: arcade.SpriteList = arcade.SpriteList()
        self._player_sprite = Player(
            "player",
            scale=config.PLAYER_SCALING,
            center_x=0,
            center_y=3112,
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

        # Chunks
        self._whole_world: deque = deque()
        self._loaded_chunks: list = []
        self._loaded_chunks_sprites: deque = deque()

        self.camera = CustomCamera(*self._screen_size)
    
    @property
    def player(self) -> Player:
        return self._player_sprite

    def draw(self):
        self.camera.use()

        for sprite_list in self._loaded_chunks_sprites:
            sprite_list.draw(pixelated=True)

        self._player_list.draw(pixelated=True)

    def create(self):
        """Create the initial world state"""
        self.setup_world()
        arcade.set_background_color(arcade.color.AMAZON)

        for visible_index in range(int(config.VISIBLE_RANGE_MIN / 16) + 31, int(config.VISIBLE_RANGE_MAX / 16) + 31):
            h_chunk = self._whole_world[visible_index]
            h_chunk: arcade.SpriteList
            self._loaded_chunks.append(visible_index)
            self._loaded_chunks_sprites.append(h_chunk)

        self._physics_engine.platforms = [self.get_colloidal_blocks()]

    def update(self):
        """Called every frame to update the world state"""
        self._physics_engine.update()
        self.camera.center_camera_to_player(self._player_sprite)
        self._optimize()

    def _optimize(self):
        """Keep this around for now"""
        if (self._player_sprite.chunk + 1 not in self._loaded_chunks,
            self._player_sprite.last_faced_dir == "right") == (True, True) or (
                self._player_sprite.chunk - 1 not in self._loaded_chunks,
                self._player_sprite.last_faced_dir == "left") == (True, True):
            insert_i = None
            chunk_index = None
            key = None

            if self._player_sprite.chunk + 1 not in self._loaded_chunks and \
                    self._player_sprite.last_faced_dir == "right":
                key = min(self._loaded_chunks)
                insert_i = False
                chunk_index = self._player_sprite.chunk + 1

            elif self._player_sprite.chunk - 1 not in self._loaded_chunks and \
                    self._player_sprite.last_faced_dir == "left":
                key = max(self._loaded_chunks)
                insert_i = True
                chunk_index = self._player_sprite.chunk - 1

            try:
                h_chunk_ = self._whole_world[chunk_index]
                h_chunk_: arcade.SpriteList
            except KeyError:
                pass
            else:
                print(self._loaded_chunks, h_chunk_)
                h_chunk_: HorizontalChunk
                self._loaded_chunks.append(chunk_index)
                if insert_i:
                    self._loaded_chunks_sprites.appendleft(h_chunk_)
                else:
                    self._loaded_chunks_sprites.append(h_chunk_)

                self._loaded_chunks.pop(self._loaded_chunks.index(key))
                self._physics_engine.platforms = [self.get_colloidal_blocks()]

    def get_colloidal_blocks(self):
        colloidable_blocks = arcade.SpriteList()

        for sprite_list in self._loaded_chunks_sprites:
            for block in sprite_list:
                if block.block_id > 129:
                    try:
                        colloidable_blocks.append(block)
                    except ValueError:
                        pass
        return colloidable_blocks

    def setup_world(self) -> None:
        config.DATA_DIR.mkdir(exist_ok=True)
        try:
            print("Attempting to load existing chunks")
            timer = Timer("load_world")

            for n in range(-31, 31):
                name = n + 31
                with gzip.open(config.DATA_DIR / f"pickle{pickle.format_version}_{name}.pickle") as f:
                    chunk = pickle.load(f)
                    h_chunk: HorizontalChunk = HorizontalChunk(n * 16, chunk)
                    h_chunk.make_sprite_list(h_chunk.iterable)
                    self._whole_world.append(h_chunk.sprites)
            print(f"Loaded chunks in {timer.stop()} seconds")
        except FileNotFoundError:
            print("Failed to load chunks. Generating world...")
            timer = Timer("world_gen")
            for n in range(-31, 31):
                self._whole_world.append(HorizontalChunk(n * 16))

            world = gen_world(-496, 496, 0, 320)
            for k, chunk in world.items():
                n = int(k[1] / 16) + 31
                self._whole_world[n]['setter'] = chunk

            print(f"Generated world in {timer.stop()} seconds")
            print("Saving world")
            timer = Timer("world_save")
            for n, chunk in enumerate(self._whole_world):
                with gzip.open(config.DATA_DIR / f"pickle{pickle.format_version}_{n}.pickle", "wb") as f:
                    pickle.dump(chunk.iterable, f)
                chunk.make_sprite_list(chunk.iterable)
                self._whole_world[n] = chunk.sprites

            print(f"Saved wold in {timer.stop()} seconds")


