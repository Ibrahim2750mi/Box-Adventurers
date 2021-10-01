from typing import Any, Dict, Optional

import arcade
import numpy as np
import numpy.typing as npt

from block.block import Block
from config import (SPRITE_PIXEL_SIZE)


class HorizontalChunk:
    def __init__(self, x: int, chunk: Optional[Dict] = None):
        if not chunk:
            chunk = {}
        self._iterable = chunk
        self._y = 0
        self._x = x
        self._chunks = 0
        self._sprites = arcade.SpriteList()
        self.bg_block_count = 0
        self.other_block_count = 0

    def __getitem__(self, key: int):
        return self._iterable[key]

    def __setitem__(self, _: Any, value: npt.NDArray[np.int_]):
        self._chunks += 1
        for y_row in np.flip(value):
            for x_inc, block_ in enumerate(y_row):
                if block_ > 129:
                    self.other_block_count += 1
                else:
                    self.bg_block_count += 1
                self._iterable[x_inc, self._y] = block_
            self._y += 1

    def __iter__(self):
        return self._iterable.__iter__()

    @property
    def iterable(self):
        return self._iterable
    
    def make_sprite_list(self, dict_of_ids: Dict):
        for (x_inc, y_inc), block_id in dict_of_ids.items():
            # HACK: Remove air blocks for now
            if block_id < 130:
                continue
            block = Block(
                width=SPRITE_PIXEL_SIZE,
                height= SPRITE_PIXEL_SIZE,
                breaking_time=2,
                hp=2,
                block_id=block_id,
                bright=False,
                center_x=(self._x + x_inc) * SPRITE_PIXEL_SIZE,
                center_y=y_inc * SPRITE_PIXEL_SIZE)
            self._sprites.append(block)

    @property
    def sprites(self):
        return self._sprites
