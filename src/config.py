SPRITE_SCALING = 0.5
INVENTORY_SCALING = SPRITE_SCALING * 6
PLAYER_SCALING = 0.75

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 700
SCREEN_TITLE = "<placeholder>"
SPRITE_PIXEL_SIZE = 20
ICON_SIZE = 16
GRID_PIXEL_SIZE = (SPRITE_PIXEL_SIZE * SPRITE_SCALING)

VIEWPORT_MARGIN = SPRITE_PIXEL_SIZE * SPRITE_SCALING
RIGHT_MARGIN = 4 * SPRITE_PIXEL_SIZE * SPRITE_SCALING

MOVEMENT_SPEED = 10 * SPRITE_SCALING
JUMP_SPEED = 48 * SPRITE_SCALING
GRAVITY = 2 * SPRITE_SCALING

MAX_SLOTS = 10
MAX_STACK = 64
VISIBLE_RANGE_MAX = int((2 * SPRITE_PIXEL_SIZE) / SPRITE_SCALING)
VISIBLE_RANGE_MIN = int((-2 * SPRITE_PIXEL_SIZE) / SPRITE_SCALING)
