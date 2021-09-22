import arcade
from arcade import color

from config import (GRAVITY, GRID_PIXEL_SIZE, JUMP_SPEED, MOVEMENT_SPEED,
                    SCREEN_HEIGHT, SCREEN_TITLE, SCREEN_WIDTH, SPRITE_SCALING,)
from entities.player import Player

# TODO: integrate the gen_world with block class and convert it to sprite lists for actual use
# from misc.terrain import gen_world


class Game(arcade.Window):
    """Base game class"""

    def __init__(self, width: int, height: int, title: str) -> None:
        """Initializer"""

        super().__init__(width, height, title)

    def setup(self) -> None:
        """ Set up the game and initialize the variables. """

        self.player_list = arcade.SpriteList()

        # Set up the player
        self.player_sprite = Player(":resources:images/animated_characters/female_person/femalePerson_idle.png",
                                    SPRITE_SCALING, 2 * GRID_PIXEL_SIZE, 3 * GRID_PIXEL_SIZE, SCREEN_WIDTH,
                                    SCREEN_HEIGHT, MOVEMENT_SPEED, JUMP_SPEED, False)
        self.player_list.append(self.player_sprite)

        self.physics_engine = arcade.PhysicsEnginePlatformer(self.player_sprite, self.all_wall_list,
                                                             gravity_constant=GRAVITY)

        # Set the background color
        arcade.set_background_color(color.AMAZON)

        # Set the viewport boundaries
        # These numbers set where we have 'scrolled' to.
        self.view_left = 0
        self.view_bottom = 0

        self.game_over = False

    def on_draw(self) -> None:
        """
        Render the screen.
        """

        # This command has to happen before we start drawing
        arcade.start_render()

        # Draw the sprites.
        self.static_wall_list.draw()
        self.moving_wall_list.draw()
        self.player_list.draw()

        # Put the text on the screen.
        # Adjust the text position based on the viewport so that we don't
        # scroll the text too.
        distance = self.player_sprite.right
        output = f"Distance: {distance}"
        arcade.draw_text(output, self.view_left + 10, self.view_bottom + 20, color.WHITE, 14)

    def on_key_press(self, key: int, modifiers: int) -> None:
        """
        Called whenever the mouse moves.
        """
        self.player_sprite.on_key_press(key, modifiers, self.physics_engine.can_jump())

    def on_key_release(self, key: int, modifiers: int) -> None:
        """
        Called when the user presses a mouse button.
        """
        self.player_sprite.on_key_release(key, modifiers)

    def on_update(self, delta_time: float) -> None:
        """ Movement and game logic """

        self.physics_engine.update()


def main() -> None:
    """ Main function """
    window = Game(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
