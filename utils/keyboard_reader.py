import asyncio
import time
from contextlib import suppress, asynccontextmanager
from functools import wraps
from threading import RLock
from typing import NamedTuple, Dict, FrozenSet, Callable, Awaitable, Coroutine, Any
import uvloop

uvloop.install()

import arrow

from pynput import keyboard

from pynput.keyboard import Key

_shift_keys = dict.fromkeys((Key.shift_r, Key.shift_l), Key.shift)
CO = Coroutine[Any, Any, None]

WrappedAsync = Callable[[None], Coroutine[Any, Any, None]]


class OnOff(NamedTuple):
    """represent which functions to call when chords are turned on/off"""
    on: Callable[[None], WrappedAsync]
    off: Callable[[None], WrappedAsync]


Chords: Dict[FrozenSet, OnOff]


class Chords(dict):
    """easy storage for chords of keys pressed"""

    def __setitem__(self, keys, val):
        return super().__setitem__(frozenset(keys), val)

    def __getitem__(self, keys):
        return super().__getitem__(frozenset(keys))

    def get(self, keys, default=None):
        return super().get(frozenset(keys), default)


def _transform_key(key):
    try:
        return key.char.lower()
    except AttributeError:
        return _shift_keys.get(key, key)


def lock_and_transform(func):
    @wraps(func)
    def wrapper(self, key):
        with self._lock:
            func(self, _transform_key(key))

    return wrapper


class KeySet:
    def __init__(self):
        self.s = set()
        self._lock = RLock()

    @lock_and_transform
    def add(self, key):
        self.s.add(key)

    @lock_and_transform
    def remove(self, key):
        with suppress(Exception):
            self.s.remove(key)

    @lock_and_transform
    def __contains__(self, key):
        return key in self.s

    @property
    def frozen(self):
        return frozenset(self.s)

    def __str__(self):
        return str(self.s)

    def __repr__(self):
        return repr(self.s)


_key_set = KeySet()


def on_press(key):
    _key_set.add(key)


def on_release(key):
    _key_set.remove(key)
    if key == Key.esc:
        # Stop listener
        return False


# Collect events until released
# with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
#     listener.join()

# # ...or, in a non-blocking fashion:


async def nothing_func(s):
    return f'{s}: nothing'


nothing = OnOff(lambda: nothing_func('ON'), lambda: nothing_func('OFF'))

test_chords: Dict[FrozenSet, OnOff] = {frozenset((Key.shift, Key.down)): OnOff('ON: shift_down', 'OFF: shift_down')}


async def parse_input(active, chords):
    cur = chords.get(_key_set.frozen, nothing)
    if active == cur:
        print('unchanged:', await (cur.on()))
    else:
        print(await (active.off()))
        print(await (cur.on()))
    return cur


@asynccontextmanager
async def listen(on_press, on_release):
    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()
    try:
        yield
    finally:
        await asyncio.get_event_loop().run_in_executor(None, listener.stop)


async def run_parse_input(chords, tick_seconds: float = .5):
    async with listen(on_press, on_release):
        active = nothing
        for _ in range(20):
            await asyncio.sleep(tick_seconds)
            active = await parse_input(active, chords)

# asyncio.run(run_parse_input(test_chords))
# controller = keyboard.Controller()
# controller.press('a')
# controller.press(keyboard.Key.shift_r)
# controller.release(keyboard.Key.shift_r)
# controller.press('a')
# listener.join()
