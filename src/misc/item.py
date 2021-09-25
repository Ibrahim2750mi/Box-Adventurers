from pathlib import Path

from arcade import Sprite, draw_text
from arcade.csscolor import WHITE

from config import ICON_SIZE, INVENTORY_SCALING


class Item(Sprite):
    def __init__(self, stackable: bool, block_id: int, *args, **kwargs):
        path = Path(__file__).parent.joinpath(f"../../assets/sprites/{block_id}.png")
        super().__init__(filename=str(path), scale=INVENTORY_SCALING, *args, **kwargs)
        self.stackable = stackable
        self.amount = 1
        self.width = ICON_SIZE * INVENTORY_SCALING
        self.height = ICON_SIZE * INVENTORY_SCALING
        self.block_id = block_id

    def draw(self, slot: int, cen_x: float, cen_y: float, inv_width: int, inv_height: int) -> None:
        super().draw()
        self.center_x = cen_x - (inv_width / 2) + 45 + ((self.width + 3) * (slot - 1))
        self.center_y = cen_y - (inv_height / 2) + 2 + 29

        draw_text(str(slot), self.center_x - 20, self.center_y - 20, WHITE, 18)
