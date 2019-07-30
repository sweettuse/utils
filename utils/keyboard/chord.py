from enum import Enum
from typing import Callable, Coroutine, Any, NamedTuple, Set, FrozenSet, Dict, Optional

from pynput.keyboard import Key

from utils.keyboard.reader import SimpleParser, StateParser
from utils.keyboard.state import State

__author__ = 'acushner'

WrappedAsync = Callable[[None], Coroutine[Any, Any, Any]]


class ChordGroup(Enum):
    """enum base: represent which group of an OnOff tuple belongs to"""


class OnOff(NamedTuple):
    """represent which functions to call when chords are turned on/off"""
    on: WrappedAsync
    off: WrappedAsync
    group: Optional[ChordGroup] = None


class Commands:
    """base commands used to indicate special cases in processing chords"""
    nothing = OnOff(lambda: _async_r('nothing: ON'), lambda: _async_r('nothing: OFF'), group=object())
    stop = OnOff(None, None, object())


Chords: Dict[FrozenSet, OnOff]


class Chords(dict):
    """
    way to map chords of keys to actions to take

    a "chord" is simply one or more keys pressed at any given moment
    e.g., cmd + esc, or shift + up
    """

    def get(self, keys, default=None) -> OnOff:
        return super().get(frozenset(keys), default)

    async def parse(self):
        """read input and execute commands based on current chords"""
        parser = SimpleParser(self._debounce_s)
        prev = Commands.nothing

        async for keys in parser.read_chars():
            prev = await self._parse_one(keys, prev)
        await prev.off()

    async def parse_one(self, keys, prev: OnOff) -> Optional[OnOff]:
        current = self.get(keys)
        if current is None:
            # we haven't found a known chord
            return None

        if current is Commands.stop:
            """stop what is currently running"""
            print('  OFF:', await prev.off())
            return Commands.nothing
        elif current == prev:
            print('   unchanged:', await current.on())
        else:
            if current.group != prev.group:
                print('  OFF:', await prev.off())
            print('   CHANGED:', await current.on())
        return current

    def __init__(self, debounce_secs=.1):
        super().__init__()
        self._debounce_s = debounce_secs

    def __setitem__(self, keys, val):
        return super().__setitem__(frozenset(keys), val)

    def __getitem__(self, keys):
        return super().__getitem__(frozenset(keys))


class StateChords(State):
    def __init__(self, name, chords: Chords, key_char_override=None):
        super().__init__(name, key_char_override)
        self.chords = chords


async def parse_state(state_chords: StateChords, debounce_s: int = .04):
    parser = StateParser(state_chords, debounce_s, frozenset((Key.shift, Key.esc)))
    prev: OnOff = Commands.nothing
    prev_state = state_chords

    async for state, keys in parser.read_chars():
        print(80 * '=')
        print()
        if prev_state != state:
            print('  OFF:', await prev.off())
        prev_state = state
        new = await state.chords.parse_one(keys, prev)
        new = new or await state.root.chords.parse_one(keys, prev)
        prev = new or prev

    await prev.off()


_test_chords = Chords()
_test_chords[{Key.shift, Key.down}] = OnOff(lambda: _async_r('down: ON'), lambda: _async_r('down: OFF'))


async def _async_r(s):
    """async return - used for testing"""
    return s
