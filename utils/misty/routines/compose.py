import asyncio
from contextlib import suppress

from misty_py.utils import wait_in_order, wait_for_group, asyncpartial, wait_first, async_run

from utils.colors.colors import Colors
from utils.misty.core import api, repeat
from utils.misty.routines.audio import say, random_sound
from utils.misty.routines.images import flash
from utils.misty.routines.movement import move_head, move_arms, animate

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


async def talk(s):
    t = await say(s, animate(10000))
    t.cancel()


async def go_ham(how_long_secs=3):
    eyes = 'e_Joy.jpg e_Joy2.jpg e_JoyGoofy.jpg e_JoyGoofy2.jpg e_JoyGoofy3.jpg'.split()
    async with api.movement.reset_to_orig():
        await wait_first(
            flash(Colors.values(), eyes, flashlight=True),
            repeat(random_sound),
            move_arms(70, 70, 100, 10000),
            move_head(90, 90, 90, 80, 100000),
            asyncio.sleep(how_long_secs)
        )


def __main():
    async_run(go_ham(6))
    # asyncio.run(talk('i am the jebtuse! how are you today?'))


if __name__ == '__main__':
    __main()
