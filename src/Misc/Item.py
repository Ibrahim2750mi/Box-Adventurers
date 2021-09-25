from pathlib import Path

from arcade import Sprite

from config import SPRITE_SCALING


class Item(Sprite):
    def __init__(self, name: str, stackable: bool, block_id: int, *args, **kwargs):
        path = Path(__file__).parent.joinpath(f"../../assets/sprites/{block_id}.png")
        super().__init__(filename=str(path), scale=SPRITE_SCALING, *args, **kwargs)
        self.name = name
        self.stackable = stackable
        self.amount = 1
        self.block_id = block_id
