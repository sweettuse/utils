import asyncio
import os
from concurrent.futures.thread import ThreadPoolExecutor
from contextlib import contextmanager, suppress
from functools import partial, wraps
from itertools import count
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


class Routine(json_obj):
    """used to programmatically store and create audio for various routines"""

    def __new__(cls, *args, **kwargs):
        return dict.__new__(cls)

    def __init__(self, routine_prefix):
        super().__init__()
        self.routine_prefix = routine_prefix

    def generate(self, *keys):
        asyncio.run(self._generate(*keys))

    async def _generate(self, *keys):
        """go to google, generate audio, and upload to misty"""
        from utils.ggl.ggl_async import atext_to_speech
        filenames = self.get_filenames(*keys)
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

    @staticmethod
    def _to_misty():
        pass

    def get_filenames(self, *keys) -> Dict[str, str]:
        keys = (set(keys) or set(self)) - {'routine_prefix'}
        prefix = f'{self.routine_prefix}_' if self.routine_prefix else ''
        return {f'{prefix}{name}_{n}.wav': sentence
                for name in keys
                for n, sentence in zip(count(), always_iterable(self[name]))}


def __main():
    pass
    # print(asyncio.run(get_actuator_positions()))
    # asyncio.run(say("hey philip, how's it going?"))


if __name__ == '__main__':
    __main()
