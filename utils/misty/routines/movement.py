import asyncio
import random
from asyncio import wait_for
from itertools import count
from typing import Callable, Awaitable, NamedTuple

from misty_py.api import MistyAPI
from misty_py.misty_ws import EventCBUnchanged
from misty_py.subscriptions import Actuator
from misty_py.utils import wait_for_group

__author__ = 'acushner'

__all__ = 'move_head move_arms search animate nod shake_head search'.split()

api = MistyAPI()


def _get_random(v):
    return 2 * v * random.random() - v


async def _run_n(coro: Callable[[], Awaitable[None]], n_times=0, sleep_time=.4):
    """run coro `n_times` or forever"""
    r = count() if n_times <= 0 else range(n_times)
    for _ in r:
        await asyncio.gather(
            coro(),
            asyncio.sleep(sleep_time)
        )


async def move_head(pitch_max=20, roll_max=20, yaw_max=20, velocity=50):
    """move head randomly forever (until canceled)"""

    async def _move():
        await api.movement.move_head(pitch=_get_random(pitch_max), roll=_get_random(roll_max),
                                     yaw=_get_random(yaw_max), velocity=velocity)

    await _run_n(_move)


async def move_arms(l_max=50, r_max=50, velocity=60):
    """move arms randomly forever (until canceled)"""

    async def _move():
        largs = dict(l_position=_get_random(l_max), l_velocity=velocity)
        rargs = dict(r_position=_get_random(r_max), r_velocity=velocity)
        await api.movement.move_arms(**largs)
        await api.movement.move_arms(**rargs)

    await _run_n(_move)


class MoveHead(NamedTuple):
    mult: float = 1.0
    velocity: int = 50
    pitch_max: int = 20
    roll_max: int = 20
    yaw_max: int = 20

    @property
    def kwargs(self):
        d = self._asdict()
        res = {}
        mult, vel = d.pop('mult'), d.pop('velocity')
        res['velocity'] = vel
        res.update((k, mult * v) for k, v in d.items())
        print(res)
        return res


class MoveArms(NamedTuple):
    mult: float = 1.0
    l_max: int = 20
    r_max: int = 20
    velocity: int = 60

    @property
    def kwargs(self):
        d = self._asdict()
        res = {}
        mult, vel = d.pop('mult'), d.pop('velocity')
        res['velocity'] = vel
        res.update((k, mult * v) for k, v in d.items())
        return res


async def search(pitch_min=0, pitch_max=15, yaw_min=-100, yaw_max=100, velocity=30, do_reset=True):
    """have misty look around forever. good for searching for faces to recognize."""
    cb = EventCBUnchanged(2)
    async with api.movement.reset_to_orig(ignore=not do_reset), api.ws.sub_unsub(Actuator.yaw, cb):
        yaws = yaw_min, yaw_max
        cur = 0
        while True:
            cur += 1
            cur &= 1
            y = yaws[cur]
            p = random.choice(range(pitch_min, pitch_max + 1))
            print('pitch, yay, vel', p, y, velocity)
            await asyncio.gather(
                api.movement.move_head(pitch=p, yaw=y, velocity=velocity),
                cb
            )
            cb.clear()


async def animate(mult=1.0):
    async with api.movement.reset_to_orig(velocity=100):
        await wait_for_group(move_arms(**MoveArms(mult).kwargs), move_head(**MoveHead(mult).kwargs))


async def nod(pitch=40, roll=None, yaw=None, velocity=100, n_times=9):
    """have misty nod up and down"""

    async with api.movement.reset_to_orig():
        async def _move():
            nonlocal pitch
            await api.movement.move_head(pitch=pitch, yaw=yaw, roll=roll, velocity=velocity)
            await asyncio.sleep(.2)
            pitch *= -1

        await _run_n(_move, n_times)


async def shake_head(pitch=None, roll=None, yaw=-40, velocity=100, n_times=6):
    """have misty shake head left and right"""

    async with api.movement.reset_to_orig():
        async def _move():
            nonlocal yaw
            await api.movement.move_head(pitch=pitch, yaw=yaw, roll=roll, velocity=velocity)
            await asyncio.sleep(.2)
            yaw *= -1

        await _run_n(_move, n_times)


def __main():
    asyncio.run(wait_for(search(pitch_min=10, pitch_max=40, velocity=60), 20))
    # asyncio.run(wait_for(animate(2), 4))
    # asyncio.run(move_arms(n_times=10))
    # asyncio.run(asyncio.gather(*[move_head(velocity=100, roll_max=50, n_times=20), move_arms(n_times=20)]))


if __name__ == '__main__':
    __main()
