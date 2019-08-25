import asyncio
import os
from concurrent.futures.thread import ThreadPoolExecutor
from contextlib import contextmanager, suppress, asynccontextmanager
from functools import partial, wraps
from itertools import count
from random import choice
from typing import Dict, Callable, Awaitable, Any

import uvloop
from misty_py.api import MistyAPI, json_obj
from misty_py.misty_ws import EventCallback
from misty_py.subscriptions import SubType, Sub, SubPayload, Actuator
from misty_py.utils import wait_in_order
from more_itertools import always_iterable

from utils.ggl.google_clients import AudioEncoding

uvloop.install()

api = MistyAPI()
__author__ = 'acushner'

pool = ThreadPoolExecutor(32)


@asynccontextmanager
async def cancel(*coros):
    """run tasks until block returns, then cancel"""
    tasks = [asyncio.create_task(c) for c in coros]
    try:
        yield
    finally:
        for t in tasks:
            with suppress(Exception):
                t.cancel()


async def run_in_executor(func, *args, **kwargs):
    f = partial(func, *args, **kwargs)
    return await asyncio.get_running_loop().run_in_executor(pool, f)


def make_async(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        return await run_in_executor(func, *args, **kwargs)

    return wrapper


@contextmanager
def named_temp_file(name, perms='wb'):
    try:
        with open(f'/tmp/{name}', perms) as f:
            yield f
    finally:
        with suppress(Exception):
            os.remove(f.name)


def first(v):
    return next(iter(v))


async def repeat(coro: Callable[[], Awaitable[Any]], wait_secs=0):
    while True:
        await coro()
        if wait_secs > 0:
            await asyncio.sleep(wait_secs)


class _AudioOption(dict):
    @property
    def random(self):
        return choice(list(self.keys()))

    async def play(self, how_long_secs=None):
        await api.audio.play(self.random, how_long_secs=how_long_secs, blocking=True)

    def __str__(self):
        return f'_TTSOption({self.name}: {"|".join(s[:20] for s in self.values)}'

    def __getitem__(self, item):
        if isinstance(item, int):
            return list(self.keys())[item]
        return super().__getitem__(item)

    def __await__(self):
        return self.play().__await__()

    def __hash__(self):
        return hash(str(self.items()))

    def __eq__(self, other):
        return hash(self) == hash(other)


class _TTSOption(_AudioOption):
    def __init__(self, prefix, name, value_or_values):
        self.name = name
        vals = self.values = tuple(always_iterable(value_or_values))
        filenames = self._init_filenames(prefix, name, vals)
        super().__init__(zip(filenames, vals))

    @staticmethod
    def _init_filenames(prefix, name, values):
        prefix = f'{prefix}_' if prefix else ''
        return (f'{prefix}{name}_{n}.wav' for n in range(len(values)))


class Routine:
    """
    used to programmatically store text, create audio from that text, and upload to misty
    """

    def __init__(self, routine_prefix):
        self._routine_prefix = routine_prefix

    def generate(self, *names):
        """run text-to-speech and upload to misty"""
        asyncio.run(self._generate(*names))

    async def _generate(self, *names):
        """go to google, generate audio, and upload to misty"""
        from utils.ggl.ggl_async import atext_to_speech
        filenames = self.get_filenames(*names)
        coros = (atext_to_speech(s, AudioEncoding.wav) for s in filenames.values())
        out = dict(zip(filenames, await asyncio.gather(*coros, return_exceptions=True)))
        coros = (self._upload(fn, data) for fn, data in out.items())
        res = await wait_in_order(*coros)
        return {r for r in res if r}

    @staticmethod
    async def _upload(fn, data):
        if isinstance(data, Exception):
            return fn
        await api.audio.upload(fn, data=data)

    def get_filenames(self, *names) -> Dict[str, str]:
        names = set(names or self)
        return {fn: val for name in names for fn, val in self[name].items()}

    def __setattr__(self, name, value):
        if name.startswith('_'):
            return super().__setattr__(name, value)
        return super().__setattr__(name, _TTSOption(self._routine_prefix, name, value))

    def __getitem__(self, name):
        return getattr(self, name)

    def __iter__(self):
        yield from (name for name, v in vars(self).items() if isinstance(v, _TTSOption))


def __main():
    pass
    # print(asyncio.run(get_actuator_positions()))
    # asyncio.run(say("hey philip, how's it going?"))


if __name__ == '__main__':
    __main()
