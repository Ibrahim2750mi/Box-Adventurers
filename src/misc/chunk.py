from collections import deque

import numpy as np
import numpy.typing as npt

from block.block import Block
from config import (SPRITE_PIXEL_SIZE)


class HorizontalChunk:
    def __init__(self, x: int):
        self.__iterable = deque()
        self.__y = 0
        self.__x = x
        self.__chunks = 0
        self.bg_block_count = 0
        self.other_block_count = 0

    def __getitem__(self, key: int):
        return self.__iterable[key]

    def __setitem__(self, un_used: int, value: npt.NDArray[np.int_]):
        self.__chunks += 1
        for y_row in np.flip(value):
            for x_inc, block_ in enumerate(y_row):
                if block_ > 129:
                    self.other_block_count += 1
                else:
                    self.bg_block_count += 1
                block = Block(SPRITE_PIXEL_SIZE, SPRITE_PIXEL_SIZE, 2, 2, block_, False,
                              center_x=(self.__x + x_inc) * SPRITE_PIXEL_SIZE,
                              center_y=self.__y * SPRITE_PIXEL_SIZE)
                self.__iterable.append(block)
            self.__y += 1

    def __iter__(self):
        return self.__iterable.__iter__()

    def get_iterable(self):
        return self.__iterable

    def __add__(self, other):
        return self.__iterable + other.get_iterable()
