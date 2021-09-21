from pathlib import Path

import arcade

class BreakMask(arcade.Sprite):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.break_state = -1
        self.textures = []
        graphics = Path("assets/game_graphics")
        for asset in graphics:
            self.textures.append(arcade.Sprite(asset))

    def add_break_state(self):
        self.break_state += 1
        self.set_texture(self.textures[self.break_state])

    def reset_break_state(self):
        self.break_state = 0
        self.set_texture(self.textures[self.break_state])

class Block(arcade.Sprite):
    def __init__(self, width, height, breaking_time, hp, id, lightning, place_sound, *args, **kwargs):
        super().__init__(*args, **kwargs, image_width = width, image_height = height)
        arcade.Sound(place_sound).play()

        self.width = width
        self.height = height
        self.x = self.center_x
        self.y = self.center_y
        self.hp = hp
        self.id = id
        self.break_mask = BreakMask()
        self.lightning = lightning
        self.breaking_time = breaking_time
    
    def remove(self):
        self = None
        self.draw = None
        self.kill()
    
    def delete(self):
        self.remove() # alias of `remove`
    
    def hp_set(self, val):
        if val <= 0:
            self.remove()
        else:
            self.hp = val

    def check_surrounding(self, spritelists):
        return arcade.check_for_collision_with_lists(self, spritelists)

    def break_anim(self, val):
        self.break_mask.add_break_state
        time.sleep(self.breaking_time)

