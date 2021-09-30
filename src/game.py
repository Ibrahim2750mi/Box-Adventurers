import math
from pathlib import Path
from typing import Tuple

import arcade
import arcade.gui
from arcade import MOUSE_BUTTON_LEFT, MOUSE_BUTTON_RIGHT, color

from block.block import Block
from misc.item import Item
from world import World
from misc.inventory import Inventory
import config

class Game(arcade.View):
    """Base game class"""

    def __init__(self) -> None:
        """Initializer"""
        super().__init__()

        self.bg_music: arcade.Sound = None
        self.break_cooldown = False
        self.place_cooldown = False
        self.hud_camera = arcade.Camera(*self.window.get_size())
        self.world = World(screen_size=self.window.get_size(), name="default")
        self.inventory = Inventory()
        self.inventory.setup_coords(self.window.get_size())

        # path = Path(__file__).parent.joinpath("../assets/music/main_game_tune.wav")
        # self.bg_music = arcade.Sound(path)
        # self.bg_music.play(loop=True)

    def setup(self):
        self.world.create()

    def on_draw(self) -> None:
        self.window.clear()
        self.world.draw()
        self.hud_camera.use()
        self.inventory.draw()

    def on_update(self, delta_time: float) -> None:
        """Movement and game logic."""
        self.world.update()
        self.inventory.update()

    def on_key_press(self, key: int, modifiers: int) -> None:
        """
        Called whenever the mouse moves.
        """
        self.world._player_sprite.on_key_press(key, modifiers, self.world._physics_engine.can_jump())

    def on_key_release(self, key: int, modifiers: int) -> None:
        """Called when the user presses a mouse button."""
        self.world._player_sprite.on_key_release(key, modifiers)

    def on_mouse_press(self, x: int, y: int, button: int, key_modifiers: int) -> None:
        # self.camera.center_camera_to_player(self.player_sprite)
        tmp_x = x - 600 + self.world._player_sprite.center_x
        tmp_y = y - 347 + self.world._player_sprite.center_y
        distance = math.sqrt((tmp_x - self.world._player_sprite.center_x) ** 2 + (tmp_y - self.world._player_sprite.center_y) ** 2)
        path = Path(__file__).parent.joinpath("../assets/sprites/mouse_point.png")
        block = arcade.get_closest_sprite(arcade.Sprite(
            str(path), image_width=2, image_height=2, center_x=tmp_x, center_y=tmp_y), self.world.get_colloidal_blocks())

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
        self.inventory.add(Item(True, block.block_id))
        block.break_(128)

        # Remove block from world
        for sprite_list in self.world._loaded_chunks_sprites:
            if block in sprite_list:
                sprite_list.remove(block)
        self.break_cooldown = True


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
        self.text = "Loading World"

    def on_show(self):
        arcade.set_background_color(color.BLACK)

    def on_draw(self):
        arcade.start_render()
        if not self.first_time:
            self.game_view.setup()
            self.window.show_view(self.game_view)
        else:
            self.first_time = False
        arcade.draw_text(self.text, config.SCREEN_WIDTH / 2 - 50, config.SCREEN_HEIGHT / 2, color=color.WHITE)


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

        path = Path(__file__).parent.joinpath("../assets/images/")
        self.background = arcade.load_texture(f"{str(path)}/ezgif-frame-{partial_frame}.png")
        arcade.draw_texture_rectangle(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2, config.SCREEN_WIDTH, config.SCREEN_HEIGHT,
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
    window = arcade.Window(config.SCREEN_WIDTH, config.SCREEN_HEIGHT, config.SCREEN_TITLE)
    window.show_view(StartView())
    arcade.run()


if __name__ == "__main__":
    main()
