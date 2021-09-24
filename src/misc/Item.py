import arcade


class Item(arcade.Sprite):
    def __init__(self, stackable: bool, max_stack: int, inventory_slot: tuple,
                 actual_amount: int, block_id: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stackable = stackable
        self.max_stack = max_stack
        self.inventory_slot = inventory_slot
        self.actaul_amout = actual_amount
        self.block_id = block_id

    def change_inventory_slot(self, position: tuple) -> None:
        self.inventory_slot = position

    def add_ammount(self, amount: int) -> None:
        self.actual_amount += amount

    def delete_ammount(self, amount: int = 0, all: bool = False) -> None:
        self.actual_amount -= amount
        if self.actual_amount < 0 or all is True:
            self.kill()
