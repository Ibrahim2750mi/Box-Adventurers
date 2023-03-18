import dataclasses
from pathlib import Path

ASSET_DIR = (Path(__file__).parent.parent / "assets").resolve()
DATA_DIR = (Path(__file__).parent.parent / "data").resolve()

MAX_SLOTS = 10

SPRITE_SCALING = 1.0
INVENTORY_SCALING = (3/11) * MAX_SLOTS
PLAYER_SCALING = 1.0

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Box Adventures"
SPRITE_PIXEL_SIZE = 20
ICON_SIZE = 16
GRID_PIXEL_SIZE = (SPRITE_PIXEL_SIZE * SPRITE_SCALING)

VIEWPORT_MARGIN = SPRITE_PIXEL_SIZE * SPRITE_SCALING
RIGHT_MARGIN = 4 * SPRITE_PIXEL_SIZE * SPRITE_SCALING

MOVEMENT_SPEED = 5 * SPRITE_SCALING
JUMP_SPEED = 24 * SPRITE_SCALING
GRAVITY = 1 * SPRITE_SCALING
PLAYER_BLOCK_REACH = 100 * PLAYER_SCALING  # 100 pixel reach to block

MAX_STACK = 99

MUSIC = False

CHUNK_WIDTH = 16
CHUNK_HEIGHT = 320

VISIBLE_RANGE_MAX = int((2.5 * CHUNK_WIDTH) / SPRITE_SCALING)
VISIBLE_RANGE_MIN = int((-2.5 * CHUNK_WIDTH) / SPRITE_SCALING)

CHUNK_WIDTH_PIXELS = SPRITE_PIXEL_SIZE * CHUNK_WIDTH
CHUNK_HEIGHT_PIXELS = SPRITE_PIXEL_SIZE * CHUNK_HEIGHT

HEIGHT_MIN = 0

@dataclasses.dataclass
class BlockConstants:
    sky = 128
    clouds = 129
    stone = 130
    dirt = 131
    coal = 132
    iron = 133
    diamond = 134
    hard_stone = 135
    oak_leaf = 136
    oak_log = 137
    timber_leaf = 138
    timber_log = 139
    teak_leaf = 140
    teak_log = 141
    pumice = 142
    basalt = 143
    obsidian = 144
    molten_rock = 145
    burned_stone = 146
    mossy_dirt = 147
    mahagoni_leaf = 148
    mahagoni_log = 149
    mangrove_leaf = 150
    mangrove_log = 151
    sand = 152
    cactus = 153
    dead_bush = 154
    grass = 155

@dataclasses.dataclass
class BiomeConstants:
    sky = 1
    upper_mine = 2
    middle_mine_1 = 3
    middle_mine_2 = 4
    middle_mine_3 = 5
    lower_mine = 6
    forest_sky = 7
    forest_floor = 8
    forest = 9
    plains_sky = 10
    plains_floor = 11
    plains = 12
    desert_sky = 13
    desert_floor = 14
    desert = 15
    volcanic_sky = 16
    volcanic_floor = 17
    volcano = 18
    jungle_sky = 19
    jungle_floor = 20
    jungle = 21