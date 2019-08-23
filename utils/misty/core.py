import asyncio
import os
from concurrent.futures.thread import ThreadPoolExecutor
from contextlib import contextmanager, suppress
from functools import partial, wraps
from typing import Dict, Callable, Awaitable, Any

import uvloop
from misty_py.api import MistyAPI
from misty_py.misty_ws import EventCallback
from misty_py.subscriptions import SubType, Sub, SubPayload, Actuator

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
def named_temp_file(name):
    try:
        with open(f'/tmp/{name}', 'wb') as f:
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


def __main():
    pass
    # print(asyncio.run(get_actuator_positions()))
    # asyncio.run(say("hey philip, how's it going?"))


if __name__ == '__main__':
    __main()
