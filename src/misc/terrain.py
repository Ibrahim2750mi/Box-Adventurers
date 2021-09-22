from collections import deque
from copy import deepcopy
from functools import cache
from math import ceil, floor
from random import choice, choices, randint
from typing import Any, Callable, Dict, NewType, Tuple

import numpy as np

# sky = 128
# clouds = 129
# stone = 130
# dirt = 131
# coal = 132
# iron = 133
# diamond = 134
# hard_stone = 135
# oak leaf = 136
# oak log = 137
# timber leaf = 138
# timber log = 139
# teak leaf = 140
# teak log = 141
# pumice = 142
# basalt = 143
# obsidian = 144
# molten rock = 145
# burned stone = 146
# mossy dirt = 147
# mahagoni leaf = 148
# mahagoni log = 149
# mangrove leaf = 150
# mangrove log = 151
# sand = 152
# cactus = 153
# dead bush = 154

Hex = NewType("Hex", str)


@cache
def __tree(tree_type: Hex, jungle: bool = False) -> np.ndarray:
    # Function to generate a numpy tree.
    if jungle:
        k = 2
        t = np.zeros((10, 5))
    else:
        k = 0
        t = np.zeros((6, 3))

    int_tree_type = int(tree_type, 16)
    t[0:3 + k, 0:3 + k] = int_tree_type
    t[3 + k:6 + k * 2, k] = int_tree_type + 1
    return t


@cache
def __volcano(volcano_w: int) -> np.ndarray[Any, Any]:
    # Function to generate a numpy volcano
    n_factor = volcano_w / 2
    volcano_h = ceil(n_factor)
    volcano = np.zeros((volcano_h, volcano_w))
    for i in range(volcano_h):
        volcano[floor(n_factor) - i, 0 + i:volcano_w - i] = 1
    volcano[volcano == 1] = np.random.choice([142, 143, 144, 145], p=[0.1, 0.5, 0.1, 0.3], size=volcano_h ** 2)
    return volcano


def __gen_empty_chunks(x_min: int, x_max: int, y_min: int, y_max: int) \
        -> Dict[Tuple[int, ...], Tuple[Tuple[int, ...], ...]]:
    # For generating empty chunks.
    world = {}
    for x in range(x_min, x_max, 16):
        for y in range(y_min, y_max, 16):
            world[(x + 16, x, y + 16, y)] = tuple(map(tuple, np.empty((16, 16), dtype=int)))
    return world


@cache
def __sky_gen() -> Tuple[Tuple[int, ...], ...]:
    # For generating the sky.
    sky = tuple(map(tuple, np.full((16, 16), 128)))
    clouds_co_ords = tuple(map(tuple, np.random.randint(16, size=(14, 2))))
    sky = __placer(4, 129, clouds_co_ords, sky)

    return sky


@cache
def __generate_upper_mine() -> Tuple[Tuple[int, ...], ...]:
    # For generating the upper part of the mine.
    mine = tuple(map(tuple, np.full((16, 16), 130)))

    dirt_co_ords = tuple(map(tuple, np.random.randint(16, size=(10, 2))))
    mine = __placer(randint(6, 8), 131, dirt_co_ords, mine)
    return mine


@cache
def __generate_middle_mine(y_max: int) -> Tuple[Tuple[int, ...], ...]:
    # For generating the main part of the mine
    mine = tuple(map(tuple, np.full((16, 16), 130)))

    coal_co_ords = tuple(map(tuple, np.random.randint(16, size=(7, 2))))
    iron_co_ords = tuple(map(tuple, np.random.randint(16, size=(4, 2))))
    diamond_co_ords = tuple(map(tuple, np.random.randint(16, size=(2, 2))))

    if -112 > y_max >= -128:
        mine = __placer(choices((6, 7, 8, 9, 10, 11, 12), (0.3, 0.3, 0.1, 0.1, 0.08, 0.09, 0.03), k=1)[0],
                        132, coal_co_ords, mine)
        mine = __placer(choices((4, 5, 6, 7, 8, 9, 10), (0.3, 0.3, 0.1, 0.1, 0.08, 0.09, 0.03), k=1)[0],
                        133, iron_co_ords, mine)
        mine = __placer(choices((2, 3, 4, 5, 6, 7, 8), (0.3, 0.3, 0.1, 0.1, 0.08, 0.09, 0.03), k=1)[0],
                        134, diamond_co_ords, mine)
    elif -32 >= y_max > -64:
        mine = __placer(choices((10, 11, 12, 13, 14, 15, 16), (0.3, 0.3, 0.1, 0.1, 0.08, 0.09, 0.03), k=1)[0],
                        132, coal_co_ords, mine)
        mine = __placer(choices((7, 8, 9, 10, 11, 12, 13), (0.3, 0.3, 0.1, 0.1, 0.08, 0.09, 0.03), k=1)[0],
                        133, iron_co_ords, mine)
    elif -64 > y_max >= -112:
        mine = __placer(choices((7, 8, 9, 10, 11, 12, 13), (0.3, 0.3, 0.1, 0.1, 0.08, 0.09, 0.03), k=1)[0],
                        132, coal_co_ords, mine)
        mine = __placer(choices((10, 11, 12, 13, 14, 15, 16), (0.3, 0.3, 0.1, 0.1, 0.08, 0.09, 0.03), k=1)[0],
                        133, iron_co_ords, mine)

    return mine


@cache
def __generate_lower_mine() -> Tuple[Tuple[int, ...], ...]:
    # For generating the lower part of the mine.
    mine = np.full((16, 16), 135)
    return tuple(map(tuple, mine))


@cache
def __gen_forest(y_max: int, tree_type: int) -> Tuple[Tuple[int, ...], ...]:
    # For generating forest biome.
    biome = np.full((16, 16), 128)

    if y_max >= 32:
        no_of_trees = randint(3, 4)
        for i in range(no_of_trees):
            biome[0:6, 2 + i * 3: 5 + i * 3] = __tree(tree_type)

    biome = tuple(map(tuple, biome))
    dirt_co_ords = tuple(map(tuple, np.random.randint(16, size=(10, 2))))
    if 32 > y_max >= 0:
        biome = __placer(9, 131, dirt_co_ords, biome)

    return biome


@cache
def __gen_plain(y_max: int) -> Tuple[Tuple[int, ...], ...]:
    # For generating plains biome.
    biome = tuple(map(tuple, np.full((16, 16), 128)))
    dirt_co_ords = tuple(map(tuple, np.random.randint(16, size=(10, 2))))
    if 32 > y_max >= 0:
        biome = __placer(9, 131, dirt_co_ords, biome)

    return biome


@cache
def __gen_desert(y_max: int) -> Tuple[Tuple[int, ...], ...]:
    # For generating desert biome.
    biome = np.full((16, 16), 128)

    if y_max >= 32:
        no_of_cactus = randint(3, 5)
        no_of_dead_bush = randint(2, 3)
        for i in range(no_of_cactus):
            biome[0:3, 0 + i * 3: 1 + i * 3] = 153
        for i in range(no_of_dead_bush):
            biome[0:1, 1 + i * 4:2 + i * 4] = 154

    biome = tuple(map(tuple, biome))
    burned_stone_co_ords = tuple(map(tuple, np.random.randint(16, size=(10, 2))))
    if 32 > y_max >= 0:
        biome = __placer(9, 147, burned_stone_co_ords, biome)

    return biome


@cache
def __gen_volcanoes(y_max: int) -> Tuple[Tuple[int, ...], ...]:
    # For generating volcanic biome.
    biome = np.full((16, 16), 128)

    if y_max >= 32:
        volcano_w = choice((9, 11, 13))
        biome[2:3 + floor(volcano_w / 2), 2:2 + volcano_w] = __volcano(volcano_w)

    biome = tuple(map(tuple, biome))
    burned_stone_co_ords = tuple(map(tuple, np.random.randint(16, size=(10, 2))))
    if 32 > y_max >= 0:
        biome = __placer(9, 147, burned_stone_co_ords, biome)

    return biome


@cache
def __gen_jungles(y_max: int, tree_type: int) -> Tuple[Tuple[int, ...], ...]:
    # For generating jungle biome.
    biome = np.full((16, 16), 128)

    if y_max >= 32:
        no_of_trees = randint(2, 3)
        for i in range(no_of_trees):
            biome[0:6, 0 + i * 5: 5 + i * 5] = __tree(tree_type, True)

    biome = tuple(map(tuple, biome))
    mossy_dirt_co_ords = tuple(map(tuple, np.random.randint(16, size=(10, 2))))
    if 32 > y_max >= 0:
        biome = __placer(9, 146, mossy_dirt_co_ords, biome)

    return biome


@cache
def __placer(range_: int, block_id: int, co_ords_arr: Tuple[Tuple[int, ...], ...], main: Tuple[Tuple[int, ...], ...]
             ) -> Tuple[Tuple[int, ...], ...]:
    # For adding chain of blocks to a chunk.
    co_ords_arr_ = deepcopy(co_ords_arr)
    main_arr = np.asarray(main)
    for co_ord_arr_ in co_ords_arr_:
        x_inc = 0
        y_inc = 0
        for _ in range(range_):
            to_be_inc = randint(0, 1)
            if to_be_inc == 1:
                x_inc += 1
            else:
                y_inc += 1

            if co_ord_arr_[0] + x_inc < 16 and co_ord_arr_[1] + y_inc < 16:
                main_arr[co_ord_arr_[1] + y_inc, co_ord_arr_[0] + x_inc] = block_id

            elif co_ord_arr_[0] + x_inc < 16 and co_ord_arr_[1] + y_inc > 15:
                main_arr[co_ord_arr_[1], co_ord_arr_[0] + x_inc] = block_id

            elif co_ord_arr_[0] + x_inc > 15 and co_ord_arr_[1] + y_inc < 16:
                main_arr[co_ord_arr_[1] + y_inc, co_ord_arr_[0]] = block_id

    return main


def gen_world(x_min: int = -192, x_max: int = 192, y_min: int = -160, y_max: int = 160
              ) -> Dict[Tuple[int, ...], Tuple[Tuple[int, ...], ...]]:
    """When called without any arguments it generates the initial world.
    Call with Arguments to generate or load more world.

    :param x_min: The x-axis point from where it has to generate the world.
    :param x_max: The x-axis point till where it will generate the world.
    :param y_min: The y-axis point from where it has to generate the world.
    :param y_max: The y-axis point till where it will generate the world.
    """
    world = __gen_empty_chunks(x_min, x_max, y_min, y_max)
    free_chunks_horizontal = 24
    no_of_biomes = randint(2, 4)
    tree_type = choice(('0x88', '0x8a', '0x8c', '0x8e'))
    jungle_tree_type = choice(('0x96', '0x94'))
    biomes_choices = [__gen_forest, __gen_plain, __gen_desert, __gen_volcanoes, __gen_jungles]
    biomes_nf = deque()
    biomes_area = deque()
    for _ in range(no_of_biomes):
        biome = choice(biomes_choices)
        if biome not in biomes_nf:
            biomes_nf.append(biome)
            biomes_area.append(int(free_chunks_horizontal / no_of_biomes) * 5)
        else:
            i = biomes_nf.index(biome)
            biomes_area[i] += int(free_chunks_horizontal / no_of_biomes) * 5

    biomes = dict(enumerate(zip(biomes_area, biomes_nf)))
    biomes: Dict[int, Tuple[int, Callable[..., np.ndarray]]]
    i = 0
    for co_ords, _ in world.items():
        # generating sky
        if co_ords[3] >= 80:
            world[co_ords] = __sky_gen()

        # generating upper mine
        elif 0 > co_ords[3] >= -32:
            world[co_ords] = __generate_upper_mine()

        # generating middle mine
        elif -32 > co_ords[3] >= -128:
            world[co_ords] = __generate_middle_mine(co_ords[3])

        # generating lower mine
        elif co_ords[3] <= -144:
            world[co_ords] = __generate_lower_mine()

        # generating biomes
        else:
            if biomes[i][0] != 0:
                if biomes[i][1] == __gen_forest:
                    world[co_ords] = biomes[i][1](co_ords[3], tree_type)
                elif biomes[i][1] == __gen_jungles:
                    world[co_ords] = biomes[i][1](co_ords[3], jungle_tree_type)
                else:
                    world[co_ords] = biomes[i][1](co_ords[3])

    return world
