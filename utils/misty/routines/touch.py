import asyncio
from random import choice
from typing import NamedTuple

from misty_py.subscriptions import SubType, Touch, SubPayload, LLSubType
from misty_py.utils import async_run

from utils.misty.core import api
from utils.misty.routines.audio import random_sound, Mood, random_simpsons_quote

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


async def _handle_response(sp: SubPayload):
    """crude but kinda endearing way of having misty respond to touch"""
    resp = touch_response.get(LLSubType.from_sub_payload(sp))
    moods = Mood.amazement, Mood.acceptance, Mood.love, Mood.joy
    if not resp:
        return
    await api.movement.move_head(**(resp * 30).kwargs, velocity=100, increment=True),
    await asyncio.gather(
        api.images.display('e_Joy.jpg'),
        random_sound(choice(moods)),
        asyncio.sleep(2)
    )


async def respond_to_touch():
    async with api.movement.reset_to_orig(), api.ws.sub_unsub(SubType.touch_sensor, _handle_response, 250):
        await asyncio.sleep(999)
    await api.images.display('e_DefaultContent.jpg')


async def touch_simpsons_quote():
    t: asyncio.Task = None

    async def _on_response(sp: SubPayload):
        nonlocal t
        print(sp)
        if t:
            return

        t = asyncio.create_task(random_simpsons_quote())
        await t
        t = None

    try:
        async with api.ws.sub_unsub(SubType.bump_sensor, _on_response):
            await asyncio.sleep(999)
    except asyncio.CancelledError:
        pass


def __main():
    async_run(respond_to_touch())


if __name__ == '__main__':
    __main()
