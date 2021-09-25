from pathlib import Path
from typing import Optional

from arcade import Sprite
from pyglet.math import Vec2

from config import INVENTORY_SCALING, MAX_SLOTS, MAX_STACK, SCREEN_WIDTH
from misc.item import Item


class InventoryFullError(Exception):
    def __init__(self) -> None:
        super().__init__("Inventory is full.")


class Inventory(Sprite):
    def __init__(self) -> None:
        path = Path(__file__).parent.joinpath("../../assets/sprites/inventory.png")
        super().__init__(filename=str(path), center_x=0, center_y=0, scale=INVENTORY_SCALING)
        self.max_slots: int = MAX_SLOTS
        self.slots: dict[int, Optional[Item]] = {
            i: None for i in range(1, self.max_slots + 1)}
        self.filled_slots = 0

    def add(self, item: Item) -> None:
        if self.filled_slots == self.max_slots:
            raise InventoryFullError
        added = False
        if item.stackable:
            for slot in self.slots:
                slot_item = self.slots[slot]
                if slot_item is not None and slot_item.block_id == item.block_id:
                    added = True
                    if slot_item.amount == MAX_STACK:
                        self.slots[self.get_free_slot()] = item
                        self.filled_slots += 1
                        break
                    else:
                        slot_item.amount += 1
        if not added:
            self.slots[self.get_free_slot()] = item
            self.filled_slots += 1

    def get_free_slot(self) -> int:
        for slot in self.slots:
            if self.slots[slot] is None:
                return slot
        raise InventoryFullError

    def draw(self) -> None:
        super().draw()
        for slot, item in self.slots.items():
            if item is not None:
                item.draw(slot, self.center_x, self.center_y, self.width, self.height)

    def update(self, pos: Vec2) -> None:
        super().update()
        self.center_x = pos[0] + SCREEN_WIDTH / 2
        self.center_y = pos[1] + self.height / 2

    def remove(self, item: Item) -> None:
        for i in range(len(self.slots), 0, -1):
            slot_item = self.slots[i]
            if slot_item is not None and slot_item.block_id == item.block_id:
                slot_item.amount -= 1
                break
