from itertools import combinations
from typing import Any, Dict, List, Optional

import arcade
import numpy as np
import numpy.typing as npt

from block.block import Block
import config


class HorizontalChunk:
    COMBINATIONS = (0, 1, -1, 0, 1, -1)

    def __init__(self, x: int, index: int, data: Optional[Dict] = None):
        """
        :param int x: x position of the chunk
        :param int index: File index for this chunk
        :param data: Chunk data
        """
        self.data = data or {}
        self._block_data = {}

        self._index = index
        self._x = x
        self.world_x = x * config.SPRITE_PIXEL_SIZE - config.SPRITE_PIXEL_SIZE // 2
        self._y = 0
        self._chunks = 0

        self._blocks = arcade.SpriteList(use_spatial_hash=True, lazy=True)
        self._bg_blocks = arcade.SpriteList(use_spatial_hash=True, lazy=True)

        self.bg_block_count = 0
        self.other_block_count = 0

    @property
    def x(self) -> int:
        return self._x

    @property
    def index(self) -> int:
        return self._index

    @property
    def spritelist(self) -> arcade.SpriteList:
        return self._blocks

    def is_visible(self, x_pos: float, max_dist: float) -> bool:
        """Is this chunk visible (in pixels)"""
        # Left and right boundary of chunk
        chunk_min, chunk_max = self.world_x, self.world_x + config.CHUNK_WIDTH_PIXELS
        # Left and right boundary of visible area
        word_min, world_max = x_pos - max_dist, x_pos + max_dist

        # Chunk is outside area (left side)
        if chunk_max < word_min:
            return False

        # chunk is outside area (right side)
        if chunk_min > world_max:
            return False

        # Otherwise we have a visible chunk
        return True

    def make_sprite_list(self):
        for (x_inc, y_inc), block_id in self.data.items():
            # HACK: Remove air blocks for now. No longer the hack is needed.
            cx = (self._x + x_inc) * config.SPRITE_PIXEL_SIZE
            cy = y_inc * config.SPRITE_PIXEL_SIZE
            block = Block(
                width=config.SPRITE_PIXEL_SIZE,
                height=config.SPRITE_PIXEL_SIZE,
                breaking_time=2,
                hp=2,
                block_id=block_id,
                bright=False,
                center_x=cx,
                center_y=cy)

            self._block_data[(x_inc, y_inc)] = block

            if block_id > 129:
                self._blocks.append(block)
            else:
                self._bg_blocks.append(block)

            yield

    def __getitem__(self, key: int):
        return self.data[key]

    def __setitem__(self, _: Any, value: npt.NDArray[np.int_]):
        self._chunks += 1
        for y_row in np.flip(value):
            for x_inc, block_ in enumerate(y_row):
                if block_ > 129:
                    self.other_block_count += 1
                else:
                    self.bg_block_count += 1
                self.data[x_inc, self._y] = block_
            self._y += 1

    def __iter__(self):
        return self.data.__iter__()

    def __repr__(self):
        return f"Chunk[{self.index}]"

    def draw(self):
        self._blocks.draw(pixelated=True)
        self._bg_blocks.draw(pixelated=True)

    def remove(self, block: Block):
        block.remove_from_sprite_lists()
        self._block_remove(block.center_x, block.center_y)

        new_block = Block(
            width=config.SPRITE_PIXEL_SIZE,
            height=config.SPRITE_PIXEL_SIZE,
            breaking_time=2,
            hp=2,
            block_id=128,
            bright=False,
            center_x=block.center_x,
            center_y=block.center_y
        )
        self._bg_blocks.append(new_block)
        self._block_add(new_block)

    def add(self, center_x, center_y, block_id):
        block = self._block_data.get((center_x // 20, center_y // 20))
        if not block:
            return
        block.remove_from_sprite_lists()
        self._block_remove(center_x, center_y)

        new_block = Block(
            width=config.SPRITE_PIXEL_SIZE,
            height=config.SPRITE_PIXEL_SIZE,
            breaking_time=2,
            hp=2,
            block_id=block_id,
            bright=False,
            center_x=center_x,
            center_y=center_y
        )
        self._blocks.append(new_block)
        self._block_add(new_block)

    def get_neighbouring_blocks(self, block: Block) -> Dict[str, Optional[Block]]:
        bx, by = block.center_x // 20, block.center_y // 20
        y_dict = {1: "N", 0: "", -1: "S"}
        x_dict = {1: "E", 0: "", -1: "W"}
        unique_combs = set(combinations(self.COMBINATIONS, 2))
        ret = {}
        for x, y in unique_combs:
            direction = y_dict[y] + x_dict[x]
            ret[direction] = [None if self.data.get((bx + x, by + y)) in (128, 129) else
                              self.data.get((bx + x, by + y))][0]
        return ret

    def _block_add(self, new_block: Block):
        key_ = ((new_block.center_x // 20) % 15, (new_block.center_y // 20) % 15)
        self.data[key_] = new_block.block_id
        self._block_data[key_] = new_block

    def _block_remove(self, x: int, y: int):
        key_ = ((x // 20) % 15, (y // 20) % 15)
        del (self.data[key_])
        del (self._block_data[key_])
