from abc import ABC
from typing import Optional

from arcade import Camera
from pyglet.math import Vec2

from entities.player import Direction, Player


class CustomCamera(Camera, ABC):
    def __init__(self):
        super().__init__()

    def center_camera_to_player(self, player_sprite: Player) -> None:
        x_offset = self.get_x_offset(player_sprite.direction)
        screen_center_x = player_sprite.center_x - (self.viewport_width / 2) + x_offset
        screen_center_y = player_sprite.center_y - (self.viewport_height / 2)

        # Don't let camera travel past 0. GeneralMud - Let it travel beyond that like minecraft :).
        # screen_center_x = max(screen_center_x, 0)
        # screen_center_y = max(screen_center_y, 0)
        player_centered = Vec2(screen_center_x, screen_center_y)

        self.move_to(player_centered, 0.2)

    def get_x_offset(self, direction: Optional[Direction]):
        x_offset = 0
        if direction is not None:
            x_offset = 80 if direction == Direction.RIGHT else -80
        return x_offset
