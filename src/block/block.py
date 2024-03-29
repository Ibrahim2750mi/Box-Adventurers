import time
from typing import Optional

import arcade

import config
from misc.item import Item

BREAK_TEXTURES = [arcade.load_texture(path) for path in (config.ASSET_DIR / "animations").iterdir()]
BLOCK_TEXTURES = {
    block_id: arcade.load_texture(config.ASSET_DIR / "sprites" / f"{block_id}.png") for block_id in range(128, 156)
}


class Block(arcade.Sprite):
    def __init__(
        self,
        width,
        height,
        breaking_time,
        hp,
        block_id,
        bright,
        *args,
        scale=1,
        center_x=0,
        center_y=0,
        **kwargs
    ):
        super().__init__(
            BLOCK_TEXTURES[block_id],
            scale=scale,
            center_x=center_x,
            center_y=center_y,
        )
        # self.place_sound = place_sound
        # arcade.Sound(place_sound).play()
        self.block_id = block_id
        self.width = width
        self.height = height
        # self.hp = hp
        # self.break_mask = BreakMask()
        # self.ORIGINAL_IMAGE = self.texture.image
        # self.bright = bright
        self.breaking_time = breaking_time
        # self.break_time_left = breaking_time
        # self.break_textures = BREAK_TEXTURES
        # self.anim_pos = 0
        # self.orig_texture = self._texture

    def hp_set(self, val):
        if val <= 0:
            self.kill()
        else:
            self.hp = val

    def check_surrounding(self, spritelists):
        return arcade.check_for_collision_with_lists(self, spritelists)

    def break_anim(self, val):
        self.hp_set(val)
        # self.break_mask.add_break_state()
        time.sleep(self.breaking_time)

    # NOTE: This should use sprite color instead
    # def bright_set(self, bright):
    #     self.bright = bright
    #     enhancer = ImageEnhance.Brightness(self.ORIGINAL_IMAGE)
    #     self.texture.image = enhancer.enhance(bright)

    def _break(self, delta_time) -> Optional[Item]:
        self.break_time_left -= delta_time
        if self.breaking_time < 0:
            return Item(stackable=True, max_stack=64, inventory_slot=0, actual_amount=1, block_id=self.block_id)
        self.anim_pos += 1
        self.texture = self.break_textures[self.anim_pos]

    def stop_breaking(self) -> None:
        # Reset time and texture
        self.break_time_left = self.breaking_time
        self.texture = self.orig_texture

    # def break_(self, block_id) -> None:
    #     self.texture = load_texture(config.ASSET_DIR / "sprites" / f"{block_id}.png")

    # Optimization experiment
    # def _get_left(self):
    #     return self.center_x - self.width / 2

    # def _get_right(self):
    #     return self.center_x + self.width / 2

    # def _get_top(self):
    #     return self.center_y + self.height / 2

    # def _get_bottom(self):
    #     return self.center_y - self.height / 2

    # left = property(_get_left, None)
    # right = property(_get_right, None)
    # top = property(_get_top, None)
    # bottom = property(_get_bottom, None)
