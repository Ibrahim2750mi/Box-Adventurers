import arcade
import arcade.gui
import gc

# --- Constants ---
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 360
SCREEN_TITLE = "Implement Views Example"


# --- Method 1 for handling click events,
# Create a child class.
class QuitButton(arcade.gui.UIFlatButton):
    def on_click(self, event: arcade.gui.UIOnClickEvent):
        arcade.exit()


class MyWindow(arcade.Window):
    def __init__(self):
        super().__init__(640, 360, "UIFlatButton Example", resizable=True)

        # --- Required for all code that uses UI element,
        # a UIManager to handle the UI.
        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        # Set background color
        #arcade.set_background_color(arcade.color.DARK_BLUE_GRAY)
        self.background = None
        self.frameNum = 22
        self.maxFrames = 285#390

        print(gc.isenabled())

        # Create a vertical BoxGroup to align buttons
        self.v_box = arcade.gui.UIBoxLayout()

        # Create the buttons
        start_button = arcade.gui.UIFlatButton(text="Start Game", width=200, style={"bg_color" : arcade.get_four_byte_color((0,0,60,200))})
        self.v_box.add(start_button.with_space_around(bottom=20))

        settings_button = arcade.gui.UIFlatButton(text="Settings", width=200, style={"bg_color" : arcade.get_four_byte_color((0,0,60,200))})
        self.v_box.add(settings_button.with_space_around(bottom=20))

        # Again, method 1. Use a child class to handle events.
        quit_button = QuitButton(text="Quit", width=200, style={"bg_color" : arcade.get_four_byte_color((0,0,60,200))})
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
        print("Start:", event)

    def on_draw(self):
        arcade.start_render()

        #background gif
        #showing the background image
        self.background = arcade.load_texture(f"D:/ometz/pyweek/32/personal/images/out{self.frameNum}.png")
        arcade.draw_texture_rectangle(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, SCREEN_WIDTH, SCREEN_HEIGHT,
                                      self.background)
        self.background = None
        #gc.collect()
        #changing it to the next frame
        self.frameNum += 1
        if self.frameNum > self.maxFrames:
            self.frameNum = 22

        self.manager.draw()


def main():
    """ Main method """

    # window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    # start_view = MyWindow()
    # window.show_view(start_view)
    window = MyWindow()
    arcade.run()


if __name__ == "__main__":
    main()