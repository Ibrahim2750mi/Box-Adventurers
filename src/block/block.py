class Block(arcade.Sprite):
    def __init__(self, width, height, breaking_time, hp, id, lightning, place_sound, textures, *args, **kwargs):
        super().__init__(*args, **kwargs, image_width = width, image_height = height, texture = textures[0])
        arcade.Sound(place_sound).play()

        for texture in textures:
            self.append_texture(texture)

        self.width = width
        self.height = height
        self.x = self.center_x-width/2
        self.y = self.center_y-height/2
        self.hp = hp
        self.id = id
        self.texture = iter(self.textures)
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
        self.set_texture = next(self.texture)
        self.hp_set(self.hp - val)
        time.sleep(self.breaking_time)
