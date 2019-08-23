import asyncio
from typing import Union, List

from misty_py.utils import RGB, wait_first
from itertools import cycle
from more_itertools import always_iterable
from utils.colors.colors import Colors
from utils.misty.core import api

__author__ = 'acushner'
eyes = 'e_Joy.jpg e_Joy2.jpg e_JoyGoofy.jpg e_JoyGoofy2.jpg e_JoyGoofy3.jpg'.split()


async def flash(colors: Union[RGB, List[RGB]], images: Union[str, List[str]],
                on_time_secs=.1, off_time_secs=.02, flashlight=False):
    """rapidly change display image, led color, and flashlight"""

    async def _set(c, i, t, on_off, force=False):
        if t <= 0:
            return

        coros = [asyncio.sleep(t)]
        if c:
            print(c)
            coros.append(api.images.set_led(c))
        if i and (on_off or force):
            coros.append(api.images.display(i))
        if flashlight:
            coros.append(api.system.set_flashlight(on_off))
        await asyncio.gather(*coros)

    try:
        for c, i in zip(cycle(always_iterable(colors, base_type=tuple)), cycle(always_iterable(images))):
            await _set(c, i, on_time_secs, True)
            await _set(RGB(0, 0, 0), i, off_time_secs, False)
    finally:
        print('in finally')
        await _set(RGB(0, 0, 0), 'e_DefaultContent.jpg', off_time_secs, False, True)


def __main():
    asyncio.run(flash(Colors.values(), eyes, on_time_secs=.05, off_time_secs=.02, total_time=10, flashlight=False))


if __name__ == '__main__':
    __main()
