import asyncio
from enum import Enum
from typing import Callable, Coroutine, Any, NamedTuple, Set, FrozenSet, Dict, Optional

from pynput.keyboard import Key

from utils.keyboard.core import KeySet, listen

__author__ = 'acushner'

WrappedAsync = Callable[[None], Coroutine[Any, Any, Any]]


class ChordGroup(Enum):
    """represent which group of an OnOff tuple belongs to"""


class OnOff(NamedTuple):
    """represent which functions to call when chords are turned on/off"""
    on: WrappedAsync
    off: WrappedAsync
    group: Optional[ChordGroup] = None


Chords: Dict[FrozenSet, OnOff]


class Chords(dict):
    """
    way to map chords of keys to actions to take

    a "chord" is simply one or more keys pressed at any given moment
    e.g., cmd + esc, or shift + up
    """

    def __init__(self, states: Set = None):
        super().__init__()
        self._states = states or set()

    def __setitem__(self, keys, val):
        return super().__setitem__(frozenset(keys), val)

    def __getitem__(self, keys):
        return super().__getitem__(frozenset(keys))

    def get(self, keys, default=None):
        return super().get(frozenset(keys), default)


async def _async_r(s):
    """async return - used for testing"""
    return s


nothing = OnOff(lambda: _async_r('nothing: ON'), lambda: _async_r('nothing: OFF'))
_test_chords = Chords()
_test_chords[{Key.shift, Key.down}] = OnOff(lambda: _async_r('down: ON'), lambda: _async_r('down: OFF'))


class KeyboardParser:
    def __init__(self, chords: Chords, *, use_last_triggered: bool = False):
        self._chords = chords
        self._key_set = KeySet()
        self._use_last_triggered = use_last_triggered
        self._last_triggered: FrozenSet = frozenset()

    def _store(self):
        if self._use_last_triggered:
            f = self._key_set.frozen
            if f in self._chords:
                self._last_triggered = f

    def _on_press(self, key):
        self._key_set.add(key)
        self._store()

    def _on_release(self, key):
        if key == Key.esc:
            self._key_set.clear()
            return False  # stops listener
        self._key_set.remove(key)
        self._store()

    async def _parse_input_helper(self, active: OnOff):
        """check current pressed keys and """
        last_chord = self._last_triggered if self._use_last_triggered else self._key_set.frozen
        cur = self._chords.get(last_chord, nothing)
        print(30 * '=')
        self._last_triggered = set()
        if active == cur:
            print('unchanged:', await (cur.on()))
        else:
            print(await (active.off()))
            print(await (cur.on()))
        print(30 * '=')
        return cur

    async def parse_input(self, tick_seconds: float = .5):
        """listen to events and parse every `tick_seconds` seconds"""
        async with listen(self._on_press, self._on_release):
            active = nothing
            for _ in range(20):
                await asyncio.sleep(tick_seconds)
                active = await self._parse_input_helper(active)
