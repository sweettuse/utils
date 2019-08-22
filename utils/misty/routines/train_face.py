import asyncio
import os
from asyncio import gather
from random import choice
from uuid import uuid4

from misty_py.api import MistyAPI, RGB
from misty_py.utils import async_run

from utils.core import play_sound
from utils.ggl.ggl_async import aspeech_to_text, atext_to_speech
from utils.misty.core import named_temp_file
from utils.misty.routines.audio import Mood, sounds

__author__ = 'acushner'

api = MistyAPI()

_intro_images = ['e_Joy.jpg']
_intro_prompts = ['face_train_intro.wav']
_train_prompts = [f'face_training_time{i}.wav' for i in range(1, 4)]
_train_instructions = ['face_training_inst.wav']
_alright = ['alright.wav', 'alrighty_then.wav', 'ok.wav', 'ok_then.wav']
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
    'pomplamoose_jamiroquai.mp3',
    'pomplamoose_waiting_line.mp3',
    'pomplamoose_radiohead.mp3',
]
_thanks = ['thank_you.wav', 'great.wav']
_random = sounds[Mood.relaxed]
_done_sounds = ['tada_win31.mp3']
_pic_prompts = ['smile_for_the_camera.wav', 'lets_take_picture.wav']
_pic_prompts = ['lets_take_picture.wav']
_shutter_click = [f'camera_shutter_click_{i}.wav' for i in range(1, 4)]
_face_eyes = ['e_ContentLeft.jpg', 'e_ContentRight.jpg']


async def _test_music():
    for m in _music_options:
        print(m)
        await api.audio.play(m, how_long_secs=4, blocking=True)


class UID:
    def __init__(self, prefix=''):
        self.uid = self._init_uid(prefix)

    @staticmethod
    def _init_uid(prefix):
        _base = hex(uuid4().fields[0])[2:]
        return ('' if not prefix else f'{prefix}_') + _base

    @property
    def image(self):
        return f'{self.uid}.jpg'

    @property
    def audio(self):
        return f'{self.uid}.wav'

    @property
    def audio_misty(self):
        return f'{self.uid}_misty.wav'

    def __str__(self):
        return self.uid


async def _intro():
    await api.audio.play(choice(_random), blocking=True)
    await gather(
        api.images.set_led(RGB(0, 255, 0)),
        api.images.display(choice(_intro_images)),
        api.audio.play(choice(_intro_prompts), blocking=True)
    )
    await api.images.set_led()


async def _record(uid, record_time):
    await api.audio.record(uid.audio, how_long_secs=record_time, blocking=True),


async def _get_name(uid: UID, record_time=4):
    await api.audio.play('first.wav', blocking=True)
    await api.audio.play('face_train_prompt_name.wav', blocking=True)
    await gather(
        api.images.set_led(RGB(255, 255, 0)),
        _record(uid, record_time)
    )
    await api.audio.play(choice(_thanks), blocking=True)
    await api.images.set_led()
    print(uid.audio)

    # return asyncio.create_task(_convert_to_misty_speech(uid))
    # await _convert_to_misty_speech(uid)


async def _upload_audio_bytes(name, audio):
    with named_temp_file(name) as f:
        f.write(audio)
        await api.audio.upload(f.name)


async def _convert_to_misty_speech(uid: UID):
    try:
        human_audio = await api.audio.get(uid.audio, '/tmp/stt.wav')
        text, confidence = await aspeech_to_text(human_audio)
        misty_audio = await atext_to_speech(text)
        await _upload_audio_bytes(uid.audio_misty, misty_audio)
    except Exception as e:
        print('ERROR', e)


async def _take_picture(uid: UID):
    await api.audio.play('next.wav', blocking=True)
    await api.audio.play(choice(_pic_prompts), blocking=True)
    await gather(
        api.audio.play('321.mp3', blocking=True),
        api.images.display('e_SystemCamera.jpg')
    )
    await gather(
        api.images.take_picture(uid.image),
        api.audio.play(choice(_shutter_click), blocking=True, how_long_secs=2)
    )
    await api.audio.play(choice(_thanks), blocking=True)


async def _train(uid: UID):
    # put in new eyes here
    await api.images.display(choice(_face_eyes))
    await api.audio.play('finally.wav', blocking=True)
    await api.audio.play(choice(_train_prompts), blocking=True)
    await api.audio.play(choice(_train_instructions), blocking=True)
    await gather(
        api.audio.play(choice(_music_options)),
        api.faces.wait_for_training(str(uid)),
        api.images.set_led(RGB(255, 255, 0))
    )
    await gather(
        api.images.set_led(RGB(0, 255, 0)),
        api.audio.play('tada_win31.mp3', blocking=True),
        api.images.display('e_Amazement.jpg')
    )
    await api.audio.play(choice(_thanks), blocking=True)
    await api.audio.play(uid.audio_misty, blocking=True)
    await api.audio.play('see_you_around.wav', blocking=True)


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
    # await _intro()
    uid = UID('ftuid')
    print(str(uid))
    await _record(uid, 4)
    await api.audio.get(uid.audio, '/tmp/a.wav')
    play_sound('/tmp/a.wav')
    # t = await _get_name(uid)
    # await _take_picture(uid)
    # await _train(uid)
    # await t
    # await api.audio.play(uid.audio_misty)
    await _done()


def __main():
    asyncio.run(api.audio.play('lizzo_juice.mp3'))
    # async_run(_test_music())
    # async_run(train_face())


if __name__ == '__main__':
    __main()

    # starts with alrighty then - remove
    # let's take a pic too abrupt'
    # too abrupt for face training time
    # crappy names fail the thing
