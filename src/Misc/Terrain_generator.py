from random import choices, randint
from time import perf_counter
from typing import Dict, Tuple

import numpy as np


# sky = 128
# clouds = 129
# stone = 130
# dirt = 131
# coal = 132
# iron = 133
# diamond = 134
# hard_stone = 135

def __gen_empty_chunks(x_min: int = -160, x_max: int = 160, y_min: int = -160, y_max: int = 160) -> \
        dict[Tuple[int, int, int, int], np.ndarray]:
    world = {}
    for x in range(x_min, x_max, 16):
        for y in range(y_min, y_max, 16):
            world[(x + 16, x, y + 16, y)] = np.empty((16, 16), dtype=int)
    return world


def __sky_gen():
    sky = np.full((16, 16), 128)
    clouds_co_ords = np.random.randint(16, size=(14, 2))
    __placer(4, 129, clouds_co_ords, sky)

    return sky


def __generate_upper_mine() -> np.ndarray:
    mine = np.full((16, 16), 130)

    dirt_co_ords = np.random.randint(16, size=(10, 2))
    __placer(randint(6, 8), 131, dirt_co_ords, mine)

    return mine


def __generate_middle_mine(y_max: int) -> np.ndarray:
    mine = np.full((16, 16), 130)

    coal_co_ords = np.random.randint(16, size=(7, 2))
    iron_co_ords = np.random.randint(16, size=(4, 2))
    diamond_co_ords = np.random.randint(16, size=(2, 2))

    if -112 > y_max >= -128:
        __placer(choices((6, 7, 8, 9, 10, 11, 12), (0.3, 0.3, 0.1, 0.1, 0.08, 0.09, 0.03), k=1)[0],
                 132, coal_co_ords, mine)
        __placer(choices((4, 5, 6, 7, 8, 9, 10), (0.3, 0.3, 0.1, 0.1, 0.08, 0.09, 0.03), k=1)[0],
                 133, iron_co_ords, mine)
        __placer(choices((2, 3, 4, 5, 6, 7, 8), (0.3, 0.3, 0.1, 0.1, 0.08, 0.09, 0.03), k=1)[0],
                 134, diamond_co_ords, mine)
    elif -32 >= y_max > -64:
        __placer(choices((10, 11, 12, 13, 14, 15, 16), (0.3, 0.3, 0.1, 0.1, 0.08, 0.09, 0.03), k=1)[0],
                 132, coal_co_ords, mine)
        __placer(choices((7, 8, 9, 10, 11, 12, 13), (0.3, 0.3, 0.1, 0.1, 0.08, 0.09, 0.03), k=1)[0],
                 133, iron_co_ords, mine)
    elif -64 > y_max >= -112:
        __placer(choices((7, 8, 9, 10, 11, 12, 13), (0.3, 0.3, 0.1, 0.1, 0.08, 0.09, 0.03), k=1)[0],
                 132, coal_co_ords, mine)
        __placer(choices((10, 11, 12, 13, 14, 15, 16), (0.3, 0.3, 0.1, 0.1, 0.08, 0.09, 0.03), k=1)[0],
                 133, iron_co_ords, mine)

    return mine


def __generate_lower_mine() -> np.ndarray:
    mine = np.full((16, 16), 135)
    return mine


def gen_world() -> Dict[Tuple[int, ...], np.ndarray]:
    world = __gen_empty_chunks()

    # generating sky
    for co_ords, chunk in world.items():
        if co_ords[3] >= 80:
            world[co_ords] = __sky_gen()

    # generating mines

    # generating upper mine
    for co_ords, chunk in world.items():
        if 0 > co_ords[3] >= -32:
            world[co_ords] = __generate_upper_mine()

    # generating middle mine
    for co_ords, chunk in world.items():
        if -32 > co_ords[3] >= -128:
            world[co_ords] = __generate_middle_mine(co_ords[3])

    # generating lower mine
    for co_ords, chunk in world.items():
        if co_ords[3] <= -144:
            world[co_ords] = __generate_lower_mine()

    return world


def __placer(range_: int, block_id: int, co_ords_arr: np.ndarray, main: np.ndarray) -> None:
    for co_ord_arr in co_ords_arr:
        x_inc = 0
        y_inc = 0
        for _ in range(range_):
            to_be_inc = randint(0, 1)
            if to_be_inc == 1:
                x_inc += 1
            else:
                y_inc += 1

            if co_ord_arr[0] + x_inc < 16 and co_ord_arr[1] + y_inc < 16:
                main[co_ord_arr[0] + x_inc][co_ord_arr[1] + y_inc] = block_id

            elif co_ord_arr[0] + x_inc < 16 and co_ord_arr[1] + y_inc > 15:
                main[co_ord_arr[0] + x_inc][co_ord_arr[1]] = block_id

            elif co_ord_arr[0] + x_inc < 16 and co_ord_arr[1] + y_inc > 15:
                main[co_ord_arr[0]][co_ord_arr[1] + y_inc] = block_id


if __name__ == '__main__':
    s = perf_counter()
    print(gen_world())
    print(perf_counter() - s)
