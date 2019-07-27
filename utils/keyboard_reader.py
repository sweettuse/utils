import asyncio
from contextlib import suppress, asynccontextmanager
from functools import wraps, partial
from threading import RLock
from typing import NamedTuple, Dict, FrozenSet, Callable, Coroutine, Any

import uvloop
from pynput import keyboard
from pynput.keyboard import Key

uvloop.install()

WrappedAsync = Callable[[None], Coroutine[Any, Any, Any]]


class OnOff(NamedTuple):
    """represent which functions to call when chords are turned on/off"""
    on: WrappedAsync
    off: WrappedAsync


Chords: Dict[FrozenSet, OnOff]


class Chords(dict):
    """
    easy storage for chords of keys pressed

    a "chord" is simply one or more keys pressed at any given moment
    e.g., cmd + esc, or shift + up
    """

    def __setitem__(self, keys, val):
        return super().__setitem__(frozenset(keys), val)

    def __getitem__(self, keys):
        return super().__getitem__(frozenset(keys))

    def get(self, keys, default=None):
        return super().get(frozenset(keys), default)


_shift_keys = dict.fromkeys((Key.shift_r, Key.shift_l), Key.shift)


def _transform_key(key):
    try:
        return key.char.lower()
    except AttributeError:
        return _shift_keys.get(key, key)


def _lock_and_transform(func):
    """
    used with `KeySet`

    lock the function call and transform the key passed in to the correct format
    """

    @wraps(func)
    def wrapper(self, key):
        with self._lock:
            func(self, _transform_key(key))

    return wrapper


class KeySet:
    """thread-safe way to store key presses/chords of keys pressed"""

    def __init__(self, chords: Chords):
        self.s = set()
        self._lock = RLock()
        self._chords = chords

    @property
    def frozen(self):
        return frozenset(self.s)

    @property
    def current(self) -> OnOff:
        """get current active chords, if any"""
        return self._chords.get(self.frozen, nothing)

    @_lock_and_transform
    def add(self, key):
        self.s.add(key)

    @_lock_and_transform
    def remove(self, key):
        with suppress(Exception):
            self.s.remove(key)

    @_lock_and_transform
    def __contains__(self, key):
        return key in self.s

    def __str__(self):
        return str(self.s)

    def __repr__(self):
        return repr(self.s)


def _on_press(key_set, key):
    key_set.add(key)


def _on_release(key_set, key):
    key_set.remove(key)
    if key == Key.esc:
        # Stop listener
        return False


# Collect events until released
# with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
#     listener.join()

async def _async_r(s):
    """async return - used for testing"""
    return s


nothing = OnOff(lambda: _async_r('nothing: ON'), lambda: _async_r('nothing: OFF'))

_test_chords = Chords()
_test_chords[{Key.shift, Key.down}] = OnOff(lambda: _async_r('down: ON'), lambda: _async_r('down: OFF'))


@asynccontextmanager
async def listen(on_press, on_release):
    """listen to keyboard presses/releases"""
    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()
    try:
        yield
    finally:
        await asyncio.get_event_loop().run_in_executor(None, listener.stop)


async def _parse_input(active, key_set):
    """check current pressed keys and """
    cur = key_set.current
    print('==========')
    if active == cur:
        print('unchanged:', await (cur.on()))
    else:
        print(await (active.off()))
        print(await (cur.on()))
    print('==========')
    return cur


async def run_parse_input(chords: Chords, tick_seconds: float = .5):
    """listen to events and parse every `tick_seconds` seconds"""
    key_set = KeySet(chords)
    async with listen(partial(_on_press, key_set), partial(_on_release, key_set)):
        active = nothing
        for _ in range(20):
            await asyncio.sleep(tick_seconds)
            active = await _parse_input(active, key_set)

# asyncio.run(run_parse_input(test_chords))
# controller = keyboard.Controller()
# controller.press('a')
# controller.press(keyboard.Key.shift_r)
# controller.release(keyboard.Key.shift_r)
# controller.press('a')
# listener.join()
