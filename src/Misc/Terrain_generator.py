import numpy as np

# sky = 128
# clouds = 129


def __gen_empty_chunks(x_min: int = -160, x_max: int = 160, y_min: int = -160, y_max: int = 160) -> dict:  # noqa 203
    world = {}
    for x in range(x_min, x_max, 16):
        for y in range(y_min, y_max, 16):
            world[(x + 16, x, y + 16, y)] = np.zeros((16, 16))
    return world


def __sky_gen():  # noqa 203
    sky = np.full((16, 16), 128)
    clouds_co_ords = np.random.randint(16, size=(16, 2))
    for cloud_co_ord in clouds_co_ords:
        sky[cloud_co_ord[0]][cloud_co_ord[1]] = 129
    return sky


def gen_world():  # noqa 201
    world = __gen_empty_chunks()
    for co_ords, chunk in world.items():
        if co_ords[3] >= 80:
            # if y max is greater than 80 we generate sky
            world[co_ords] = __sky_gen()

    return world


if __name__ == '__main__':
    print(gen_world())
