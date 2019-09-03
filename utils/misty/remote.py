import asyncio
from collections import ChainMap
from typing import Optional

from pynput.keyboard import Key

from utils.keyboard.chord import OnOff, Chords, ChordGroup, WrappedAsync, Commands, StateChords, parse_state

# api = SimpleNamespace()  # represent fake MistyAPI
# api.movement = SimpleNamespace()
from utils.misty.core import api


async def drive(forward=0, left_right=0):
    return f'driving: forward = {forward}, left_right = {left_right}'


async def stop():
    return 'driving: stopping'


async def halt():
    return 'HALT'


class MistyChordGroup(ChordGroup):
    drive = 'd'
    head = 'h'
    arms = 'a'


async def _async_r(s):
    return s


async def move_head(pitch=None, roll=None, yaw=None):
    return f'HEAD: pitch={pitch}, roll={roll}, yaw={yaw}'


# api.movement.drive = drive
# api.movement.stop = stop
# api.movement.halt = halt
# api.movement.move_head = move_head
# api.movement.move_arms = move_arms


def _get_drive_chords():
    # driving
    def _create_drive_func(on: WrappedAsync):
        return OnOff(on, lambda: api.movement.stop(), MistyChordGroup.drive)

    chords = Chords()
    chords[Key.up,] = _create_drive_func(lambda: api.movement.drive(10))
    chords[Key.right,] = _create_drive_func(lambda: api.movement.drive(0, 1))
    chords[Key.down,] = _create_drive_func(lambda: api.movement.drive(-10))
    chords[Key.left,] = _create_drive_func(lambda: api.movement.drive(0, -1))

    chords[Key.up, Key.left] = _create_drive_func(lambda: api.movement.drive(10, -1))
    chords[Key.up, Key.right] = _create_drive_func(lambda: api.movement.drive(10, 1))
    chords[Key.down, Key.left] = _create_drive_func(lambda: api.movement.drive(-10, -1))
    chords[Key.down, Key.right] = _create_drive_func(lambda: api.movement.drive(-10, 1))
    return chords


def _get_head_chords():
    """
    pitch: up and down
    roll: tilt (ear to shoulder)
    yaw: turn left and right
    """

    def _create_head_func(increment=True, **kwargs):
        return OnOff(lambda: api.movement.move_head(increment=increment, **kwargs, velocity=100), Commands.nothing.off,
                     MistyChordGroup.head)

    def _create_arms_func(pos, vel, *directions, increment=True):
        kwargs = ChainMap(*({f'{d}_position': pos, f'{d}_velocity': vel} for d in directions))
        return OnOff(lambda: api.movement.move_arms(increment=increment, **kwargs), Commands.nothing.off,
                     MistyChordGroup.head)

    chords = Chords()
    chords[Key.up,] = _create_head_func(pitch=15)
    chords[Key.down,] = _create_head_func(pitch=-15)
    chords[Key.left,] = _create_head_func(yaw=-15)
    chords[Key.right,] = _create_head_func(yaw=15)
    chords['a'] = _create_head_func(roll=-15)
    chords['e'] = _create_head_func(roll=15)
    chords[Key.space,] = _create_head_func(False, pitch=0, roll=0, yaw=0)
    chords[Key.shift, Key.up,] = _create_arms_func(15, 15, 'r')
    chords[Key.shift, Key.right,] = _create_arms_func(-15, -15, 'r')
    chords[Key.shift, Key.left,] = _create_arms_func(15, 15, 'l')
    chords[Key.shift, Key.down,] = _create_arms_func(-15, -15, 'l')
    return chords


# def _get_arms_chords():
#     chords = Chords()
#     chords[Key.up,] = _create_arms_func(15, 15, *'lr')
#     chords[Key.down,] = _create_arms_func(-15, -15, *'lr')
#     chords[Key.left, Key.up,] = _create_arms_func(15, 15, 'l')
#     chords[Key.left, Key.down,] = _create_arms_func(-15, -15, 'l')
#     chords[Key.right, Key.up,] = _create_arms_func(15, 15, 'r')
#     chords[Key.right, Key.down,] = _create_arms_func(-15, -15, 'r')
#     chords[Key.space,] = _create_arms_func(0, 0, *'lr', increment=False)
#     return chords


def _get_global_chords():
    chords = Chords()
    chords[Key.shift, 'h'] = OnOff(lambda: api.movement.halt(), lambda: api.movement.halt(), group=object())
    chords[Key.space,] = Commands.stop
    return chords


root = StateChords('__root__', _get_global_chords(), key_char_override=Key.esc)
with StateChords.create_machine(root):
    drive = StateChords('drive', _get_drive_chords())
    head = StateChords('head', _get_head_chords())
    # arms = StateChords('arms', _get_arms_chords())


async def run_remote():
    return await parse_state(root)


# TODO: add eye control


if __name__ == '__main__':
    asyncio.run(run_remote())
