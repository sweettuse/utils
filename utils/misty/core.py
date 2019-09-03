import asyncio
from concurrent.futures.thread import ThreadPoolExecutor
from contextlib import suppress, asynccontextmanager
from functools import partial, wraps
from typing import Callable, Awaitable, Any

import uvloop
from misty_py.api import MistyAPI

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
