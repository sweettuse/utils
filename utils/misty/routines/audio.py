import asyncio
from enum import Enum
from random import choice

from utils.ggl.ggl_async import atext_to_speech
from utils.ggl.google_clients import AudioEncoding
from utils.misty.core import api

# from utils.ggl.google_clients import text_to_speech

__author__ = 'acushner'

__all__ = 'Mood play_mood random_sound say play random_simpsons_quote'.split()


class Mood(Enum):
    curious = 'curious'
    excited = 'excited'
    hate = 'hate'
    idle = 'idle'
    love = 'love'
    terror = 'terror'
    sounds = 'sounds'
    relaxed = 'relaxed'


sounds = {
    Mood.curious: '001-EeeeeeE.wav 004-EuuEuuuuu.wav 005-EeeeeeE-02.wav 007-EeeHA.wav 010-Uhm.wav 020-eooooO.wav 023-Tiss.wav 024-Tiss-02.wav'.split(),
    Mood.excited: '007-Surprised_Ahhh.wav 010-Eh.wav 013-Surprised-Ahghh.wav 017-HuOoo.wav 017-Skreetc.wav 026-PstPstPst.wav 044-RRrAaaRw.wav'.split(),
    Mood.hate: '019-KaYA.wav 030-Beewe.wav 031-Psspewpew.wav 032-Bewbewbeeew.wav'.split(),
    Mood.idle: '002-Ahhh.wav 003-UmmMmmUmm.wav 006-EhMeEhmeUh.wav 009-Idle-Hum-01.wav 010-Hummmmmm.wav'.split(),
    Mood.love: '003-Waaa.wav 008-AhhhAhh.wav 015-Meow.wav 017-Sensor-Touch-Excitement-02.wav 042-OHHHahhah.wav 007-OuuuUUO.wav 012-WhooooA.wav 016-Sensor-Touch-Excitement.wav 041-AhhhhUhh.wav '.split(),
    Mood.terror: '003-Screetch.wav 006-Sigh-01.wav 007-Eurhura.wav 008-Huhurr.wav 013-0Bark.wav 027-Ruuufff.wav 043-Bbbaaah.wav 004-Ahhhh.wav 006-UhhhhOoE.wav 008-Ah.wav 009-Eheheur.wav 020-Whoap.wav 028-Erruruuff.wav 045-Wah.wav 005-Eurra.wav 006-Urhurra.wav 008-Eeh.wav 011-Ah-02.wav 027-Bark-04.wav 037-Eurrt.wav'.split(),
    Mood.sounds: '001-Veep.wav 004-Sniff.wav 006-Sniffle.wav 010-Sniff-02.wav 034-Hicup.wav 003-Scratch.wav 005-Sigh-02.wav 007-Sneeze.wav 028-Snort.wav'.split(),
    Mood.relaxed: '001-OooOooo.wav 002-Weerp.wav 005-OoAhhh.wav 012-Ahhhhh.wav 035-Eurraka.wav 002-Growl-01.wav 004-WhaooooO.wav 011-EhAhhh-Refreshed.wav 033-Ya.wav 036-Eurch.wav'.split()
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


async def play(name, *, do_animation=True, mult=1.0):
    """play a file on misty and animate by default"""
    from utils.misty.routines.movement import animate
    async with api.movement.reset_to_orig():
        try:
            if do_animation:
                t = asyncio.create_task(animate(mult))
            await api.audio.play(name, blocking=True)
        finally:
            if do_animation:
                t.cancel()


async def random_simpsons_quote():
    name = f'simpsons--simpsons_{choice(range(1, 101))}.mp3'
    print(name)
    await api.audio.play(name)


def __main():
    asyncio.run(play_mood(Mood.love))
    pass


if __name__ == '__main__':
    __main()
