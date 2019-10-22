import asyncio
from asyncio import gather
from random import choice

from misty_py.api import MistyAPI
from misty_py.apis.base import HEIGHT, WIDTH
from misty_py.utils.color import RGB
from misty_py.utils import wait_in_order, wait_first

from utils.ggl.ggl_async import aspeech_to_text, atext_to_speech
from utils.misty.core import UID
from utils.misty.routines.audio import Mood, sounds, play
from utils.misty.routines.text.base import bt

from utils.misty.routines.text.train_face import ftr

__author__ = 'acushner'

api = MistyAPI()

_intro_images = ['e_Joy.jpg']
_music_options = ['studiopolis_short.mp3', 'price_is_right.mp3', 'gandalf_sax.mp3']
_music_options += [
    'central_park_sunday.mp3',
    '3-24 Jump Up, Super Star! Music Box Version.mp3',
    'moon_remastered.mp3',
    'messenger_howling_grotto.mp3',
    '02 Overworld.mp3',
    'iitr_song_of_storms.mp3',
    '1-09 Fossil Falls.mp3',
    '13 - Baby Universe.mp3',
    '1-17 Gusty Garden Galaxy.mp3',
    '3-26 Jump Up, Super Star!.mp3',
    '2-36 Password.mp3',
    '01 nananan katamari.mp3',
    'iirt_aquatic_ruin_zone.mp3',
    'mk7_credits.mp3',
    '06 lonely rolling star.mp3',
]
_music_options += [
    'lizzo_juice.mp3',
]
_thanks = ['thank_you.wav', 'great.wav']
_random = sounds[Mood.relaxed]
_done_sounds = ['tada_win31.mp3']
_shutter_click = [f'camera_shutter_click_{i}.wav' for i in range(1, 4)]
_face_eyes = ['e_ContentLeft.jpg', 'e_ContentRight.jpg']


async def _test_music():
    for m in _music_options:
        print(m)
        await api.audio.play(m, how_long_secs=4, blocking=True)


async def _intro():
    await gather(
        api.images.set_led(RGB(0, 255, 0)),
        api.images.display(choice(_intro_images)),
        ftr.intro
    )
    await api.images.set_led()


async def _record(uid, record_time):
    await api.audio.record(uid.audio, how_long_secs=record_time, blocking=True),


async def _get_name(uid: UID, record_time=3):
    await wait_in_order(
        play('first.wav'),
        ftr.prompt_name,
        api.images.set_led(RGB(255, 255, 0)),
        asyncio.create_task(uid.prompt_name()),
        _record(uid, record_time),
        api.images.set_led(),
        play(choice(_thanks)),
    )
    t = asyncio.create_task(_convert_to_misty_speech(uid))
    print(uid.audio)
    return t


async def _convert_to_misty_speech(uid: UID):
    try:
        human_audio = await api.audio.get(uid.audio, '/tmp/stt.wav')
        text, confidence = await aspeech_to_text(human_audio)
        misty_audio = await atext_to_speech(text)
        await api.audio.upload(uid.audio_misty, data=misty_audio)
    except Exception as e:
        print('ERROR', e)


async def _take_picture(uid: UID):
    await play('next.wav')
    await ftr.prompt_picture
    await gather(
        play('321.mp3', do_animation=False),
        api.images.display('e_SystemCamera.jpg')
    )
    await gather(
        play(choice(_shutter_click), do_animation=False),
        api.images.take_picture(uid.image, width=WIDTH, height=HEIGHT),
    )
    await api.images.display(uid.image)
    await bt.thanks
    await ftr.take_a_look
    await asyncio.sleep(4)


async def _train(uid: UID):
    # put in new eyes here
    await api.images.display(choice(_face_eyes))
    await play('finally.wav')
    await ftr.prompt_training
    await ftr.instructions
    await api.images.set_led(RGB(255, 255, 0))
    await wait_first(
        play(choice(_music_options), do_animation=False),
        api.faces.wait_for_training(str(uid)),
    )
    await gather(
        api.images.set_led(RGB(0, 255, 0)),
        play('tada_win31.mp3'),
        api.images.display('e_Amazement.jpg')
    )
    await play(choice(_thanks))
    await play(uid.audio_misty)
    await ftr.goodbye


async def _done():
    await gather(
        api.images.display('e_DefaultContent.jpg'),
        api.images.set_led()
    )


async def train_face():
    """
    create a clean routine for training someone's face
    - respond to misty command?
    - take picture to confirm who's face it is
    - change led colors while training
    - display countdown on screen
    - prompt for name at end and translate into text?
    - save picture with name
    - ultimately a simple website with form to add cool things about the person?
    - flask server to automatically associate names with faces?
    """
    # await api.audio.wait_for_key_phrase()
    print(UID.dump_store())
    uid = UID('ftuid')
    await _intro()
    print(str(uid))
    t = await _get_name(uid)
    await _take_picture(uid)
    await _train(uid)
    await play(uid.audio_misty)
    await _done()
    await (await uid.prompt_name())


def __main():
    # asyncio.run(api.audio.play('lizzo_juice.mp3'))
    # async_run(_test_music())
    asyncio.run(train_face())


if __name__ == '__main__':
    __main()

    # starts with alrighty then - remove
    # let's take a pic too abrupt'
    # too abrupt for face training time
    # crappy names fail the thing
