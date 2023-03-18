import dataclasses

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
