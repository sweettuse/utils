import asyncio
from typing import Union, List

from misty_py.utils import RGB, wait_first
from itertools import cycle
from more_itertools import always_iterable
from utils.colors.colors import Colors
from utils.misty.core import api

__author__ = 'acushner'
eyes = 'e_Joy.jpg e_Joy2.jpg e_JoyGoofy.jpg e_JoyGoofy2.jpg e_JoyGoofy3.jpg'.split()
all_eyes = ['e_Admiration.jpg', 'e_Aggressiveness.jpg', 'e_Amazement.jpg', 'e_Anger.jpg', 'e_ApprehensionConcerned.jpg',
            'e_Contempt.jpg', 'e_ContentLeft.jpg', 'e_ContentRight.jpg', 'e_DefaultContent.jpg', 'e_Disgust.jpg',
            'e_Disoriented.jpg', 'e_EcstacyHilarious.jpg', 'e_EcstacyStarryEyed.jpg', 'e_Fear.jpg', 'e_Grief.jpg',
            'e_Joy.jpg', 'e_Joy2.jpg', 'e_JoyGoofy.jpg', 'e_JoyGoofy2.jpg', 'e_JoyGoofy3.jpg', 'e_Love.jpg',
            'e_Rage.jpg', 'e_Rage2.jpg', 'e_Rage3.jpg', 'e_Rage4.jpg', 'e_RemorseShame.jpg', 'e_Sadness.jpg',
            'e_Sleeping.jpg', 'e_SleepingZZZ.jpg', 'e_Sleepy.jpg', 'e_Sleepy2.jpg', 'e_Sleepy3.jpg', 'e_Sleepy4.jpg',
            'e_Surprise.jpg', 'e_SystemBlackScreen.jpg', 'e_SystemBlinkLarge.jpg', 'e_SystemBlinkStandard.jpg',
            'e_SystemCamera.jpg', 'e_SystemFlash.jpg', 'e_SystemGearPrompt.jpg', 'e_SystemLogoPrompt.jpg',
            'e_Terror.jpg', 'e_Terror2.jpg', 'e_TerrorLeft.jpg', 'e_TerrorRight.jpg']


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
        await asyncio.shield(_set(RGB(0, 0, 0), 'e_DefaultContent.jpg', off_time_secs, False, True))


def __main():
    asyncio.run(flash(Colors.values(), eyes, on_time_secs=.05, off_time_secs=.02, flashlight=False))


if __name__ == '__main__':
    __main()
