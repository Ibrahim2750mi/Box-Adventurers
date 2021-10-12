from typing import Optional

import arcade.key
from arcade import Sprite
from pyglet.math import Vec2

from misc.item import Item
import config


class InventoryFullError(Exception):
    def __init__(self) -> None:
        super().__init__("Inventory is full.")


class Inventory(Sprite):
    def __init__(self) -> None:
        super().__init__(
            filename=config.ASSET_DIR / "sprites" / "inventory.png",
            center_x=0,
            center_y=0,
            scale=config.INVENTORY_SCALING,
        )
        self.max_slots: int = config.MAX_SLOTS
        self.slots: dict[int, Optional[Item]] = {i: None for i in range(1, self.max_slots + 1)}
        self.filled_slots = 0
        self.selected_slot = 1

    def add(self, item: Item) -> None:
        if self.filled_slots == self.max_slots:
            raise InventoryFullError
        added = False
        if item.stackable:
            for i in range(len(self.slots), 0, -1):
                slot_item = self.slots[i]
                if slot_item is not None and slot_item.block_id == item.block_id:
                    added = True
                    if slot_item.amount == config.MAX_STACK:
                        self.slots[self.get_free_slot()] = item
                        self.filled_slots += 1
                    else:
                        slot_item.amount += 1
                    break
        if not added:
            self.slots[self.get_free_slot()] = item
            self.filled_slots += 1

    def setup_coords(self, pos: Vec2) -> None:
        self.center_x = pos[0] + config.SCREEN_WIDTH / 2
        self.center_y = pos[1] + self.height / 2

    def get_free_slot(self) -> int:
        for slot in self.slots:
            if self.slots[slot] is None:
                return slot
        raise InventoryFullError

    def smart_draw(self):
        self.draw(pixelated=True)
        for slot, item in self.slots.items():
            if slot == self.selected_slot:
                self.draw_outline(slot)
            if item:
                item.smart_draw(slot, self.center_x, self.center_y, self.width, self.height)

    def remove(self, item: Item) -> None:
        for i in range(len(self.slots), 0, -1):
            slot_item = self.slots[i]
            if slot_item is not None and slot_item.block_id == item.block_id:
                slot_item.amount -= 1
                if slot_item.amount == 0:
                    self.slots[i] = None
                break

    def change_slot_keyboard(self, key_pressed: int = 0):
        # https://api.arcade.academy/en/latest/arcade.key.html?highlight=arcade.key ->  Numbers on the main keyboard
        if 57 >= key_pressed > 48:
            self.selected_slot = key_pressed - 48

    def change_slot_mouse(self, scroll_y: int = 0):
        if self.selected_slot == 1 and abs(scroll_y) == scroll_y:
            self.selected_slot = 9
            return
        elif self.selected_slot == 9 and abs(scroll_y) != scroll_y:
            self.selected_slot = 1
            return
        self.selected_slot -= scroll_y

    def get_selected_item(self, center_x: int, center_y: int) -> Optional[arcade.Sprite]:
        item = self.slots[self.selected_slot]
        if not item:
            return

        return item.replicate(center_x, center_y)

    def draw_outline(self, slot: int):
        rw = config.ICON_SIZE * config.INVENTORY_SCALING
        rx = self.center_x - (self.width / 2) + config.INVENTORY_SCALING * 15 \
            + ((rw + config.INVENTORY_SCALING) * (slot - 1))
        ry = self.center_y - (self.height / 2) + 2 + config.INVENTORY_SCALING * 10
        arcade.draw_rectangle_outline(center_x=rx, center_y=ry, width=rw, height=rw, color=
                                      (200, 200, 200), border_width=4)
