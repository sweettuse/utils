import random
from dataclasses import dataclass, asdict
from enum import Enum
from io import BytesIO
from typing import Optional
from uuid import uuid4

import simpleaudio as sa
from lifxlan3 import timer
from misty_py.utils import classproperty
from tones import SINE_WAVE, SQUARE_WAVE, TRIANGLE_WAVE, SAWTOOTH_WAVE
from tones.mixer import Mixer

__author__ = 'acushner'

from utils.core import exhaust


class WaveType(Enum):
    sine = SINE_WAVE  # chill
    square = SQUARE_WAVE  # video game
    triangle = TRIANGLE_WAVE  # chill video game?
    sawtooth = SAWTOOTH_WAVE  # buzzy

    @classproperty
    def random(cls):
        return random.choice(list(cls))


@dataclass
class TrackArgs:
    attack: float = None
    decay: float = None
    vibrato_frequency: float = None
    vibrato_variance: float = 3.


@timer
def fun(wave_type: WaveType, notes: Optional[str] = None, mixer: Optional[Mixer] = None, duration=.2):
    mixer = mixer or Mixer(44100, .3)
    track_args = TrackArgs()  # vibrato_frequency=5, vibrato_variance=5)
    name = str(uuid4())
    mixer.create_track(name, wave_type.value, **asdict(track_args))
    if notes:
        octave = 4
        for n in notes.split():
            if n == '+':
                octave += 1
            elif n == '-':
                octave -= 1
            else:
                buckets = notes, nums = [], []
                exhaust(buckets[c.isdigit() or c == '.'].append(c) for c in n)
                mult = float(''.join(nums)) if nums else 1
                note = ''.join(notes)
                if note == 's':
                    mixer.add_note(name, 'a', duration=mult * duration, octave=octave, amplitude=0)
                else:
                    mixer.add_note(name, note, duration=mult * duration, octave=octave)

    else:
        mixer.add_note(name, duration=.5)
        mixer.add_note(name, endnote='f', duration=.5)
        mixer.add_note(name, 'f')
    return mixer


@timer
def to_wav(mixer: Mixer) -> BytesIO:
    bio = BytesIO()
    mixer.write_wav(bio)
    bio.seek(0)
    return bio


def play(bio: BytesIO):
    wo = sa.WaveObject.from_wave_file(bio)
    wo.play().wait_done()


def _right() -> str:
    """bach something in c minor"""
    return ('c g f g ab f eb f g eb d eb f d c d 2eb + 2c - 2f + 2c - 2eb + 2c - 2d 2b '
            'c eb g + c - d + c - b a d g b + d - eb + d c - b eb ab + c eb - f + eb d c - f bb + d f - g + f eb d '
            'eb c - bb + c d - bb ab bb + c - bb ab g f '
            )


def _left() -> str:
    return ('- 2c + 2c - 2f + 2c - 2eb + 2c - 2d 2b c g f g ab f eb f g eb d eb f d c d '
            '2eb 2c 2f 2d 2g 2f 2g 2eb 2ab 2g 2a 2f 2bb 2a 2b 2g '
            '+ c - ab g ab bb g f g ab 4s + eb d c'
            )


def bach():
    dur = .15
    mixer = fun(WaveType.sine, _right(), duration=dur)
    fun(WaveType.triangle, _left(), mixer, duration=dur)
    output = to_wav(mixer)
    play(output)


def outlier():
    offset = '- - '
    notes = 'c g + c - eb bb + eb - d + d - a ab eb + c db - ab db '
    dur = .47
    mixer = fun(WaveType.sawtooth, offset + notes * 3, duration=dur)
    wav = to_wav(mixer)
    # with open('/tmp/outlier.wav', 'wb') as f:
    #     f.write(wav.read())
    play(wav)


def all_notes():
    pass


def __main():
    # return outlier()
    return bach()


if __name__ == '__main__':
    __main()
