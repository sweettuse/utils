import asyncio
import os
from contextlib import suppress
from random import choice, random
from typing import Callable, Awaitable

import arrow
from misty_py.misty_ws import UnchangedValue, EventCallback
from misty_py.subscriptions import Actuator
from misty_py.utils import wait_first, asyncpartial, wait_for_group, wait_in_order

from utils.misty.core import api

__author__ = 'acushner'


async def wave(l_or_r: str = 'r', position=60, velocity=60, n_times=6):
    positions = position, 0
    for i in range(n_times):
        kwargs = {f'{l_or_r}_position': position, f'{l_or_r}_velocity': velocity}
        await api.movement.move_arms(**kwargs)
        await asyncio.sleep(.4)
        position = positions[i & 1]
    await api.movement.move_arms(l_position=0, r_position=0, l_velocity=velocity, r_velocity=velocity)


async def wave2(l_or_r: str = 'l', position=120, velocity=60, n_times=8):
    positions = position, 0
    uv = UnchangedValue(5, debug=True)
    ecb = EventCallback(uv)
    async with api.ws.sub_unsub(Actuator.left_arm, ecb, 10):
        for i in range(n_times):
            position = positions[i & 1]
            kwargs = {f'{l_or_r}_position': position, f'{l_or_r}_velocity': velocity}
            await api.movement.move_arms(**kwargs)
            ecb.clear()
            uv.clear()
            await ecb
            print(position)
    await api.movement.move_arms(l_position=0, r_position=0, l_velocity=velocity, r_velocity=velocity)


async def wait_play():
    coros = (asyncio.sleep(n) for n in range(1, 100))
    d, p = await wait_first(*coros)
    print(type(d), d)
    print(len(p))


def _get_random(v):
    return 2 * v * random() - v


async def eyes_wont_set():
    pos = 80
    await asyncio.gather(
        api.images.display('e_Sleeping.jpg'),
        api.movement.move_head(pos, velocity=20),
    )
    await asyncio.sleep(2)
    await api.images.display('e_DefaultContent.jpg')


def __main():
    pass


if __name__ == '__main__':
    __main()
