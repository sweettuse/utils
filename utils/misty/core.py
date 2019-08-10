import asyncio
import os
from concurrent.futures.thread import ThreadPoolExecutor
from contextlib import contextmanager, suppress
from functools import partial
from pathlib import Path
from tempfile import NamedTemporaryFile

import uvloop
from misty_py.api import MistyAPI

from utils.google_clients import text_to_speech
uvloop.install()

api = MistyAPI('http://192.168.86.20')
__author__ = 'acushner'

pool = ThreadPoolExecutor(32)


async def run_in_executor(func, *args, **kwargs):
    f = partial(func, *args, **kwargs)
    return await asyncio.get_running_loop().run_in_executor(pool, f)


@contextmanager
def named_temp_file(name):
    try:
        with open(f'/tmp/{name}', 'wb') as f:
            yield f
    finally:
        pass
        # with suppress(Exception):
        #     os.remove(f.name)


async def say(s):
    clip = await run_in_executor(text_to_speech, s)
    with named_temp_file('from_google.mp3') as f:
        f.write(clip)
        await api.audio.upload(f.name)
        print('done1')
    print('done')


def __main():
    # asyncio.run(say('hello? is this thing on?'))
    asyncio.run(say("what's up, buddy? i hope this api audio complete thing works"))


if __name__ == '__main__':
    __main()
