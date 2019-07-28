import asyncio
import threading
from asyncio import Task
from contextlib import suppress, asynccontextmanager
from functools import wraps, partial
from queue import Queue, Empty
from threading import RLock
from typing import NamedTuple, Dict, FrozenSet, Callable, Coroutine, Any, Set, Optional, Awaitable, AsyncIterable

import arrow
import uvloop
from pynput import keyboard
from pynput.keyboard import Key

from utils.core import exhaust

uvloop.install()

WrappedAsync = Callable[[None], Coroutine[Any, Any, Any]]


class OnOff(NamedTuple):
    """represent which functions to call when chords are turned on/off"""
    on: WrappedAsync
    off: WrappedAsync


_shift_keys = dict.fromkeys((Key.shift_r, Key.shift_l), Key.shift)
_mod_keys = {Key.shift, Key.cmd, Key.ctrl, Key.esc, Key.alt}
_mod_keys.update(getattr(Key, f'f{n}') for n in range(1, 21))
nothing = OnOff(lambda: _async_r('nothing: ON'), lambda: _async_r('nothing: OFF'))


def _transform_key(key):
    if hasattr(key, 'char'):
        return key.char.lower()
    return _shift_keys.get(key, key)


def _is_mod_key(key):
    return key in _mod_keys


Chords: Dict[FrozenSet, OnOff]


class Chords(dict):
    """
    easy storage for chords of keys pressed

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


_test_chords = Chords()
_test_chords[{Key.shift, Key.down}] = OnOff(lambda: _async_r('down: ON'), lambda: _async_r('down: OFF'))


def _lock_and_transform(func):
    """
    decorator: used with `KeySet`
    lock the function call and transform the key passed in to the correct format
    """

    @wraps(func)
    def wrapper(self, key):
        with self._lock:
            func(self, _transform_key(key))

    return wrapper


class KeySet:
    """thread-safe way to store key presses/chords of keys pressed"""

    def __init__(self):
        self.s = set()
        self._lock = RLock()

    @property
    def frozen(self):
        return frozenset(self.s)

    @_lock_and_transform
    def add(self, key):
        self.s.add(key)

    @_lock_and_transform
    def remove(self, key):
        with suppress(Exception):
            self.s.remove(key)

    def clear(self):
        with self._lock:
            self.s.clear()

    @_lock_and_transform
    def __contains__(self, key):
        return key in self.s

    def __str__(self):
        return str(self.s)

    def __repr__(self):
        return repr(self.s)


class SplitKeys:
    """
    split keys up between modifier keys and regular keys

    same interface as `KeySet`
    """

    def __init__(self):
        self._keys = KeySet()
        self._mod_keys = KeySet()

    def _proper_set(self, key):
        if _is_mod_key(key):
            return self._mod_keys
        return self._keys

    def add(self, key):
        self._proper_set(key).add(key)

    def remove(self, key):
        self._proper_set(key).remove(key)

    def clear(self):
        self._keys.clear()

    @property
    def frozen(self):
        return frozenset(self._keys.s | self._mod_keys.s)

    def __contains__(self, item):
        return item in self._keys or item in self._mod_keys

    def __str__(self):
        return str(self.frozen)

    def __repr__(self):
        return repr(self.frozen)


@asynccontextmanager
async def listen(on_press, on_release, stop_or_join='stop'):
    """listen to keyboard presses/releases"""
    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()
    try:
        yield listener
    finally:
        await asyncio.get_event_loop().run_in_executor(None, getattr(listener, stop_or_join))


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


class AsyncThreadEvent:
    """event that can be used from both threads and event loops"""

    def __init__(self):
        self._q = Queue()
        self._pending = False

    def set(self):
        if not self._pending:
            self._pending = True
            self._q.put_nowait(None)

    async def wait(self):
        return await asyncio.get_event_loop().run_in_executor(None, self._q.get)

    def clear(self):
        self._pending = False


class SimpleParser:
    """
    parse and group inputs every `debounce_secs`
    """

    def __init__(self, debounce_secs=.02):
        self._keys = SplitKeys()
        self._debounce_s = debounce_secs
        self._process_pending: AsyncThreadEvent = AsyncThreadEvent()

    def _on_press(self, key):
        self._keys.add(key)
        self._process_pending.set()

    def _on_release(self, key):
        if key == Key.esc:
            self._keys.clear()
            self._process_pending.set()
            return False  # stops listener
        if _is_mod_key(key):
            self._keys.remove(key)

    async def _process(self, listener: keyboard.Listener) -> AsyncIterable[FrozenSet]:
        while True:
            await self._process_pending.wait()
            self._process_pending.clear()

            if not listener.running:
                break

            await asyncio.sleep(self._debounce_s)
            yield self._keys.frozen
            self._keys.clear()

    async def read_chars(self):
        async with listen(self._on_press, self._on_release, stop_or_join='join') as listener:
            async for keys in self._process(listener):
                print(keys)


if __name__ == '__main__':
    asyncio.run(SimpleParser().read_chars())
# asyncio.run(run_parse_input(test_chords))
# controller = keyboard.Controller()
# controller.press('a')
# controller.press(keyboard.Key.shift_r)
# controller.release(keyboard.Key.shift_r)
# controller.press('a')
# listener.join()
