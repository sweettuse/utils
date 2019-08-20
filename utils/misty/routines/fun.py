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


async def random_simpsons_quote():
    fn = f'simpsons_{choice(range(1, 101))}.mp3'
    print(fn)
    await api.audio.play(fn)


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


async def _run_n(coro: Callable[[], Awaitable[None]], n_times, sleep_time=.4):
    for _ in range(n_times):
        await coro()
        await asyncio.sleep(sleep_time)


async def move_head(pitch_max=20, roll_max=20, yaw_max=20, velocity=50, n_times=6):
    async def _move():
        await api.movement.move_head(pitch=_get_random(pitch_max), roll=_get_random(roll_max),
                                     yaw=_get_random(yaw_max), velocity=velocity)

    await _run_n(_move, n_times)


async def move_arms(l_max=50, r_max=50, velocity=60, n_times=6):
    async def _move():
        await api.movement.move_arms(l_position=_get_random(l_max), r_position=_get_random(r_max), l_velocity=velocity,
                                     r_velocity=velocity)

    await _run_n(_move, n_times)


async def smooth_jazz():
    """smooth jazz will be deployed in 3...2...1..."""

    async def cancel(_g):
        with suppress(asyncio.CancelledError):
            _g.cancel()
            await _g

    p = asyncpartial(api.audio.play, blocking=True)

    await api.movement.move_head(0, 0, 0, velocity=40)
    await p('smooth_jazz_will_be_deployed.mp3')
    g = asyncio.gather(move_head(velocity=100, roll_max=50, n_times=100), move_arms(n_times=100))
    coros = (
        wait_for_group(
            p('smooth_jazz.mp3'),
            api.images.display('e_Love.jpg'),
            wait_in_order(
                asyncio.sleep(8.5),
                cancel(g),
                api.images.display('e_Sleeping.jpg'),
                wait_for_group(
                    api.movement.move_head(-100, velocity=4),
                    api.movement.move_arms(l_position=-80, r_position=-80, l_velocity=30, r_velocity=4),
                ),
            ),
        ),
        asyncio.sleep(4),
        api.images.display('e_DefaultContent.jpg'),
    )

    return await wait_in_order(*coros)


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
