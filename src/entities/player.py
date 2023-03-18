import math
from abc import ABC
from enum import Enum
from typing import Optional

import arcade
from arcade import key, load_texture_pair

import config
from entities.entity import Entity
from misc.inventory import Inventory


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
        self.textures.extend(load_texture_pair(config.ASSET_DIR / "mobs" / f"{image_file}.png"))
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

    @property
    def chunk(self):
        """The chunk index the player is located in"""
        return int((self.center_x + config.SPRITE_PIXEL_SIZE / 2) // 320)

    def distance_to_block(self, block):
        """Distance from player and a block"""
        return math.sqrt(
            (self.center_x - block.center_x) ** 2 + (self.center_y - block.center_y) ** 2
        )

    def on_key_press(self, key_pressed: int, _: int) -> None:
        """Called whenever a key is pressed."""
        if key_pressed in (key.UP, key.W):
            if self.physics_engine.can_jump():
                self.change_y = self.jump_speed
        elif key_pressed in (key.LEFT, key.A):
            self.change_x = -self.movement_speed
            self.direction = Direction.LEFT
            self.last_faced_dir = "left"
            self.texture = self.textures[Direction.LEFT.value]
        elif key_pressed in (key.RIGHT, key.D):
            self.change_x = self.movement_speed
            self.direction = Direction.RIGHT
            self.last_faced_dir = "right"
            self.texture = self.textures[Direction.RIGHT.value]

    def on_key_release(self, key_released: int, _: int) -> None:
        """Called when the user releases a key."""
        if key_released in (key.LEFT, key.RIGHT, key.A, key.D):
            self.change_x = 0
            self.direction = None

    @property
    def hand(self) -> Optional[arcade.Sprite]:
        return self.inventory.get_selected_item(self.center_x - 8, self.center_y - 8)

    @property
    def eyes(self) -> int:
        """Returns the Y position of the player's eyes."""
        return self.center_y + (config.PLAYER_SCALING * 16)


class PlayerSpriteList(arcade.SpriteList, ABC):
    def __init__(self, player: Player):
        super(PlayerSpriteList, self).__init__(lazy=True)
        self.player = player
        self.append(player)

    def update_list(self):
        if len(self) != 1:
            self.pop()
        hand = self.player.hand
        if not hand:
            return
        self.append(hand)

    def __str__(self):
        if len(self) == 1:
            return str(self[0])
        return str(self[0], self[1])
