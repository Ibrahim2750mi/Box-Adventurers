import gc
from collections import deque
from functools import cache
from itertools import islice
from pathlib import Path

import arcade
import arcade.gui
import numpy as np
from arcade import color

from config import (GRAVITY, JUMP_SPEED, MOVEMENT_SPEED, PLAYER_SCALING,
                    SCREEN_HEIGHT, SCREEN_TITLE, SCREEN_WIDTH,
                    VISIBLE_RANGE_MAX, VISIBLE_RANGE_MIN,)
from entities.player import Player
from misc.camera import CustomCamera
from misc.chunk import HorizontalChunk
from misc.terrain import gen_world


class Game(arcade.View):
    """Base game class"""

    def __init__(self) -> None:
        """Initializer"""
        super().__init__()

        # Initialising arguments
        self.whole_world: deque = None
        self.physics_engine: arcade.PhysicsEnginePlatformer = None
        self.block_list: arcade.SpriteList = None
        self.background_list: arcade.SpriteList = None
        self.player_list: arcade.SpriteList = None
        self.player_sprite: Player = None
        self.camera: CustomCamera = None
        self.hud_camera: arcade.Camera = None
        self.loaded_chunks: dict = None
        self.bg_music: arcade.Sound = None

    @cache
    def __add_blocks(self, h_chunk: HorizontalChunk):
        for block in h_chunk:
            try:
                if block.block_id > 129:
                    self.block_list.append(block)
                else:
                    self.background_list.append(block)
            except ValueError:
                pass

    @cache
    def __add_chunk(self, h_chunk: HorizontalChunk, insert_i: bool, block_list_: list, background_list_: list):

        temp_block_list = arcade.SpriteList()
        if insert_i:
            for block in h_chunk:
                if block.block_id > 129:
                    temp_block_list.append(block)
        try:
            temp_block_list.extend(block_list_)
        except ValueError:
            for block in self.block_list:
                try:
                    temp_block_list.append(block)
                except ValueError:
                    pass
        self.block_list = temp_block_list

        temp_block_bg_list = arcade.SpriteList()
        if insert_i:
            for block in h_chunk:
                if block.block_id <= 129:
                    temp_block_bg_list.append(block)
        try:
            temp_block_bg_list.extend(background_list_)
        except ValueError:
            for block in self.background_list:
                try:
                    temp_block_bg_list.append(block)
                except ValueError:
                    pass
        self.background_list = temp_block_bg_list
        if not insert_i:
            self.__add_blocks(h_chunk)
        self.physics_engine = arcade.PhysicsEnginePlatformer(self.player_sprite, [self.block_list], GRAVITY)

    def optimise(self):
        if (self.player_sprite.chunk + 1 not in self.loaded_chunks.keys(),
            self.player_sprite.last_faced_dir == "right") == (True, True) \
                or (self.player_sprite.chunk - 1 not in self.loaded_chunks.keys(),
                    self.player_sprite.last_faced_dir == "left") == (True, True):

            block_list_ = None
            background_list_ = None
            insert_i = None
            chunk_index = None

            if self.player_sprite.chunk + 1 not in self.loaded_chunks.keys() and \
                    self.player_sprite.last_faced_dir == "right":
                key = min(self.loaded_chunks.keys())
                blocks = self.loaded_chunks[key][0]
                blocks_bg = self.loaded_chunks[key][1]
                del (self.loaded_chunks[key])
                insert_i = False
                block_list_ = islice(self.block_list, blocks - 1, len(self.block_list) - 1)
                background_list_ = islice(self.background_list, blocks_bg - 1, len(self.background_list) - 1)
                chunk_index = self.player_sprite.chunk + 1

            elif self.player_sprite.chunk - 1 not in self.loaded_chunks.keys() and \
                    self.player_sprite.last_faced_dir == "left":
                key = max(self.loaded_chunks.keys())
                blocks = self.loaded_chunks[key][0]
                blocks_bg = self.loaded_chunks[key][1]
                del (self.loaded_chunks[key])
                insert_i = True
                block_list_ = islice(self.block_list, len(self.block_list) - blocks - 1)
                background_list_ = islice(self.background_list, len(self.background_list) - blocks_bg - 1)
                chunk_index = self.player_sprite.chunk - 1

            try:
                h_chunk = self.whole_world[chunk_index]
            except KeyError:
                pass
            else:
                h_chunk: HorizontalChunk
                self.loaded_chunks[chunk_index] = (h_chunk.other_block_count, h_chunk.bg_block_count)
                self.__add_chunk(h_chunk, insert_i, block_list_, background_list_)

    def setup(self) -> None:
        """Set up the game and initialize the variables."""

        self.setup_world()

        self.camera = CustomCamera(SCREEN_WIDTH, SCREEN_HEIGHT, self.window)
        self.hud_camera = arcade.Camera(SCREEN_WIDTH, SCREEN_HEIGHT)

        self.setup_player()

        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player_sprite,
            [self.block_list],
            gravity_constant=GRAVITY)

        arcade.set_background_color(color.AMAZON)

        path = Path(__file__).parent.joinpath("../assets/music/main_game_tune.wav")
        self.bg_music = arcade.Sound(path)
        self.bg_music.play(loop=True)

        self.view_left: int = 0
        self.view_bottom: int = 0

        self.game_over: bool = False

    def setup_world(self):
        self.block_list = arcade.SpriteList()
        self.background_list = arcade.SpriteList()

        self.whole_world = deque()
        self.loaded_chunks = {}
        path = Path(__file__).parent.joinpath("misc/world.npy")
        try:
            with open(str(path), "rb") as f:
                self.whole_world = np.load(f, allow_pickle=True)
        except FileNotFoundError:
            for n in range(-31, 31):
                self.whole_world.append(HorizontalChunk(n * 16))

            world = gen_world(-496, 496, 0, 320)
            for k, chunk in world.items():
                self.whole_world[int(k[1] / 16) + 10][0] = chunk

            with open(str(path), "wb") as f:
                np.save(f, self.whole_world, allow_pickle=True)

        for visible_index in range(int(VISIBLE_RANGE_MIN / 16) + 31, int(VISIBLE_RANGE_MAX / 16) + 31):
            h_chunk = self.whole_world[visible_index]
            h_chunk: HorizontalChunk
            self.loaded_chunks[visible_index] = (h_chunk.other_block_count, h_chunk.bg_block_count)
            self.__add_blocks(h_chunk)

    def setup_player(self):
        self.player_list = arcade.SpriteList()

        # Set up the player
        self.player_sprite = Player("player",
                                    PLAYER_SCALING, 0, 3112, SCREEN_WIDTH,
                                    SCREEN_HEIGHT, MOVEMENT_SPEED, JUMP_SPEED, False)
        self.player_list.append(self.player_sprite)
        self.player_sprite.inventory.setup_coords(self.camera.position)

    def on_draw(self) -> None:
        """
        Render the screen.
        """
        # This command has to happen before we start drawing
        arcade.start_render()

        self.camera.use()
        self.background_list.draw()
        self.block_list.draw()
        self.player_list.draw()

        self.hud_camera.use()
        self.player_sprite.inventory.draw()

    def on_key_press(self, key: int, modifiers: int) -> None:
        """
        Called whenever the mouse moves.
        """
        self.player_sprite.on_key_press(key, modifiers, self.physics_engine.can_jump())

    def on_key_release(self, key: int, modifiers: int) -> None:
        """Called when the user presses a mouse button."""
        self.player_sprite.on_key_release(key, modifiers)

    def on_update(self, delta_time: float) -> None:
        """Movement and game logic."""

        self.physics_engine.update()
        self.player_sprite.inventory.update()
        self.camera.center_camera_to_player(self.player_sprite)
        # print(self.player_sprite.center_y, self.player_sprite.center_x)
        self.optimise()


# --- Method 1 for handling click events,
# Create a child class.
class QuitButton(arcade.gui.UIFlatButton):
    def on_click(self, event: arcade.gui.UIOnClickEvent):
        arcade.exit()


class StartView(arcade.View):
    def __init__(self):
        super().__init__()

        # --- Required for all code that uses UI element,
        # a UIManager to handle the UI.
        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        # Set background color
        # arcade.set_background_color(arcade.color.DARK_BLUE_GRAY)
        self.background = None
        self.frameNum = 22
        self.maxFrames = 285  # 390

        print(gc.isenabled())

        # Create a vertical BoxGroup to align buttons
        self.v_box = arcade.gui.UIBoxLayout()

        # Create the buttons
        start_button = arcade.gui.UIFlatButton(text="Start Game", width=200, style={
                                               "bg_color": arcade.get_four_byte_color((0, 0, 60, 200))})
        self.v_box.add(start_button.with_space_around(bottom=20))

        settings_button = arcade.gui.UIFlatButton(text="Settings", width=200, style={
                                                  "bg_color": arcade.get_four_byte_color((0, 0, 60, 200))})
        self.v_box.add(settings_button.with_space_around(bottom=20))

        # Again, method 1. Use a child class to handle events.
        quit_button = QuitButton(text="Quit", width=200, style={
                                 "bg_color": arcade.get_four_byte_color((0, 0, 60, 200))})
        self.v_box.add(quit_button)

        # --- Method 2 for handling click events,
        # assign self.on_click_start as callback
        start_button.on_click = self.on_click_start

        # --- Method 3 for handling click events,
        # use a decorator to handle on_click events
        @settings_button.event("on_click")
        def on_click_settings(event):
            print("Settings:", event)

        # Create a widget to hold the v_box widget, that will center the buttons
        self.manager.add(
            arcade.gui.UIAnchorWidget(
                anchor_x="center_x",
                anchor_y="center_y",
                child=self.v_box)
        )

    def on_click_start(self, event):
        game_view = Game()
        game_view.setup()
        self.window.show_view(game_view)

    def on_draw(self):
        arcade.start_render()

        # background gif
        # showing the background image
        self.background = arcade.load_texture(f"./assets/images/out{self.frameNum}.png")
        arcade.draw_texture_rectangle(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, SCREEN_WIDTH, SCREEN_HEIGHT,
                                      self.background)
        self.background = None
        # gc.collect()
        # changing it to the next frame
        self.frameNum += 1
        if self.frameNum > self.maxFrames:
            self.frameNum = 22

        self.manager.draw()


def main():
    """ Main method """
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.show_view(StartView())
    arcade.run()


if __name__ == "__main__":
    main()
