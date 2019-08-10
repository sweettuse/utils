import asyncio
from asyncio import gather
from random import choice
from uuid import uuid4

from misty_py.api import MistyAPI, MISTY_URL, RGB
from misty_py.utils import async_run

__author__ = 'acushner'

api = MistyAPI(MISTY_URL)

_intro_images = ['DefaultEyes_Joy.jpg']
_intro_prompts = ['face_train_intro.wav']
_train_prompts = [f'face_training_time{i}.wav' for i in range(1, 4)]
_train_instructions = ['face_training_inst.wav']
_alright = ['alright.wav', 'alrighty_then.wav', 'ok.wav', 'ok_then.wav']
_music_options = ['studiopolis_short.mp3', 'smooth_jazz_is_being_deployed.mp3', 'price_is_right.mp3', 'gandalf_sax.mp3']
_thanks = ['thank_you.wav', 'great.wav']
_random = ['001-EeeeeeE.wav', '001-OooOooo.wav', '002-Growl-01.wav', '002-Weerp.wav', '003-UmmMmmUmm.wav',
           '003-Waaa.wav', '004-Ahhhh.wav', '005-EeeeeeE-02.wav', '005-Eurra.wav', '005-OoAhhh.wav']
_done_sounds = ['tada_win31.mp3']
_pic_prompts = ['smile_for_the_camera.wav', 'lets_take_picture.wav']
_shutter_click = [f'camera_shutter_click_{i}.wav' for i in range(1, 4)]


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

    def __str__(self):
        return self.uid


async def _intro():
    await gather(
        api.images.set_led(RGB(0, 255, 0)),
        api.images.display(choice(_intro_images)),
        api.audio.play(choice(_alright), blocking=True)
    )
    await api.audio.play(choice(_intro_prompts), blocking=True)
    await api.images.set_led()


async def _get_name(uid: UID, record_time=4):
    await api.audio.play('first.wav', blocking=True)
    await api.audio.play('face_train_prompt_name.wav', blocking=True)
    await gather(
        api.images.set_led(RGB(255, 255, 0)),
        api.audio.start_recording(uid.audio, record_time),
        asyncio.sleep(record_time)
    )
    await api.audio.play(choice(_thanks), blocking=True)
    await api.images.set_led()


async def _take_picture(uid: UID):
    await api.audio.play(choice(_pic_prompts), blocking=True)
    await gather(
        api.audio.play('321.mp3', blocking=True),
        api.images.display('DefaultEyes_SystemCamera.jpg')
    )
    await gather(
        api.images.take_picture(uid.image),
        api.audio.play(choice(_shutter_click), blocking=True, how_long_secs=2)
    )
    await api.audio.play(choice(_thanks), blocking=True)


async def _train(uid: UID):
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
        api.images.display('DefaultEyes_Amazement.jpg')
    )
    await api.audio.play(choice(_thanks), blocking=True)
    await api.audio.play('see_you_around.wav', blocking=True)


async def _done():
    await gather(
        api.images.display('DefaultEyes_DefaultContent.jpg'),
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
    await api.audio.wait_for_key_phrase()
    await _intro()
    uid = UID('ftuid')
    print(str(uid))
    await _get_name(uid)
    await _take_picture(uid)
    await _train(uid)
    await _done()


def __main():
    async_run(train_face())


if __name__ == '__main__':
    __main()
