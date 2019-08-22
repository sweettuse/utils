import asyncio
import os
from asyncio import wait_for
from contextlib import suppress, asynccontextmanager
from typing import Callable, Awaitable

from misty_py.api import MistyAPI, wait_in_order
from random import random

from misty_py.utils import asyncpartial, wait_for_group

__author__ = 'acushner'
api = MistyAPI()


def _get_random(v):
    return 2 * v * random() - v


async def _run_n(coro: Callable[[], Awaitable[None]], n_times, sleep_time=.4):
    """run coro `n_times`"""
    for _ in range(n_times):
        await coro()
        await asyncio.sleep(sleep_time)


async def move_head(pitch_max=20, roll_max=20, yaw_max=20, velocity=50, n_times=6):
    """move head randomly"""

    async def _move():
        await api.movement.move_head(pitch=_get_random(pitch_max), roll=_get_random(roll_max),
                                     yaw=_get_random(yaw_max), velocity=velocity)

    await _run_n(_move, n_times)


async def move_arms(l_max=50, r_max=50, velocity=60, n_times=6):
    """move arms randomly"""

    async def _move():
        await api.movement.move_arms(l_position=_get_random(l_max), r_position=_get_random(r_max), l_velocity=velocity,
                                     r_velocity=velocity)

    await _run_n(_move, n_times)


async def animate(n_times=100):
    async def _helper():
        async with api.movement.reset_to_orig():
            await wait_for_group(move_arms(n_times=n_times), move_head(n_times=n_times))
    return await _helper()


async def nod(pitch=40, roll=None, yaw=None, velocity=100, n_times=6):
    """have misty nod up and down"""

    async def _move():
        nonlocal pitch
        await api.movement.move_head(pitch=pitch, yaw=yaw, roll=roll, velocity=velocity)
        await asyncio.sleep(.2)
        pitch *= -1

    await _run_n(_move, n_times)
    await api.movement.move_head(pitch=0)


async def shake_head(pitch=None, roll=None, yaw=-40, velocity=100, n_times=6):
    """have misty shake head left and right"""

    async def _move():
        nonlocal yaw
        await api.movement.move_head(pitch=pitch, yaw=yaw, roll=roll, velocity=velocity)
        await asyncio.sleep(.2)
        yaw *= -1

    await _run_n(_move, n_times)
    await api.movement.move_head(yaw=0)


def __main():
    asyncio.run(move_arms())
    # asyncio.run(move_arms(n_times=10))
    # asyncio.run(asyncio.gather(*[move_head(velocity=100, roll_max=50, n_times=20), move_arms(n_times=20)]))


if __name__ == '__main__':
    __main()
