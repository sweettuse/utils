from enum import Enum
from typing import Callable, Coroutine, Any, NamedTuple, Set, FrozenSet, Dict, Optional

from pynput.keyboard import Key

from utils.keyboard.reader import SimpleParser

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

    def __init__(self, states: Set = None, debounce_secs=.1):
        super().__init__()
        self._states = states or set()
        self._debounce_s = debounce_secs

    def __setitem__(self, keys, val):
        return super().__setitem__(frozenset(keys), val)

    def __getitem__(self, keys):
        return super().__getitem__(frozenset(keys))

    def get(self, keys, default=None) -> OnOff:
        return super().get(frozenset(keys), default)

    async def parse(self):
        """read input and execute commands based on current chords"""
        parser = SimpleParser(self._debounce_s)
        prev = Commands.nothing

        async for keys in parser.read_chars():
            current = self.get(keys)
            if current is None:
                # we haven't found a known chord
                continue

            if current is Commands.stop:
                """stop what is currently running"""
                print('  OFF:', await prev.off())
                prev = Commands.nothing
                continue

            elif current == prev:
                print('   unchanged:', await current.on())
            else:
                if current.group != prev.group:
                    print('  OFF:', await prev.off())
                print('   CHANGED:', await current.on())
            prev = current
        await prev.off()


_test_chords = Chords()
_test_chords[{Key.shift, Key.down}] = OnOff(lambda: _async_r('down: ON'), lambda: _async_r('down: OFF'))


async def _async_r(s):
    """async return - used for testing"""
    return s
