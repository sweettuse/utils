import asyncio

from misty_py.api import MistyAPI
from random import random

__author__ = 'acushner'
api = MistyAPI()


async def move(pitch_max=20, roll_max=20, yaw_max=20, velocity=50, n_times=6):
    def _get_random(v):
        return 2 * v * random() - v

    for _ in range(n_times):
        await api.movement.move_head(pitch=_get_random(pitch_max), roll=_get_random(roll_max), yaw=_get_random(yaw_max),
                                     velocity=velocity)
        await asyncio.sleep(.4)


async def play():
    pass


def __main():
    asyncio.run(move(velocity=100, roll_max=50, n_times=20))


if __name__ == '__main__':
    __main()
