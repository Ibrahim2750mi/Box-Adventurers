import math
from typing import Tuple

import arcade
import arcade.gui
from arcade import MOUSE_BUTTON_LEFT, MOUSE_BUTTON_RIGHT, color

from block.block import Block
from misc.item import Item
from world import World
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

        # TODO: Is this necessary?
        self.world.player.inventory.setup_coords((0, 0))

        self.bg_music = None
        if config.MUSIC:
            self.bg_music = arcade.Sound(config.ASSET_DIR / "music" / "main_game_tune.wav")
            self.bg_music.play(loop=True)

    def setup(self):
        yield from self.world.create()

    def on_draw(self) -> None:
        self.window.clear()

        self.world.draw()
        arcade.draw_rectangle_outline(self.bx, self.by, 20, 20, color.RED, 1)

        self.hud_camera.use()
        self.world.player.inventory.draw()


    def on_update(self, delta_time: float) -> None:
        """Movement and game logic."""
        self.world.update()
        self.world.player.inventory.update()

    def on_key_press(self, key: int, modifiers: int) -> None:
        """Called when keyboard is pressed"""
        self.world.player.on_key_press(key, modifiers)

    def on_key_release(self, key: int, modifiers: int) -> None:
        """Called when keyboard is released"""
        self.world.player.on_key_release(key, modifiers)

    def on_mouse_press(self, x: int, y: int, button: int, key_modifiers: int) -> None:
        player = self.world.player
        tmp_x = x - 600 + player.x
        tmp_y = y - 347 + player.y
        # distance = math.sqrt((tmp_x - player.x) ** 2 + (tmp_y - player.y) ** 2)

        # TODO: This part needs work
        chunk = self.world._whole_world.get(self.world._player_sprite.chunk)

        print(tmp_x, tmp_y, self.world.player.center_x, self.world.player.center_y)
        self.bx = tmp_x
        self.by = tmp_y
        print(chunk.index)

        if not chunk:
            return
        block, block_dist = arcade.get_closest_sprite(
            arcade.Sprite(
                config.ASSET_DIR / "sprites" / "mouse_point.png",
                image_width=2,
                image_height=2,
                center_x=tmp_x,
                center_y=tmp_y
            ),
            chunk.spritelist,
        )

        if button == MOUSE_BUTTON_LEFT and not self.break_cooldown:
            # if block is within range and is not sky then break it
            if block_dist <= 100:
                self.world.player.inventory.add(Item(True, block.block_id))
                block.remove_from_sprite_lists()

        # elif button == MOUSE_BUTTON_RIGHT and not self.place_cooldown:
        #     distance <= 100 and block[0].block_id <= 129 and self.place_block)

    def on_mouse_release(self, x: float, y: float, button: int, modifiers: int):
        """ Called when the user presses a mouse button. """
        if button == MOUSE_BUTTON_LEFT:
            self.break_cooldown = False
        if button == MOUSE_BUTTON_RIGHT:
            self.place_cooldown = False


# --- Method 1 for handling click events,
# Create a child class.
class QuitButton(arcade.gui.UIFlatButton):
    def on_click(self, event: arcade.gui.UIOnClickEvent):
        arcade.exit()


class LoadingScreen(arcade.View):
    def __init__(self):
        super().__init__()
        self.frames = 0
        self.text = "Loading World"
        self.game_view = None
        self.game_loader_generator = None
        self.angle = 0
        self.frame = 0

    def on_show(self):
        arcade.set_background_color(color.BLACK)

    def on_draw(self):
        self.window.clear()
        # On frame 0 we render the loading screen so this happens instantly
        # On frame 1 we crate the game object and the loading iterator
        # From frame 2 we invoke loading loading steps until done 
        if self.frame == 1:
            self.game_view = Game()
            self.game_loader_generator = self.game_view.setup()
        elif self.frame > 1:
            try:
                # Trigger next loading step
                next(self.game_loader_generator)
                self.angle += 10
            except StopIteration:
                # Loading is done. Show the game view (Will happen in next frame)
                self.window.show_view(self.game_view)

        arcade.draw_text(
            self.text,
            self.window.width / 2,
            self.window.height / 2 + 30,
            color=color.WHITE,
            anchor_x="center",
        )
        arcade.draw_rectangle_filled(
            self.window.width / 2,  # x
            self.window.height / 2 - 30,  # y
            50,
            50,
            arcade.color.WHITE,
            self.angle,
        )
        self.frame += 1


class StartView(arcade.View):
    def __init__(self):
        super().__init__()

        # --- Required for all code that uses UI element,
        # a UIManager to handle the UI.
        self.manager = arcade.gui.UIManager()
        # Enable UI events
        self.manager.enable()

        # Set background color
        # arcade.set_background_color(arcade.color.DARK_BLUE_GRAY)
        self.background = None
        self.frameNum = 1
        self.maxFrames = 1  # 155

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
        self.window.show_view(LoadingScreen())

    def on_draw(self):
        self.window.clear()

        # background gif
        # showing the background image
        if len(str(self.frameNum)) == 1:
            partial_frame = "00" + str(self.frameNum)
        elif len(str(self.frameNum)) == 2:
            partial_frame = "0" + str(self.frameNum)
        else:
            partial_frame = str(self.frameNum)

        self.background = arcade.load_texture(config.ASSET_DIR / "images" / f"ezgif-frame-{partial_frame}.png")
        arcade.draw_texture_rectangle(
            config.SCREEN_WIDTH // 2,
            config.SCREEN_HEIGHT // 2,
            config.SCREEN_WIDTH,
            config.SCREEN_HEIGHT,
            self.background,
        )
        # changing it to the next frame
        self.frameNum += 1
        if self.frameNum > self.maxFrames:
            self.frameNum = 1

        self.manager.draw()

    def on_view_hide(self):
        """Disable the UI events"""
        self.manager.disable()


def main():
    """ Main method """
    window = arcade.Window(config.SCREEN_WIDTH, config.SCREEN_HEIGHT, config.SCREEN_TITLE)
    window.show_view(StartView())
    arcade.run()


if __name__ == "__main__":
    main()
