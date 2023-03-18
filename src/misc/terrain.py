from collections import deque
from collections.abc import Callable
from functools import cache
from math import ceil, floor
from random import choice, choices, randint
from typing import Deque, Dict, Tuple

import numpy as np

import config
from utils import TArray
from constants import BiomeConstants, BlockConstants


@cache
def _tree(tree_type: int, jungle: bool = False) -> np.ndarray:
    # Function to generate a numpy tree.
    if jungle:
        k = 2
        t = np.zeros((10, 5))
    else:
        k = 0
        t = np.zeros((6, 3))

    t[0:3 + k, 0:3 + k] = tree_type
    t[3 + k:6 + k * 2, int(k / 2) + 1] = tree_type + 1
    t[t == 0] = BlockConstants.sky
    return t


def _volcano(volcano_w: int) -> np.ndarray:
    # Function to generate a numpy volcano
    n_factor = volcano_w / 2
    volcano_h = ceil(n_factor)
    volcano = np.zeros((volcano_h, volcano_w))
    for i in range(volcano_h):
        volcano[floor(n_factor) - i, 0 + i:volcano_w - i] = BiomeConstants.sky
    volcano[volcano == 1] = np.random.choice([BlockConstants.pumice, BlockConstants.basalt, BlockConstants.obsidian, BlockConstants.molten_rock], p=[0.1, 0.5, 0.1, 0.3], size=volcano_h ** 2)
    volcano[volcano == 0] = 128
    return volcano


def _gen_empty_chunks(x_min: int, x_max: int, y_min: int, y_max: int) \
        -> Dict[Tuple[int, ...], TArray]:
    # For generating empty chunks.
    empty_world = {}
    for x in range(x_min, x_max, 16):
        for y in range(y_min, y_max, 16):
            empty_world[(x + 16, x, y + 16, y)] = TArray(np.empty((16, 16), dtype=int))
    return empty_world


def _sky_gen(y_max: int = None) -> TArray:
    # For generating the sky.
    y_max = config.HEIGHT_MIN + 320
    sky = TArray(np.full((16, 16), 128))
    clouds_co_ords = np.random.randint(16, size=(14, 2))
    sky = _placer(4, BlockConstants.clouds, clouds_co_ords, sky)
    sky.adv_info[(y_max, y_max - 80)] = BiomeConstants.sky
    return sky


def _generate_upper_mine() -> TArray:
    # For generating the upper part of the mine.
    y_max = config.HEIGHT_MIN + 320
    mine = TArray(np.full((16, 16), BlockConstants.stone), 2)

    dirt_co_ords = np.random.randint(16, size=(10, 2))
    mine = _placer(randint(6, 8), BlockConstants.dirt, dirt_co_ords, mine)
    mine.adv_info[(y_max - 160, y_max - 192)] = BiomeConstants.upper_mine
    return mine


def _generate_middle_mine(y: int, biome_code: int = None) -> TArray:
    # For generating the main part of the mine
    y_max = config.HEIGHT_MIN + 320
    mine = TArray(np.full((16, 16), BlockConstants.stone))
    coal_co_ords = np.random.randint(16, size=(7, 2))
    iron_co_ords = np.random.randint(16, size=(4, 2))
    diamond_co_ords = np.random.randint(16, size=(2, 2))

    if y_max - 272 > y >= y_max - 288 or biome_code == 5:
        mine = _placer(choices((6, 7, 8, 9, 10, 11, 12), (0.3, 0.3, 0.1, 0.1, 0.08, 0.09, 0.03), k=1)[0],
                        BlockConstants.coal, coal_co_ords, mine)
        mine = _placer(choices((4, 5, 6, 7, 8, 9, 10), (0.3, 0.3, 0.1, 0.1, 0.08, 0.09, 0.03), k=1)[0],
                        BlockConstants.iron, iron_co_ords, mine)
        mine = _placer(choices((2, 3, 4, 5, 6, 7, 8), (0.3, 0.3, 0.1, 0.1, 0.08, 0.09, 0.03), k=1)[0],
                        BlockConstants.diamond, diamond_co_ords, mine)

        mine.adv_info[(y_max - 272, y_max - 288)] = BiomeConstants.middle_mine_3

    elif y_max - 192 >= y > y_max - 224 or biome_code == 3:
        mine = _placer(choices((10, 11, 12, 13, 14, 15, 16), (0.3, 0.3, 0.1, 0.1, 0.08, 0.09, 0.03), k=1)[0],
                        BlockConstants.coal, coal_co_ords, mine)
        mine = _placer(choices((7, 8, 9, 10, 11, 12, 13), (0.3, 0.3, 0.1, 0.1, 0.08, 0.09, 0.03), k=1)[0],
                        BlockConstants.iron, iron_co_ords, mine)

        mine.adv_info[(y_max - 192, y_max - 224)] = BiomeConstants.middle_mine_1

    elif y_max - 224 >= y >= y_max - 272 or biome_code == 4:
        mine = _placer(choices((7, 8, 9, 10, 11, 12, 13), (0.3, 0.3, 0.1, 0.1, 0.08, 0.09, 0.03), k=1)[0],
                        BlockConstants.coal, coal_co_ords, mine)
        mine = _placer(choices((10, 11, 12, 13, 14, 15, 16), (0.3, 0.3, 0.1, 0.1, 0.08, 0.09, 0.03), k=1)[0],
                        BlockConstants.iron, iron_co_ords, mine)
        mine.adv_info[(y_max - 224, y_max - 272)] = BiomeConstants.middle_mine_2

    return mine


def _generate_lower_mine(y_min: int) -> TArray:
    mine = TArray(np.full((16, 16), BlockConstants.hard_stone))
    mine.adv_info[(y_min + 16, y_min)] = BiomeConstants.lower_mine
    return mine


def _gen_forest(y: int, biome_code: int = None) -> TArray:
    # For generating forest biome.
    y_max = config.HEIGHT_MIN + 320
    tree_type = choice((BlockConstants.oak_leaf, BlockConstants.timber_leaf, BlockConstants.teak_leaf))
    if y_max - 128 > y >= y_max - 160 or biome_code == 8:
        biome = TArray(np.full((16, 16), BlockConstants.dirt))
        biome.adv_info[(y_max - 128, y_max - 160)] = BiomeConstants.forest_floor
    else:
        biome = TArray(np.full((16, 16), 128))
        biome.adv_info[(y_max - 80, y_max - 128)] = BiomeConstants.forest_sky

    if y_max - 128 >= y > y_max - BlockConstants.obsidian or biome_code == 9:
        no_of_trees = randint(2, 3)
        for i in range(no_of_trees):
            biome[10:16, i + 2 + i * 3: i + 5 + i * 3] = _tree(tree_type)
        biome.adv_info[(y_max - 128, y_max - BlockConstants.obsidian)] = BiomeConstants.forest

    return biome


def _gen_plain(y: int, biome_code: int = None) -> TArray:
    # For generating plains biome.
    y_max = config.HEIGHT_MIN + 320
    if y_max - 128 > y >= y_max - 160 or biome_code == 1:
        biome = TArray(np.full((16, 16), BlockConstants.dirt))
        biome.adv_info[(y_max - 128, y_max - 160)] = BiomeConstants.plains_floor
        if y == y_max - BlockConstants.obsidian or biome_code == 12:
            biome.adv_info[(y_max - BlockConstants.obsidian, y_max - BlockConstants.obsidian)] = BiomeConstants.plains
            biome[0, :] = BlockConstants.grass
    else:
        biome = TArray(np.full((16, 16), 128))
        biome.adv_info[(y_max - 80, y_max - 128)] = BiomeConstants.plains_sky

    return biome


def _gen_desert(y: int, biome_code: int = None) -> TArray:
    # For generating desert biome.
    y_max = config.HEIGHT_MIN + 320
    if y_max - 128 > y >= y_max - 160 or biome_code == 14:
        biome = TArray(np.full((16, 16), BlockConstants.sand))
        biome.adv_info[(y_max - 128, y_max - 160)] = BiomeConstants.desert_floor
    else:
        biome = TArray(np.full((16, 16), 128))
        biome.adv_info[(y_max - 80, y_max - 128)] = BiomeConstants.desert_sky

    if y_max - 128 >= y > y_max - BlockConstants.obsidian or biome_code == 15:
        no_of_cactus = randint(1, 5)
        no_of_dead_bush = randint(2, 3)
        for i in range(no_of_dead_bush):
            biome[15:16, 1 + i * 4:2 + i * 4] = BlockConstants.dead_bush
        for i in range(no_of_cactus):
            biome[13:16, 0 + i * 3: 1 + i * 3] = BlockConstants.cactus
        biome.adv_info[(y_max - 128, y_max - BlockConstants.obsidian)] = BiomeConstants.desert

    return biome


def _gen_volcanoes(y: int, biome_code: int = None) -> TArray:
    # For generating volcanic biome.
    y_max = config.HEIGHT_MIN + 320
    if y_max - 128 > y >= y_max - 160 or biome_code == 17:
        biome = TArray(np.full((16, 16), BlockConstants.burned_stone))
        biome.adv_info[(y_max - 128, y_max - 160)] = BiomeConstants.volcanic_floor
    else:
        biome = TArray(np.full((16, 16), 128))
        biome.adv_info[(y_max - 80, y_max - 128)] = BiomeConstants.volcanic_sky

    if y_max - 128 >= y > y_max - BlockConstants.obsidian or biome_code == 18:
        volcano_w = choice((9, 11, 13))
        biome[16 - floor(volcano_w / 2) - 1:16, 2:2 + volcano_w] = _volcano(volcano_w)
        biome.adv_info[(y_max - 128, y_max - BlockConstants.obsidian)] = BiomeConstants.volcano

    return biome


def _gen_jungles(y: int, biome_code: int = None) -> TArray:
    # For generating jungle biome.
    y_max = config.HEIGHT_MIN + 320
    jungle_tree_type = choice((BlockConstants.mangrove_leaf, BlockConstants.mahagoni_leaf))

    if y_max - 128 > y >= y_max - 160 or biome_code == 20:
        biome = TArray(np.full((16, 16), BlockConstants.mossy_dirt))
        biome.adv_info[(y_max - 128, y_max - 160)] = BiomeConstants.jungle_floor

    else:
        biome = TArray(np.full((16, 16), 128))
        biome.adv_info[(y_max - 80, y_max - 128)] = BiomeConstants.jungle_sky

    if y_max - 128 >= y > y_max - BlockConstants.obsidian or biome_code == 21:
        no_of_trees = randint(1, 2)
        for i in range(no_of_trees):
            biome[6:16, i + i * 5: i + 5 + i * 5] = _tree(jungle_tree_type, True)
        biome.adv_info[(y_max - 128, y_max - BlockConstants.obsidian)] = BiomeConstants.jungle
    return biome


def _placer(range_: int, block_id: int, co_ords_arr: TArray,
             main: TArray
             ) -> TArray:
    # For adding chain of blocks to a chunk.
    main_arr = main.arr
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
                main_arr[co_ord_arr[1] + y_inc, co_ord_arr[0] + x_inc] = block_id

            elif co_ord_arr[0] + x_inc < 16 and co_ord_arr[1] + y_inc > 15:
                main_arr[co_ord_arr[1], co_ord_arr[0] + x_inc] = block_id

            elif co_ord_arr[0] + x_inc > 15 and co_ord_arr[1] + y_inc < 16:
                main_arr[co_ord_arr[1] + y_inc, co_ord_arr[0]] = block_id
    main.arr = main_arr
    return main


def gen_world(x_min: int = -192, x_max: int = 192, y_min: int = -160, y_max: int = 160
              ) -> Dict[Tuple[int, ...], TArray]:
    """When called without any arguments it generates the initial world.
    Call with Arguments to generate or load more world. Also please keep the difference of y_min and y_max 320.
    :param x_min: The x-axis point from where it has to generate the world.
    :param x_max: The x-axis point till where it will generate the world.
    :param y_min: The y-axis point from where it has to generate the world.
    :param y_max: The y-axis point till where it will generate the world.
    """
    world = _gen_empty_chunks(x_min, x_max, y_min, y_max)
    free_chunks_horizontal = int((abs(x_min) + abs(x_max)) / 16)
    no_of_biomes = randint(2, 4)
    biomes_choices = [_gen_forest, _gen_plain, _gen_desert, _gen_volcanoes, _gen_jungles]
    biomes_nf = deque()
    biomes_area = deque()
    for _ in range(no_of_biomes):
        biome = choice(biomes_choices)
        if biome not in biomes_nf:
            biomes_nf.append(biome)
            biomes_area.append(int(free_chunks_horizontal / no_of_biomes) * 5)
        else:
            i = biomes_nf.index(biome)
            biomes_area[i] += int(free_chunks_horizontal / no_of_biomes) * BiomeConstants.middle_mine_3

    biomes = dict(enumerate([deque(elem) for elem in zip(biomes_area, biomes_nf)]))
    biomes: Dict[int, Deque[int, Callable[[int], int]], TArray]
    i = 0
    for co_ords, _ in world.items():
        # generating sky
        if co_ords[3] >= y_max - 80:
            world[co_ords] = _sky_gen()

        # generating upper mine
        elif y_max - 160 > co_ords[3] >= y_max - 192:
            world[co_ords] = _generate_upper_mine()

        # generating middle mine
        elif y_max - 192 > co_ords[3] >= y_max - 288:
            world[co_ords] = _generate_middle_mine(co_ords[3])

        # generating lower mine
        elif co_ords[3] <= y_min + 16:
            world[co_ords] = _generate_lower_mine(y_min)

        # generating biomes
        else:
            if biomes[i][0] != 0:
                pass
            else:
                if len(biomes) - 1 > i:
                    i += 1

            biome_gen: Callable[[int], int] = biomes[i][1]
            # biomes[i][1]: Callable[[int, int], TArray]

            if biomes[i][1] == _gen_forest:
                world[co_ords] = biome_gen(co_ords[3])
            elif biomes[i][1] == _gen_jungles:
                world[co_ords] = biome_gen(co_ords[3])
            else:
                world[co_ords] = biome_gen(co_ords[3])
            biomes[i][0] -= 1

    return world


def gen_chunk(y: int, biome_code: int):
    biomes = [_gen_forest, _gen_plain, _gen_desert, _gen_volcanoes, _gen_jungles]
    if biome_code / 3 - 2 > 0:
        return biomes[biome_code // 3 - 2](y, biome_code=biome_code)
    else:
        biomes = [_sky_gen, _generate_upper_mine, _generate_lower_mine]
        if biome_code in (3, 4, 5):
            return _generate_middle_mine(y, biome_code=biome_code)
        elif biome_code == 6:
            return biomes[2](config.HEIGHT_MIN)
        else:
            return biomes[biome_code - 1](config.HEIGHT_MIN + 320)

if __name__ == '__main__':
    generated_world = gen_world(-496, 496)
    with open("world.npy", "wb") as f:
        np.save(f, generated_world, allow_pickle=True)
