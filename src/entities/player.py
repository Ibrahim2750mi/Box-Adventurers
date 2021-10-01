from enum import Enum
from typing import Optional

from arcade import key, load_texture
import arcade

from entities.entity import Entity
from misc.inventory import Inventory
import config

class Direction(Enum):
    LEFT = 0
    RIGHT = 1


class Player(Entity):

    def __init__(
            self,
            image_file: str,
            scale: float,
            center_x: float,
            center_y: float,
            screen_width: int,
            screen_height: int,
            movement_speed: float,
            jump_speed: float,
            flipped_horizontally: bool,
        ) -> None:
        """Initialize the Player.

        :param image_file: Path to the image file.
        :type image_file: str
        :param scale: Scale of the sprite.
        :type scale: float
        :param center_x: Player's x coordinate.
        :type center_x: float
        :param center_y: Player's y coordinate.
        :type center_y: float
        :param screen_width: Width on the screen.
        :type screen_width: int
        :param screen_height: Height of the screen
        :type screen_height: int
        :param movement_speed: Player's movement speed.
        :type movement_speed: float
        :param jump_speed: Player's jump speed.
        :type jump_speed: float
        :param flipped_horizontally: Should the player sprite be flipped.
        :type flipped_horizontally: bool
        """
        super().__init__(
            config.ASSET_DIR / "mobs" / f"{image_file}.png",
            scale * 5 / 2,
            center_x, center_y,
            flipped_horizontally,
        )
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.movement_speed = movement_speed
        self.jump_speed = jump_speed
        self.direction: Optional[Direction] = None
        self.last_faced_dir = "left"
        self.textures = []
        self.textures.append(load_texture(config.ASSET_DIR / "mobs" / f"{image_file}.png",))
        self.textures.append(load_texture(config.ASSET_DIR / "mobs" / f"{image_file}.png", flipped_horizontally=True))
        self._physics_engine: arcade.PhysicsEnginePlatformer = None
        self.inventory = Inventory()

    @property
    def physics_engine(self) -> arcade.PhysicsEnginePlatformer:
        return self._physics_engine

    @physics_engine.setter
    def physics_engine(self, value):
        self._physics_engine = value

    @property
    def x(self) -> float:
        return self.center_x

    @property
    def y(self) -> float:
        return self.center_y

    def on_key_press(self, key_pressed: int, modifier: int) -> None:
        """Called whenever a key is pressed.

        :param key_pressed: Key that got pressed.
        :type key_pressed: int
        :param modifier: Modifiers pressed with the key.
        :type modifier: int
        :param can_jump: If the player on the ground.
        :type can_jump: bool
        """
        if key_pressed == key.UP:
            if self.physics_engine.can_jump():
                self.change_y = self.jump_speed
        elif key_pressed == key.LEFT:
            self.change_x = -self.movement_speed
            self.direction = Direction.LEFT
            self.last_faced_dir = "left"
            self.texture = self.textures[Direction.LEFT.value]
        elif key_pressed == key.RIGHT:
            self.change_x = self.movement_speed
            self.direction = Direction.RIGHT
            self.last_faced_dir = "right"
            self.texture = self.textures[Direction.RIGHT.value]

    def on_key_release(self, key_released: int, modifiers: int) -> None:
        """Called when the user releases a key.

        :param key_pressed: Key that was released.
        :type key_pressed: int
        :param modifiers: Modifiers that were released with the key.
        :type modifiers: int
        """
        if key_released in (key.LEFT, key.RIGHT):
            self.change_x = 0
            self.direction = None

    @property
    def chunk(self):
        return int(self.center_x / 224) + 31
