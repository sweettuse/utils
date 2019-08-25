import asyncio
from typing import NamedTuple

from misty_py.subscriptions import SubType, Touch, SubPayload, LLSubType
from misty_py.utils import async_run

from utils.misty.core import api
from utils.misty.routines.audio import random_sound, Mood

__author__ = 'acushner'


class PRY(NamedTuple):
    pitch: int = 0
    roll: int = 0
    yaw: int = 0

    @property
    def kwargs(self):
        return self._asdict()

    def __mul__(self, other):
        return PRY(*(other * v for v in self))

    def __rmul__(self, other):
        return self * other


touch_response = {
    Touch.chin: PRY(pitch=-1),
    Touch.chin_left: PRY(-1, 1, -1),
    Touch.chin_right: PRY(-1, -1, 1),
    Touch.head_back: PRY(pitch=1),
    Touch.head_front: PRY(pitch=-1),
    Touch.head_left: PRY(1, -1, -1),
    Touch.head_right: PRY(1, 1, 1),
    Touch.head_top: PRY(),
    Touch.scruff: PRY(-4, -4, -4),
}


async def respond_to_touch(sp: SubPayload):
    """crude but kinda endearing way of having misty respond to touch"""
    resp = touch_response.get(LLSubType.from_sub_payload(sp))
    if not resp:
        return
    await api.movement.move_head(**(resp * 30).kwargs, velocity=100, increment=True),
    await asyncio.gather(
        api.images.display('e_Joy.jpg'),
        random_sound(Mood.excited),
        asyncio.sleep(2)
    )


async def play():
    async with api.movement.reset_to_orig(), api.ws.sub_unsub(SubType.touch_sensor, respond_to_touch, 10000):
        await asyncio.sleep(30)
    await api.images.display('e_DefaultContent.jpg')


def __main():
    async_run(play())


if __name__ == '__main__':
    __main()
