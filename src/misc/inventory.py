from pathlib import Path
from typing import Optional

from arcade import Sprite

from config import INVENTORY_CENTER_X, INVENTORY_CENTER_Y, MAX_SLOTS, MAX_STACK
from misc.item import Item


class InventoryFullError(Exception):
    def __init__(self) -> None:
        super().__init__("Inventory is full.")


class Inventory(Sprite):
    def __init__(self) -> None:
        path = Path(__file__).parent.joinpath("../../assets/sprites/inventory.jpg")
        super().__init__(filename=str(path), center_x=INVENTORY_CENTER_X, center_y=INVENTORY_CENTER_Y)
        self.max_slots: int = MAX_SLOTS
        self.slots: dict[int, Optional[Item]] = {
            i: None for i in range(1, self.max_slots + 1)}
        self.filled_slots = 0

    def add(self, item: Item) -> None:
        if self.filled_slots == self.max_slots:
            raise InventoryFullError
        added = False
        for slot in self.slots:
            slot_item = self.slots[slot]
            if slot_item is not None and slot_item.name == item.name:
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
        for item in self.slots.values():
            if item is not None:
                item.draw()

    def remove(self, item: Item) -> None:
        for i in range(len(self.slots), 0, -1):
            slot_item = self.slots[i]
            if slot_item is not None and slot_item.name == item.name:
                slot_item.amount -= 1
                break
