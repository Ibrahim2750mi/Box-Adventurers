import time
from pathlib import Path
from typing import Optional

import arcade
from arcade.texture import load_texture
from PIL import Image, ImageEnhance

from misc.item import Item

BREAK_TEXTURES_PATH = Path(__file__).parent.joinpath(f"../../assets/animations/")
BREAK_TEXTURES = [arcade.Texture(path, Image.open(path)) for path in BREAK_TEXTURES_PATH.iterdir()]


class Block(arcade.Sprite):
    def __init__(self, width, height, breaking_time, hp, block_id, bright, *args, scale=1,
                 center_x=0, center_y=0, **kwargs):
        path = Path(__file__).parent.joinpath(f"../../assets/sprites/{block_id}.png")
        super().__init__(filename=str(path), scale=scale, center_x=center_x, center_y=center_y,
                         image_width=width, image_height=height, *args, **kwargs)
        # self.place_sound = place_sound
        # arcade.Sound(place_sound).play()
        self.block_id = block_id
        self.width = width
        self.height = height
        self.x = self.center_x
        self.y = self.center_y
        self.hp = hp
        # self.break_mask = BreakMask()
        self.ORIGINAL_IMAGE = self.texture.image
        self.bright = bright
        self.breaking_time = breaking_time
        self.break_time_left = breaking_time
        self.break_textures = BREAK_TEXTURES
        self.anim_pos = 0
        self.orig_texture = self._texture

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

    def bright_set(self, bright):
        self.bright = bright
        enhancer = ImageEnhance.Brightness(self.ORIGINAL_IMAGE)
        self.texture.image = enhancer.enhance(bright)

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

    def break_(self, block_id) -> None:
        path = Path(__file__).parent.joinpath(f"../../assets/sprites/{block_id}.png")
        self.texture = load_texture(path)
