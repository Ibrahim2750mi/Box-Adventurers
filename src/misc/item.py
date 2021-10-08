from arcade import Sprite, draw_text
from arcade.csscolor import WHITE
import config


class Item(Sprite):

    def __init__(self, stackable: bool, block_id: int, *args, **kwargs):
        super().__init__(
            filename=config.ASSET_DIR / "sprites" / f"{block_id}.png",
            scale=config.INVENTORY_SCALING,
            *args,
            **kwargs,
        )
        self.stackable = stackable
        self.amount = 1
        self.width = config.ICON_SIZE * config.INVENTORY_SCALING
        self.height = config.ICON_SIZE * config.INVENTORY_SCALING
        self.block_id = block_id

    def draw(self, slot: int, cen_x: float, cen_y: float, inv_width: int, inv_height: int) -> None:
        super().draw(pixelated=True)
        self.center_x = cen_x - (inv_width / 2) + 45 + ((self.width + 3) * (slot - 1))
        self.center_y = cen_y - (inv_height / 2) + 2 + 29

        # draw_text("20", self.center_x - 20, self.center_y - 20, WHITE, 18)
        draw_text(str(self.amount), self.center_x + 10, self.center_y - 20, WHITE, 20, width=40)
