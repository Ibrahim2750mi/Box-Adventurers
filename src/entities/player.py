from enum import Enum
from pathlib import Path
from typing import Optional

from arcade import key, load_texture

from entities.entity import Entity
from misc.inventory import Inventory


class Direction(Enum):
    LEFT = 0
    RIGHT = 1


class Player(Entity):

    def __init__(
            self, image_file: str, scale: float, center_x: float, center_y: float, screen_width: int,
            screen_height: int, movement_speed: float, jump_speed: float, flipped_horizontally: bool) -> None:
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
        path = Path(__file__).parent.joinpath(f"../../assets/mobs/{image_file}.png")
        super().__init__(
            str(path), scale * 5 / 2, center_x, center_y, flipped_horizontally)
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.movement_speed = movement_speed
        self.jump_speed = jump_speed
        self.direction: Optional[Direction] = None
        self.inventory = Inventory()
        self.last_faced_dir = "left"
        self.textures = []
        self.textures.append(load_texture(str(path)))
        self.textures.append(load_texture(str(path), flipped_horizontally=True))

    def on_key_press(
            self, key_pressed: int, modifier: int,
            can_jump: bool) -> None:
        """Called whenever a key is pressed.

        :param key_pressed: Key that got pressed.
        :type key_pressed: int
        :param modifier: Modifiers pressed with the key.
        :type modifier: int
        :param can_jump: If the player on the ground.
        :type can_jump: bool
        """
        if key_pressed == key.UP:
            if can_jump:
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
        :param modifiers: Mofidiers that were released with the key.
        :type modifiers: int
        """
        if key_released in (key.LEFT, key.RIGHT):
            self.change_x = 0
            self.direction = None

    @property
    def chunk(self):
        return int(self.center_x / 224) + 31
