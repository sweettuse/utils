import asyncio
from enum import Enum
from random import choice
from typing import Optional

from utils.ggl.ggl_async import atext_to_speech
from utils.ggl.google_clients import AudioEncoding
from utils.misty.core import api

# from utils.ggl.google_clients import text_to_speech

__author__ = 'acushner'

__all__ = 'Mood play_mood random_sound say play random_simpsons_quote'.split()


class Mood(Enum):
    acceptance = 'acceptance'
    amazement = 'amazement'
    anger = 'anger'
    annoyance = 'annoyance'
    awe = 'awe'
    boredom = 'boredom'
    disapproval = 'disapproval'
    disgust = 'disgust'
    disoriented_confused = 'disoriented_confused'
    distraction = 'distraction'
    ecstacy = 'ecstacy'
    fear = 'fear'
    grief = 'grief'
    joy = 'joy'
    loathing = 'loathing'
    love = 'love'
    phrase = 'phrase'
    rage = 'rage'
    sadness = 'sadness'
    sleepy = 'sleepy'
    sleepy_snore = 'sleepy_snore'
    system = 'system'


sounds = {
    Mood.acceptance: ['s_Acceptance.wav'],
    Mood.amazement: ['s_Amazement.wav', 's_Amazement2.wav'],
    Mood.anger: ['s_Anger.wav', 's_Anger2.wav', 's_Anger3.wav', 's_Anger4.wav'],
    Mood.annoyance: ['s_Annoyance.wav', 's_Annoyance2.wav', 's_Annoyance3.wav', 's_Annoyance4.wav'],
    Mood.awe: ['s_Awe.wav', 's_Awe2.wav', 's_Awe3.wav'],
    Mood.boredom: ['s_Boredom.wav'],
    Mood.disapproval: ['s_Disapproval.wav'],
    Mood.disgust: ['s_Disgust.wav', 's_Disgust2.wav', 's_Disgust3.wav'],
    Mood.disoriented_confused: ['s_DisorientedConfused.wav', 's_DisorientedConfused2.wav',
                                's_DisorientedConfused3.wav', 's_DisorientedConfused4.wav',
                                's_DisorientedConfused5.wav', 's_DisorientedConfused6.wav'],
    Mood.distraction: ['s_Distraction.wav'],
    Mood.ecstacy: ['s_Ecstacy.wav', 's_Ecstacy2.wav'],
    Mood.fear: ['s_Fear.wav'],
    Mood.grief: ['s_Grief.wav', 's_Grief2.wav', 's_Grief3.wav', 's_Grief4.wav'],
    Mood.joy: ['s_Joy.wav', 's_Joy2.wav', 's_Joy3.wav', 's_Joy4.wav'],
    Mood.loathing: ['s_Loathing.wav'],
    Mood.love: ['s_Love.wav'],
    Mood.phrase: ['s_PhraseByeBye.wav', 's_PhraseEvilAhHa.wav', 's_PhraseHello.wav', 's_PhraseNoNoNo.wav',
                  's_PhraseOopsy.wav', 's_PhraseOwOwOw.wav', 's_PhraseOwwww.wav', 's_PhraseUhOh.wav'],
    Mood.rage: ['s_Rage.wav'],
    Mood.sadness: ['s_Sadness.wav', 's_Sadness2.wav', 's_Sadness3.wav', 's_Sadness4.wav', 's_Sadness5.wav',
                   's_Sadness6.wav', 's_Sadness7.wav'],
    Mood.sleepy: ['s_Sleepy.wav', 's_Sleepy2.wav', 's_Sleepy3.wav', 's_Sleepy4.wav', 's_SleepySnore.wav'],
    Mood.system: ['s_SystemCameraShutter.wav', 's_SystemFailure.wav', 's_SystemSuccess.wav', 's_SystemWakeWord.wav']
}


async def play_mood(mood):
    """play all sounds from a given mood"""
    names = sounds[mood]
    for n in names:
        print('playing:', mood, n)
        await api.audio.play(n, blocking=True)


async def random_sound(mood=None, blocking=True):
    """play a roundom built-in sound"""
    mood = mood or choice(list(Mood))
    name = choice(sounds[mood])
    print('playing:', mood, name)
    await api.audio.play(name, blocking=blocking)


async def say(s, *, do_animation=True, mult=1.5):
    clip = await atext_to_speech(s, AudioEncoding.wav)
    name = 'from_google.wav'
    await api.audio.upload(name, data=clip)
    await play(name, do_animation=do_animation, mult=mult)


async def play(name, *, how_long_secs: Optional[int] = None, do_animation=True, mult=1.0):
    """play a file on misty and animate by default"""
    from utils.misty.routines.movement import animate
    async with api.movement.reset_to_orig():
        try:
            if do_animation:
                t = asyncio.create_task(animate(mult))
            await api.audio.play(name, blocking=True, how_long_secs=how_long_secs)
        finally:
            if do_animation:
                t.cancel()


async def random_simpsons_quote():
    name = f'simpsons--simpsons_{choice(range(1, 101))}.mp3'
    print(name)
    await api.audio.play(name)


def __main():
    asyncio.run(random_sound())
    # asyncio.run(play_mood(Mood.love))
    pass


if __name__ == '__main__':
    __main()
