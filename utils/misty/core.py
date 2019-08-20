import asyncio
import os
from concurrent.futures.thread import ThreadPoolExecutor
from contextlib import contextmanager, suppress
from functools import partial, wraps
from typing import Dict

import uvloop
from misty_py.api import MistyAPI
from misty_py.misty_ws import EventCallback
from misty_py.subscriptions import SubType, Sub, SubPayload, Actuator

from utils.ggl.google_clients import text_to_speech

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


async def say(s):
    clip = await run_in_executor(text_to_speech, s)
    with named_temp_file('from_google.mp3') as f:
        f.write(clip)
        await api.audio.upload(f.name)
        print('done1')
    await api.audio.play('from_google.mp3')
    print('done')


def first(v):
    return next(iter(v))


async def get_actuator_positions() -> Dict[Actuator, float]:
    res: Dict[Sub, float] = {}
    submitted = False

    async def _wait_one(sp: SubPayload):
        nonlocal expected_sub_ids
        if not submitted:
            return False
        expected_sub_ids -= {sp.sub_id}
        with suppress(Exception):
            res[sp.sub_id.sub] = sp.data.message.value
        await sp.sub_id.unsubscribe()
        return not expected_sub_ids

    ecb = EventCallback(_wait_one)

    expected_sub_ids = set(await api.ws.subscribe(SubType.actuator_position, ecb))
    submitted = True
    await ecb

    return {Actuator(first(sub.ec).value): v for sub, v in res.items()}


def __main():
    # print(asyncio.run(get_actuator_positions()))
    asyncio.run(say("hey philip, how's it going?"))


if __name__ == '__main__':
    __main()
