import math
from collections import deque
import pickle
from pathlib import Path
from typing import Tuple

import arcade
import arcade.gui
from arcade import MOUSE_BUTTON_LEFT, MOUSE_BUTTON_RIGHT, color

from block.block import Block
from config import (GRAVITY, JUMP_SPEED, MOVEMENT_SPEED, PLAYER_SCALING,
                    SCREEN_HEIGHT, SCREEN_TITLE, SCREEN_WIDTH,
                    VISIBLE_RANGE_MAX, VISIBLE_RANGE_MIN, )
from entities.player import Player
from misc.camera import CustomCamera
from misc.chunk import HorizontalChunk
from misc.item import Item
from misc.terrain import gen_world


class Game(arcade.View):
    """Base game class"""

    def __init__(self) -> None:
        """Initializer"""
        super().__init__()

        # Initialising arguments
        self.whole_world: deque = None

        self.physics_engine: arcade.PhysicsEnginePlatformer = None

        self.player_list: arcade.SpriteList = None
        self.player_sprite: Player = None

        self.camera: CustomCamera = None
        self.hud_camera: arcade.Camera = None

        self.loaded_chunks: list = None
        self.loaded_chunks_sprites: deque = None

        self.bg_music: arcade.Sound = None
        self.broke_blocks: dict = None

        self.break_cooldown = False
        self.place_cooldown = False

    def get_colloidal_blocks(self):
        colloidable_blocks = arcade.SpriteList()

        for sprite_list_ in self.loaded_chunks_sprites:
            for block in sprite_list_:
                if block.block_id > 129:
                    colloidable_blocks.append(block)
        return colloidable_blocks

    def optimise(self):
        if (self.player_sprite.chunk + 1 not in self.loaded_chunks,
            self.player_sprite.last_faced_dir == "right",) == (True, True) and (
                self.player_sprite.chunk - 1 not in self.loaded_chunks,
                self.player_sprite.last_faced_dir == "left",) == (True, True,):
            insert_i = None
            chunk_index = None
            key = None

            if self.player_sprite.chunk + 1 not in self.loaded_chunks and \
                    self.player_sprite.last_faced_dir == "right":
                key = min(self.loaded_chunks)
                insert_i = False
                chunk_index = self.player_sprite.chunk + 1

            elif self.player_sprite.chunk - 1 not in self.loaded_chunks and \
                    self.player_sprite.last_faced_dir == "left":
                key = max(self.loaded_chunks)
                insert_i = True
                chunk_index = self.player_sprite.chunk - 1

            try:
                h_chunk_ = self.whole_world[chunk_index]
                h_chunk_: arcade.SpriteList
            except KeyError:
                pass
            else:
                h_chunk_: HorizontalChunk
                self.loaded_chunks.append(chunk_index)
                if insert_i:
                    self.loaded_chunks_sprites.appendleft(h_chunk_)
                else:
                    self.loaded_chunks_sprites.append(h_chunk_)

                self.loaded_chunks.pop(self.loaded_chunks.index(key))
                self.physics_engine = arcade.PhysicsEnginePlatformer(self.player_sprite,
                                                                     self.get_colloidal_blocks(), GRAVITY)

    def setup(self) -> None:
        """Set up the game and initialize the variables."""

        self.setup_world()

        self.camera = CustomCamera(SCREEN_WIDTH, SCREEN_HEIGHT, self.window)
        self.hud_camera = arcade.Camera(SCREEN_WIDTH, SCREEN_HEIGHT)

        self.setup_player()

        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player_sprite,
            self.get_colloidal_blocks(),
            gravity_constant=GRAVITY)

        arcade.set_background_color(color.AMAZON)

        path = Path(__file__).parent.joinpath("../assets/music/main_game_tune.wav")
        self.bg_music = arcade.Sound(path)
        self.bg_music.play(loop=True)

    def setup_world(self) -> None:

        self.loaded_chunks = []
        self.loaded_chunks_sprites = deque()

        path = Path(__file__).parent.joinpath("../data")
        try:
            for n in range(-31, 31):
                with open(f"{str(path)}/pickle{pickle.format_version}_{n}.pickle", "rb") as f:
                    chunk = pickle.load(f)
                    h_chunk: HorizontalChunk = HorizontalChunk(n * 16, chunk)
                    h_chunk.make_sprite_list(h_chunk.iterable)
                    self.whole_world.append(h_chunk.sprites)

        except FileNotFoundError:
            self.whole_world = deque()
            for n in range(-31, 31):
                self.whole_world.append(HorizontalChunk(n * 16))

            world = gen_world(-496, 496, 0, 320)
            for k, chunk in world.items():
                n = int(k[1] / 16) + 31
                self.whole_world[n]['setter'] = chunk

            for n, chunk in enumerate(self.whole_world):
                with open(f"{str(path)}/pickle{pickle.format_version}_{n}.pickle", "wb") as f:
                    pickle.dump(chunk.iterable, f)
                chunk.make_sprite_list(chunk.iterable)
                self.whole_world[n] = chunk.sprites

        for visible_index in range(int(VISIBLE_RANGE_MIN / 16) + 31, int(VISIBLE_RANGE_MAX / 16) + 31):
            h_chunk = self.whole_world[visible_index]
            h_chunk: arcade.SpriteList
            self.loaded_chunks.append(visible_index)
            self.loaded_chunks_sprites.append(h_chunk)

    def setup_player(self) -> None:
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
        self.player_list.draw(pixelated=True)

        for sprite_list in self.loaded_chunks_sprites:
            sprite_list.draw(pixelated=True)

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

    def on_mouse_press(self, x: int, y: int, button: int, key_modifiers: int) -> None:
        self.camera.center_camera_to_player(self.player_sprite)
        tmp_x = x - 600 + self.player_sprite.center_x
        tmp_y = y - 347 + self.player_sprite.center_y
        distance = math.sqrt((tmp_x - self.player_sprite.center_x) ** 2 + (tmp_y - self.player_sprite.center_y) ** 2)
        path = Path(__file__).parent.joinpath("../assets/sprites/mouse_point.png")
        block = arcade.get_closest_sprite(arcade.Sprite(
            str(path), image_width=2, image_height=2, center_x=tmp_x, center_y=tmp_y), self.get_colloidal_blocks())

        if button == MOUSE_BUTTON_LEFT and not self.break_cooldown:
            # if block is within range and is not sky then break it
            block: Tuple[Block, float]
            distance <= 100 and block[0].block_id > 129 and self.break_block(block[0])

        # elif button == MOUSE_BUTTON_RIGHT and not self.place_cooldown:
        #     distance <= 100 and block[0].block_id <= 129 and self.place_block)

    def on_mouse_release(self, x: float, y: float, button: int, modifiers: int):
        """ Called when the user presses a mouse button. """
        if button == MOUSE_BUTTON_LEFT:
            self.break_cooldown = False
        if button == MOUSE_BUTTON_RIGHT:
            self.place_cooldown = False

    def break_block(self, block: Block):
        self.player_sprite.inventory.add(Item(True, block.block_id))
        block.break_(128)
        for sprite_list_ in self.loaded_chunks_sprites:
            if block in sprite_list_:
                sprite_list_.remove(block)
        self.break_cooldown = True

    # def place_block(self, block: Block):
    #     self.player_sprite.inventory.remove(Item(True, block))
    #     block.place(block.id)

    def on_update(self, delta_time: float) -> None:
        """Movement and game logic."""
        self.physics_engine.update()
        self.player_sprite.inventory.update()
        self.camera.center_camera_to_player(self.player_sprite)
        self.optimise()


# --- Method 1 for handling click events,
# Create a child class.
class QuitButton(arcade.gui.UIFlatButton):
    def on_click(self, event: arcade.gui.UIOnClickEvent):
        arcade.exit()


class LoadingScreen(arcade.View):
    def __init__(self, game_view):
        super().__init__()
        self.first_time = True
        self.game_view = game_view

    def on_show(self):
        arcade.set_background_color(color.BLACK)

    def on_draw(self):
        arcade.start_render()
        if not self.first_time:
            self.game_view.setup()
            self.window.show_view(self.game_view)
        else:
            self.first_time = False
        arcade.draw_text("Loading World...", SCREEN_WIDTH / 2 - 50, SCREEN_HEIGHT / 2, color=color.WHITE)


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
        self.frameNum = 1
        self.maxFrames = 155  # 390

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
        loading_screen = LoadingScreen(game_view)
        self.window.show_view(loading_screen)

    def on_draw(self):
        arcade.start_render()

        # background gif
        # showing the background image
        if len(str(self.frameNum)) == 1:
            partial_frame = "00" + str(self.frameNum)
        elif len(str(self.frameNum)) == 2:
            partial_frame = "0" + str(self.frameNum)
        else:
            partial_frame = str(self.frameNum)

        self.background = arcade.load_texture(f"../assets/images/ezgif-frame-{partial_frame}.png")
        arcade.draw_texture_rectangle(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, SCREEN_WIDTH, SCREEN_HEIGHT,
                                      self.background)
        self.background = None
        # gc.collect()
        # changing it to the next frame
        self.frameNum += 1
        if self.frameNum > self.maxFrames:
            self.frameNum = 1

        self.manager.draw()

    def on_view_hide(self):
        self.manager.disable()


def main():
    """ Main method """
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.show_view(StartView())
    arcade.run()


if __name__ == "__main__":
    main()
