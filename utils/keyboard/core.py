import asyncio
from contextlib import suppress, asynccontextmanager
from functools import wraps
from queue import Queue
from threading import RLock

from pynput import keyboard
from pynput.keyboard import Key

__author__ = 'acushner'

_keys_with_directions = {Key.alt_l, Key.alt_r, Key.alt_gr, Key.cmd_l, Key.cmd_r, Key.ctrl_l, Key.ctrl_r, Key.shift_l,
                         Key.shift_r}

MOD_KEYS = {Key.shift, Key.cmd, Key.ctrl, Key.esc, Key.alt}


# MOD_KEYS.update(getattr(Key, f'f{n}') for n in range(1, 21))


def _transform_key(key):
    """keys from pynput either have a `char` attribute or they don't"""
    if hasattr(key, 'char'):
        return key.char.lower()
    if key in _keys_with_directions:
        return getattr(key, key.name.split('_')[0])
    return key


def is_mod_key(key):
    return key in MOD_KEYS


def _lock_and_transform(func):
    """
    decorator used with `KeySet`
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
        if is_mod_key(key):
            return self._mod_keys
        return self._keys

    def add(self, key):
        self._proper_set(key).add(key)

    def remove(self, key):
        self._proper_set(key).remove(key)

    def clear_regular(self):
        self._keys.clear()

    def clear_mod(self):
        self._mod_keys.clear()

    def clear(self):
        self.clear_regular()
        self.clear_mod()

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
