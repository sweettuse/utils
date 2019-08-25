import asyncio
from contextlib import suppress

import silly
from misty_py.utils import wait_in_order, wait_for_group, asyncpartial, wait_first, async_run

from utils.colors.colors import Colors
from utils.misty.core import api, repeat, cancel
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
    await p('smooth_jazz_will_be_deployed.mp3')
    g = asyncio.gather(move_head(velocity=100, roll_max=50), move_arms())
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


async def talk(s):
    async with cancel(animate()):
        await say(s)


async def party_mode(how_long_secs=3, eyes=eyes, music='gandalf_sax.mp3'):
    play = asyncpartial(api.audio.play, music, blocking=True)
    async with api.movement.reset_to_orig():
        await wait_first(
            flash(Colors.values(), eyes, flashlight=True),
            repeat(play),
            move_arms(70, 70, 100),
            move_head(90, 90, 90, 80),
            asyncio.sleep(how_long_secs)
        )


async def lets_get_silly():
    adj = silly.paragraph()
    print(adj)
    await talk(adj)


async def lets_get_sweary():
    await asyncio.sleep(3)
    async with cancel(animate()):
        for _ in range(10):
            await bt.swears
            # await bt.emphatic


async def play():
    async with cancel(animate(2)):
        await asyncio.sleep(5)


def __main():
    # async_run(smooth_jazz())
    async_run(party_mode(10))
    # async_run(lets_get_sweary())
    # asyncio.run(talk('i am the jebtuse! how are you today?'))


if __name__ == '__main__':
    __main()
