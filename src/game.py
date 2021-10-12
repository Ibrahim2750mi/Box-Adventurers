from typing import Optional, Tuple

import arcade
import arcade.gui
from arcade import MOUSE_BUTTON_LEFT, MOUSE_BUTTON_RIGHT, color

from misc.item import Item
from world import World
import config


class Game(arcade.View):
    """Base game class"""

    def __init__(self) -> None:
        """Initializer"""
        super().__init__()

        self.bg_music: Optional[arcade.Sound] = None
        self.break_cooldown = False
        self.place_cooldown = False
        self.hud_camera = arcade.Camera(*self.window.get_size())
        self.world = World(screen_size=self.window.get_size(), name="default")

        # Block selection position
        self.bx = None
        self.by = None
        self.b_color = color.RED

        # TODO: Is this necessary?
        self.world.player.inventory.setup_coords((0, 0))

        if config.MUSIC:
            self.bg_music = arcade.Sound(
                config.ASSET_DIR / "music" / "main_game_tune.wav"
            )
            self.bg_music.play(loop=True)

    def setup(self):
        self.world.create()

    def on_draw(self) -> None:
        self.window.clear()

        self.world.draw()

        # Draw the block selection
        if self.bx is not None and self.by is not None:
            arcade.draw_rectangle_outline(self.bx, self.by, 20, 20, self.b_color, 1)

        self.hud_camera.use()
        self.world.player.inventory.smart_draw()

    def on_update(self, delta_time: float) -> None:
        """Movement and game logic."""
        # print(delta_time)
        self.world.update()
        self.world.player.inventory.update()
        # We created the window with gc_mode="context_gc" and must
        # manually garbage collect OpenGL resources (if any)
        num_deleted = self.window.ctx.gc()
        # Notify us when resources are deleted
        if num_deleted:
            print(f"Arcade garbage collector deleted {num_deleted} OpenGL resources")

    def on_key_press(self, key: int, modifiers: int) -> None:
        """Called when keyboard is pressed"""
        self.world.player.on_key_press(key, modifiers)
        self.world.player.inventory.change_slot_keyboard(key)

    def on_key_release(self, key: int, modifiers: int) -> None:
        """Called when keyboard is released"""
        self.world.player.on_key_release(key, modifiers)

    def on_mouse_motion(self, x, y, dx, dy):
        world_x, world_y = self.screen_to_world_position(x, y)
        block = self.world.get_block_at_world_position(world_x, world_y)

        # Only show the marker when there is a valid block selection.
        self.bx, self.by = world_x, world_y
        if block and self.world.player.distance_to_block(block) < config.PLAYER_BLOCK_REACH:
            self.b_color = color.GREEN
        elif block:
            self.b_color = color.WHITE
        else:
            self.b_color = color.RED

    def on_mouse_press(self, x: float, y: float, button: int, key_modifiers: int) -> None:
        player = self.world.player
        world_x, world_y = self.screen_to_world_position(x, y)
        block = self.world.get_block_at_world_position(world_x, world_y)
        self.world.dir_of_mouse_from_player(world_x, world_y)
        if button == MOUSE_BUTTON_LEFT:
            # NOTE: This can be improved later with can_break(block) looking at other game states
            if block and self.world.block_break_check(block):
                self.world.remove_block(block)
                player.inventory.add(Item(True, block.block_id))
        elif button == MOUSE_BUTTON_RIGHT and not self.place_cooldown:
            if block:
                return
            self.world.place_block(world_x, world_y)

    def on_mouse_scroll(self, x: int, y: int, scroll_x: int, scroll_y: int):
        self.world.player.inventory.change_slot_mouse(scroll_y)

    def on_mouse_release(self, x: float, y: float, button: int, modifiers: int):
        """ Called when the user presses a mouse button. """
        if button == MOUSE_BUTTON_LEFT:
            self.break_cooldown = False
        if button == MOUSE_BUTTON_RIGHT:
            self.place_cooldown = False

    def on_resize(self, width, height):
        self.hud_camera.resize(width, height)
        self.world.camera.resize(width, height)

    def screen_to_world_position(self, screen_x: float = 0, screen_y: float = 0) -> Tuple[float, float]:
        """
        Convert screen to world position.
        This is normally used to convert mouse coordinates.
        """
        return (
            screen_x + self.world.camera.position[0],
            screen_y + self.world.camera.position[1],
        )


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
        self.angle = 0
        self.frame = 0
        self.done_loading = False

    def on_show(self):
        arcade.set_background_color(color.BLACK)

    def on_draw(self):
        self.window.clear()
        # On frame 0 we render the loading screen so this happens instantly
        # On frame 1 we crate the game object and the loading iterator
        # From frame 2 we invoke loading loading steps until done 
        if self.frame > 1:
            # Run until all visible chunks are loaded
            self.game_view.world.process_new_chunks()
            self.done_loading, _ = self.game_view.world.update_visible_chunks()

            # Trigger next loading step
            self.angle += 5

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

    def on_update(self, delta_time: float):
        if self.frame == 1:
            self.game_view = Game()
            self.game_view.setup()

        # Loading is done. Show the game view (Will happen in next frame)
        if self.done_loading:
            self.window.show_view(self.game_view)

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

    def on_click_start(self, _):
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

    def on_hide_view(self):
        """Disable the UI events"""
        self.manager.disable()


def main():
    """ Main method """
    window = arcade.Window(config.SCREEN_WIDTH, config.SCREEN_HEIGHT, config.SCREEN_TITLE, gc_mode="context_gc",
                           resizable=True)
    window.show_view(StartView())
    arcade.run()


if __name__ == "__main__":
    main()
