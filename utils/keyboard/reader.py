import asyncio
from typing import FrozenSet, AsyncIterable

import uvloop
from pynput import keyboard
from pynput.keyboard import Key

from utils.keyboard.core import is_mod_key, SplitKeys, listen, AsyncThreadEvent

uvloop.install()


class SimpleParser:
    """
    parse and group inputs every `debounce_secs`
    """

    def __init__(self, debounce_secs=.04):
        self._keys = SplitKeys()
        self._debounce_s = debounce_secs
        self._process_pending = AsyncThreadEvent()

    def _on_press(self, key):
        self._keys.add(key)
        self._process_pending.set()

    def _on_release(self, key):
        if key == Key.esc:
            self._keys.clear()
            self._process_pending.set()
            return False  # stop listener

        if is_mod_key(key):
            self._keys.remove(key)

    async def _process(self, listener: keyboard.Listener) -> AsyncIterable[FrozenSet]:
        """handle the legwork of processing events after `_debounce_s`"""
        while listener.running:
            await self._process_pending.wait()
            if not listener.running:
                break
            await asyncio.sleep(self._debounce_s)

            frozen = self._keys.frozen
            self._keys.clear_regular()
            self._process_pending.clear()
            yield frozen

    async def read_chars(self):
        """read chars every `_debounce_s` seconds and yield the frozenset of all keys pushed"""
        async with listen(self._on_press, self._on_release, stop_or_join='join') as listener:
            async for keys in self._process(listener):
                yield keys

    async def display_chars(self):
        """useful for debugging"""
        async for keys in self.read_chars():
            print(keys)


if __name__ == '__main__':
    asyncio.run(SimpleParser().display_chars())
