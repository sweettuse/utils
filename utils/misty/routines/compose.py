import asyncio
from contextlib import suppress
from random import choice

import silly
from misty_py.utils import wait_in_order, wait_for_group, asyncpartial, wait_first, async_run
from more_itertools import always_iterable

from utils.colors.colors import Colors
from utils.misty.core import api
from utils.aio.core import cancel, repeat
from utils.misty.routines.audio import say, random_sound
from utils.misty.routines.images import flash, all_eyes, eyes
from utils.misty.routines.movement import move_head, move_arms, animate
from utils.misty.routines.text.base import bt

__author__ = 'acushner'


async def smooth_jazz():
    """smooth jazz will be deployed in 3...2...1..."""

    async def cancel(_g):
        with suppress(asyncio.CancelledError):
            _g.cancel()
            await _g

    p = asyncpartial(api.audio.play, blocking=True)

    await api.movement.move_head(0, 0, 0, velocity=40)
    await p('misc--smooth_jazz_will_be_deployed.mp3')
    g = asyncio.gather(move_head(velocity=100, roll_max=50), move_arms())
    coros = (
        wait_for_group(
            p('misc--smooth_jazz.mp3'),
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


async def party_mode(how_long_secs=15, eyes=eyes, music: str = None):
    await bt.party_time
    _music_options = ('sfx--studiopolis.mp3', 'music--gandalf_sax.mp3', 'vgm--best--messenger_howling_grotto.mp3',
                      'vgm--best--mk7_credits.mp3', 'music--price_is_right.mp3')
    music = choice(list(always_iterable(music)) or _music_options)
    print(music)
    play = asyncpartial(api.audio.play, music, blocking=True)
    async with api.movement.reset_to_orig():
        await wait_first(
            flash(Colors.values(), eyes, flashlight=True),
            repeat(play),
            move_arms(70, 70, 100),
            move_head(90, 90, 90, 80),
            asyncio.sleep(how_long_secs)
        )
    await api.images.display('e_DefaultContent.jpg')


async def lets_get_silly():
    adj = silly.sentence()
    print(adj)
    await say(adj)


async def lets_get_sweary():
    await asyncio.sleep(3)
    async with cancel(animate()):
        for _ in range(10):
            await bt.swears
            # await bt.emphatic


async def t_base():
    for _ in range(5):
        await bt.greeting


def __main():
    # async_run(smooth_jazz())
    # asyncio.run(party_mode(30))
    # async_run(lets_get_sweary())
    # import os
    # print(os.environ['MISTY_IP'])
    async_run(party_mode())
    # asyncio.run(talk('i am the jebtuse! how are you today?'))


if __name__ == '__main__':
    __main()
