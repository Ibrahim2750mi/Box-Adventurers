import arcade
from arcade import color

from block.block import Block
from config import (GRAVITY, JUMP_SPEED, MOVEMENT_SPEED, SCREEN_HEIGHT,
                    SCREEN_TITLE, SCREEN_WIDTH, SPRITE_PIXEL_SIZE,
                    SPRITE_SCALING,)
from entities.player import Player
from misc.camera import CustomCamera
from misc.terrain import gen_world


class Game(arcade.Window):
    """Base game class"""

    def __init__(self, width: int, height: int, title: str) -> None:
        """Initializer"""
        super().__init__(width, height, title, resizable=True)

        # Initialising arguments
        self.physics_engine: arcade.PhysicsEnginePlatformer = None
        self.block_list: arcade.SpriteList = None
        self.background_list: arcade.SpriteList = None
        self.player_list: arcade.SpriteList = None
        self.player_sprite: Player = None
        self.camera: CustomCamera = None
        self.hud_camera: arcade.Camera = None

    def setup(self) -> None:
        """Set up the game and initialize the variables."""

        self.setup_world()

        self.camera = CustomCamera(self.width, self.height, self)
        self.hud_camera = arcade.Camera(self.width, self.height)

        self.setup_player()

        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player_sprite,
            [self.block_list],
            gravity_constant=GRAVITY)

        arcade.set_background_color(color.AMAZON)

        self.game_over: bool = False

    def setup_world(self):
        self.block_list = arcade.SpriteList()
        self.background_list = arcade.SpriteList()
        world = gen_world(-160, 160, 0, 320)
        for k, chunk in world.items():
            for inc_y, chunk_row in enumerate(chunk):
                for inc_x, block in enumerate(chunk_row):
                    if block > 129:
                        self.block_list.append(Block(SPRITE_PIXEL_SIZE, SPRITE_PIXEL_SIZE, 2, 2, block, False,
                                                     center_x=(k[0] - inc_x) * SPRITE_PIXEL_SIZE,
                                                     center_y=(k[2] - inc_y) * SPRITE_PIXEL_SIZE))
                    else:
                        self.background_list.append(Block(SPRITE_PIXEL_SIZE, SPRITE_PIXEL_SIZE, 2, 2, block,
                                                          False, center_x=(k[0] - inc_x) * SPRITE_PIXEL_SIZE,
                                                          center_y=(k[2] - inc_y) * SPRITE_PIXEL_SIZE))

    def setup_player(self):
        self.player_list = arcade.SpriteList()

        # Set up the player
        self.player_sprite = Player(":resources:images/animated_characters/female_person/"
                                    "femalePerson_idle.png",
                                    SPRITE_SCALING, 0, 3112, SCREEN_WIDTH,
                                    SCREEN_HEIGHT,
                                    MOVEMENT_SPEED, JUMP_SPEED, False)
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


def main() -> None:
    """Entry point to the game."""
    window = Game(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
