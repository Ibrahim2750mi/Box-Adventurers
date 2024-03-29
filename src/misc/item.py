from arcade import Sprite, draw_text
from arcade.csscolor import WHITE

import config


class Item(Sprite):

    def __init__(self, stackable: bool, block_id: int, *args, **kwargs):
        super().__init__(
            config.ASSET_DIR / "sprites" / f"{block_id}.png",
            scale=config.INVENTORY_SCALING,
            *args,
            **kwargs,
        )
        self.stackable = stackable
        self.amount = 1
        self.width = config.ICON_SIZE * config.INVENTORY_SCALING
        self.height = config.ICON_SIZE * config.INVENTORY_SCALING
        self.block_id = block_id

    def smart_draw(self, slot: int, cen_x: float, cen_y: float, inv_width: int, inv_height: int) -> None:
        self.center_x = cen_x - (inv_width / 2) + config.INVENTORY_SCALING * 15 + \
                        ((self.width + config.INVENTORY_SCALING) * (slot - 1))
        self.center_y = cen_y - (inv_height / 2) + 2*config.INVENTORY_SCALING/3 + config.INVENTORY_SCALING * 29/3

        self.draw()

        # draw_text("20", self.center_x - 20, self.center_y - 20, WHITE, 18)
        draw_text(str(self.amount), self.center_x + 5, self.center_y - 20, WHITE, 12)

    def replicate(self, center_x: int, center_y: int):
        """Replicate for the player hand."""
        return Sprite(
            config.ASSET_DIR / "sprites" / f"{self.block_id}.png",
            scale=1/(2 * config.SPRITE_PIXEL_SIZE),
            center_x=center_x,
            center_y=center_y
        )
