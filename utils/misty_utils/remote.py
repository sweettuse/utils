import asyncio
from enum import Enum
from types import SimpleNamespace

from utils.keyboard.chord import OnOff, Chords, KeyboardParser, ChordGroup, WrappedAsync
from pynput.keyboard import Key

# api = MistyAPI('https://fake')
chords = Chords()

api = SimpleNamespace()  # represent MistyAPI
api.movement = SimpleNamespace()


async def drive(forward=0, left_right=0):
    return f'driving: forward = {forward}, left_right = {left_right}'


async def stop():
    return 'driving: stopping'


class MistyChordGroup(ChordGroup):
    drive = 'd'
    head = 'h'


api.movement.drive = drive
api.movement.stop = stop


def _create_drive_func(on: WrappedAsync):
    return OnOff(on, lambda: api.movement.stop(), MistyChordGroup.drive)


# driving
chords[{Key.up}] = _create_drive_func(lambda: api.movement.drive(50))
chords[{Key.right}] = _create_drive_func(lambda: api.movement.drive(left_right=50))
chords[{Key.down}] = _create_drive_func(lambda: api.movement.drive(-50))
chords[{Key.left}] = _create_drive_func(lambda: api.movement.drive(left_right=-50))

chords[{Key.up, Key.left}] = _create_drive_func(lambda: api.movement.drive(50, -50))
chords[{Key.up, Key.right}] = _create_drive_func(lambda: api.movement.drive(50, 50))
chords[{Key.down, Key.left}] = _create_drive_func(lambda: api.movement.drive(-50, -50))
chords[{Key.down, Key.right}] = _create_drive_func(lambda: api.movement.drive(-50, 50))

# TODO: add eye control


asyncio.run(KeyboardParser(chords, use_last_triggered=False).parse_input())
# chords = {frozenset((Key.up,)): OnOff(api.movement.drive
