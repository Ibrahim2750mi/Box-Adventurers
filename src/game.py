import arcade
from arcade import color

from block.block import Block
from config import (GRAVITY, GRID_PIXEL_SIZE, JUMP_SPEED, MOVEMENT_SPEED,
                    SCREEN_HEIGHT, SCREEN_TITLE, SCREEN_WIDTH,
                    SPRITE_PIXEL_SIZE, SPRITE_SCALING, )
from entities.player import Player
from misc.terrain import gen_world


# TODO: integrate the gen_world with block class and convert it to sprite lists for actual use
# from misc.terrain import gen_world


class Game(arcade.Window):
    """Base game class"""

    def __init__(self, width: int, height: int, title: str) -> None:
        """Initializer"""

        super().__init__(width, height, title, resizable=True)

        # Initialising arguments
        self.physics_engine = None
        self.view_left = None
        self.view_bottom = None
        self.game_over = None
        self.block_list = None
        self.background_list = None
        self.player_list = None
        self.player_sprite = None

    def setup(self) -> None:
        """Set up the game and initialize the variables."""

        self.setup_world()
        self.setup_player()

        self.physics_engine: arcade.PhysicsEnginePlatformer = arcade.PhysicsEnginePlatformer(self.player_sprite,
                                                                                             [self.block_list],
                                                                                             gravity_constant=GRAVITY)

        arcade.set_background_color(color.AMAZON)

        self.view_left: int = 0
        self.view_bottom: int = 0

        self.game_over: bool = False

    def setup_world(self):
        self.block_list: arcade.SpriteList = arcade.SpriteList()
        self.background_list: arcade.SpriteList = arcade.SpriteList()
        world = gen_world(0, 384, 0, 320)
        for k, chunk in world.items():
            for inc_y, chunk_row in enumerate(chunk):
                for inc_x, block in enumerate(chunk_row):
                    if block > 129:
                        self.block_list.append(Block(SPRITE_PIXEL_SIZE, SPRITE_PIXEL_SIZE, 2, 2, block, False, False,
                                                     center_x=(k[1] + inc_x) * SPRITE_PIXEL_SIZE,
                                                     center_y=(k[3] + inc_y) * SPRITE_PIXEL_SIZE))
                    else:
                        self.background_list.append(Block(SPRITE_PIXEL_SIZE, SPRITE_PIXEL_SIZE, 2, 2, block, False,
                                                          False, center_x=(k[1] + inc_x) * SPRITE_PIXEL_SIZE,
                                                          center_y=(k[1] + inc_x) * SPRITE_PIXEL_SIZE))

    def setup_player(self):
        self.player_list: arcade.SpriteList = arcade.SpriteList()

        # Set up the player
        self.player_sprite: Player = Player(":resources:images/animated_characters/female_person/"
                                            "femalePerson_idle.png",
                                            SPRITE_SCALING, 0, 5120, SCREEN_WIDTH,
                                            SCREEN_HEIGHT, MOVEMENT_SPEED, JUMP_SPEED, False)
        self.player_list.append(self.player_sprite)

    def on_draw(self) -> None:
        """
        Render the screen.
        """

        # This command has to happen before we start drawing
        arcade.start_render()

        # Draw the sprites.
        self.background_list.draw()
        self.block_list.draw()
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
