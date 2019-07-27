import asyncio
from types import SimpleNamespace

from misty_py.api import MistyAPI

from utils.keyboard_reader import OnOff, nothing, Chords, run_parse_input
from pynput.keyboard import Key

# api = MistyAPI('https://fake')
chords = Chords()

api = SimpleNamespace()  # represent MistyAPI
api.movement = SimpleNamespace()


async def drive(forward=0, left_right=0):
    return f'driving: forward = {forward}, left_right = {left_right}'


async def stop():
    return 'driving: stopping'


api.movement.drive = drive
api.movement.stop = stop

# driving
chords[{Key.up}] = OnOff(lambda: api.movement.drive(50), lambda: api.movement.stop())
chords[{Key.right}] = OnOff(lambda: api.movement.drive(left_right=50), lambda: api.movement.stop())
chords[{Key.down}] = OnOff(lambda: api.movement.drive(-50), lambda: api.movement.stop())
chords[{Key.left}] = OnOff(lambda: api.movement.drive(left_right=-50), lambda: api.movement.stop())

chords[{Key.up, Key.left}] = OnOff(lambda: api.movement.drive(50, -50), lambda: api.movement.stop())
chords[{Key.up, Key.right}] = OnOff(lambda: api.movement.drive(50, 50), lambda: api.movement.stop())
chords[{Key.down, Key.left}] = OnOff(lambda: api.movement.drive(-50, -50), lambda: api.movement.stop())
chords[{Key.down, Key.right}] = OnOff(lambda: api.movement.drive(-50, 50), lambda: api.movement.stop())

# TODO: add eye control


print(chords.get({Key.up}))
asyncio.run(run_parse_input(chords))
# chords = {frozenset((Key.up,)): OnOff(api.movement.drive
