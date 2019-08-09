import asyncio
from collections import ChainMap
from types import SimpleNamespace
from typing import Optional

from misty_py.api import MistyAPI
from misty_py.utils import ArmSettings
from pynput.keyboard import Key

from utils.keyboard.chord import OnOff, Chords, ChordGroup, WrappedAsync, Commands, StateChords, parse_state

api = MistyAPI('http://192.168.86.20')

# api = SimpleNamespace()  # represent fake MistyAPI
# api.movement = SimpleNamespace()


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


async def move_arms(l_position: Optional[float] = None, l_velocity: Optional[float] = None,
                    r_position: Optional[float] = None, r_velocity: Optional[float] = None):
    return f'{ArmSettings("left", l_position, l_velocity)},{ArmSettings("right", r_position, r_velocity)}'


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

    def _create_head_func(**kwargs):
        return OnOff(lambda: api.movement.move_head(**kwargs), Commands.nothing.off, MistyChordGroup.head)

    chords = Chords()
    chords[Key.up,] = _create_head_func(pitch=50)
    chords[Key.down,] = _create_head_func(pitch=-50)
    chords[Key.left,] = _create_head_func(yaw=-50)
    chords[Key.right,] = _create_head_func(yaw=50)
    chords[Key.up, Key.left] = _create_head_func(roll=-50)
    chords[Key.up, Key.right] = _create_head_func(roll=50)
    chords[Key.space,] = _create_head_func(pitch=0, roll=0, yaw=0)
    return chords


def _get_arms_chords():
    def _create_arms_func(pos, vel, *directions):
        kwargs = ChainMap(*({f'{d}_position': pos, f'{d}_velocity': vel} for d in directions))
        return OnOff(lambda: api.movement.move_arms(**kwargs), Commands.nothing.off, MistyChordGroup.arms)

    chords = Chords()
    chords[Key.up,] = _create_arms_func(50, 50, *'lr')
    chords[Key.down,] = _create_arms_func(-50, -50, *'lr')
    chords[Key.left, Key.up,] = _create_arms_func(50, 50, 'l')
    chords[Key.left, Key.down,] = _create_arms_func(-50, -50, 'l')
    chords[Key.right, Key.up,] = _create_arms_func(50, 50, 'r')
    chords[Key.right, Key.down,] = _create_arms_func(-50, -50, 'r')
    chords[Key.space,] = _create_arms_func(0, 0, *'lr')
    return chords


def _get_global_chords():
    chords = Chords()
    chords[Key.shift, 'h'] = OnOff(lambda: api.movement.halt(), lambda: api.movement.halt(), group=object())
    chords[Key.space,] = Commands.stop
    return chords


root = StateChords('__root__', _get_global_chords(), key_char_override=Key.esc)
with StateChords.create_machine(root):
    drive = StateChords('drive', _get_drive_chords())
    head = StateChords('head', _get_head_chords())
    arms = StateChords('arms', _get_arms_chords())

# TODO: add eye control

# loop = asyncio.get_event_loop()
# asyncio.run
asyncio.run(parse_state(root))

# asyncio.run(parse_state(root))
# asyncio.run(chords.parse())
# chords = {frozenset((Key.up,)): OnOff(api.movement.drive
