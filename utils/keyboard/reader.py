import asyncio
from typing import FrozenSet, AsyncIterable, NamedTuple

import uvloop
from pynput import keyboard
from pynput.keyboard import Key

from utils.keyboard.core import is_mod_key, SplitKeys, listen, AsyncThreadEvent
from utils.keyboard.state import State

uvloop.install()


class SimpleParser:
    """
    parse and group inputs after `debounce_s` from first input of group
    """

    def __init__(self, debounce_s=.04, listener_stop_combo: FrozenSet = frozenset((Key.shift, Key.esc))):
        self._keys = SplitKeys()
        self._debounce_s = debounce_s
        self._process_pending = AsyncThreadEvent()
        self._listener_stop_combo = listener_stop_combo
        self._join_or_stop = 'stop'

    def _on_press(self, key):
        self._keys.add(key)
        self._process_pending.set()

    def _on_release(self, key):
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
            if self._listener_stop_combo <= frozen:
                break

            self._keys.clear_regular()
            self._process_pending.clear()
            yield frozen

    async def read_chars(self) -> AsyncIterable[FrozenSet]:
        """read chars every `_debounce_s` seconds and yield the frozenset of all keys pushed"""
        async with listen(self._on_press, self._on_release, stop_or_join=self._join_or_stop) as listener:
            async for keys in self._process(listener):
                yield keys

    async def display_chars(self):
        """useful for debugging"""
        async for keys in self.read_chars():
            print(keys)


class StateKeys(NamedTuple):
    state: State
    keys: frozenset


class StateParser(SimpleParser):

    def __init__(self, state: State, debounce_s=.04, listener_stop_combo: FrozenSet = frozenset((Key.esc,))):
        super().__init__(debounce_s, listener_stop_combo)
        self._state = state

    def _update_state(self, key) -> bool:
        self._state, used = self._state.parse(key)
        return bool(used)

    def _on_press(self, key):
        if not self._update_state(key):
            return super()._on_press(key)

    async def read_chars(self) -> AsyncIterable[StateKeys]:
        async for keys in super().read_chars():
            yield StateKeys(self._state, keys)


def _state_machine_run():
    machine = State('__root__', key_char_override=Key.esc)
    with State.create_machine(machine):
        head = State('head')
        pitch = head >> State('pitch')
        yaw = head >> State('yaw')
        roll = head >> State('roll')

        arms = State('arms')
        arms >> State('left')
        arms >> State('right')
        arms >> State('both')

    asyncio.run(StateParser(machine, listener_stop_combo=frozenset((Key.shift, Key.esc))).display_chars())


def __main():
    return _state_machine_run()
    asyncio.run(SimpleParser(listener_stop_combo=frozenset((Key.shift, Key.esc))).display_chars())


if __name__ == '__main__':
    __main()
