import time
from pathlib import Path

import arcade
from PIL import ImageEnhance


class BreakMask(arcade.Sprite):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.break_state = -1
        self.textures = []
        graphics = Path("assets/game_graphics")
        for asset in graphics.iterdir():
            self.textures.append(arcade.Sprite(asset))

    def add_break_state(self):
        self.break_state += 1
        self.set_texture(self.textures[self.break_state])

    def reset_break_state(self):
        self.break_state = 0
        self.set_texture(self.textures[self.break_state])


class Block(arcade.Sprite):
    def __init__(self, width, height, breaking_time, hp, block_id, bright, place_sound, *args, scale=1,
                 center_x=0, center_y=0, **kwargs):
        path = Path(__file__).parent.joinpath(f"../../assets/Sprites/{block_id}.png")
        super().__init__(*args, **kwargs,
                         filename=str(path), scale=scale, center_x=center_x, center_y=center_y,
                         image_width=width, image_height=height)
        self.place_sound = place_sound
        # arcade.Sound(place_sound).play()
        self.block_id = block_id

        self.width = width
        self.height = height
        self.x = self.center_x
        self.y = self.center_y
        self.hp = hp
        # self.break_mask = BreakMask()
        self.bright = bright
        self.breaking_time = breaking_time

    def hp_set(self, val):
        if val <= 0:
            self.kill()
        else:
            self.hp = val

    def check_surrounding(self, spritelists):
        return arcade.check_for_collision_with_lists(self, spritelists)

    def break_anim(self, val):
        self.hpset(val)
        # self.break_mask.add_break_state()
        time.sleep(self.breaking_time)

    def bright_set(self, bright):
        self.bright = bright
        enhancer = ImageEnhance.Brightness(self.texture.image)
        self.texture.image = enhancer.enhance(bright)
