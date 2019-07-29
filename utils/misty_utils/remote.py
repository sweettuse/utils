import asyncio
from types import SimpleNamespace

from pynput.keyboard import Key

from utils.keyboard.chord import OnOff, Chords, ChordGroup, WrappedAsync, Commands

# api = MistyAPI('https://fake')
chords = Chords()

api = SimpleNamespace()  # represent fake MistyAPI
api.movement = SimpleNamespace()


async def drive(forward=0, left_right=0):
    return f'driving: forward = {forward}, left_right = {left_right}'


async def stop():
    return 'driving: stopping'


async def halt():
    return 'HALT'


class MistyChordGroup(ChordGroup):
    drive = 'd'
    head = 'h'


async def _async_r(s):
    return s


api.movement.drive = drive
api.movement.stop = stop
api.movement.halt = halt


# driving
def _create_drive_func(on: WrappedAsync):
    return OnOff(on, lambda: api.movement.stop(), MistyChordGroup.drive)


chords[Key.up,] = _create_drive_func(lambda: api.movement.drive(50))
chords[Key.right,] = _create_drive_func(lambda: api.movement.drive(left_right=50))
chords[Key.down,] = _create_drive_func(lambda: api.movement.drive(-50))
chords[Key.left,] = _create_drive_func(lambda: api.movement.drive(left_right=-50))

chords[Key.up, Key.left] = _create_drive_func(lambda: api.movement.drive(50, -50))
chords[Key.up, Key.right] = _create_drive_func(lambda: api.movement.drive(50, 50))
chords[Key.down, Key.left] = _create_drive_func(lambda: api.movement.drive(-50, -50))
chords[Key.down, Key.right] = _create_drive_func(lambda: api.movement.drive(-50, 50))

# stop everything
chords[Key.shift, 'h'] = OnOff(lambda: api.movement.halt(), lambda: api.movement.halt(), group=object())
chords[Key.space,] = Commands.stop

# TODO: head
# TODO: add eye control


asyncio.run(chords.parse())
# chords = {frozenset((Key.up,)): OnOff(api.movement.drive
