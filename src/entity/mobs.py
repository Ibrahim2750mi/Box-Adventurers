import random
from typing import Any, List, Tuple

import arcade

from src.constants import SPRITE_SCALING


class Mob(arcade.Sprite):
    def __init__(self: Any, health: int, drops: List[Tuple[str, int]]) -> None:
        self.health = health
        self.drops = drops

    def random_move(self: Any) -> None:
        self.change_x += random.choices([0, 24, -24], weights=[3, 1, 1])

    def kill(self: Any) -> List:
        return self.drops


class Cow(Mob):
    def __init__(
        self: Any, x: int, y: int, health: int, drops: List[Tuple[str, int]]
    ) -> None:

        super().__init__(health, drops)
        arcade.Sprite.__init__(
            self, "assets/cow.png", SPRITE_SCALING, center_x=x, center_y=y
        )


class Sheep(Mob):
    def __init__(
        self: Any, x: int, y: int, health: int, drops: List[Tuple[str, int]]
    ) -> None:

        super().__init__(health, drops)
        arcade.Sprite.__init__(
            self, "assets/sheep.png", SPRITE_SCALING, center_x=x, center_y=y
        )
