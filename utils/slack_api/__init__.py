import asyncio
import time
from enum import Enum
from pathlib import Path
from threading import Event
from typing import NamedTuple

import uvloop
from misty_py.utils import json_obj

uvloop.install()

_CONF = Path('~/.slack/config').expanduser()

_loop: uvloop.Loop = asyncio.get_event_loop()

__all__ = 'parse_config', 'UserType', 'ConvType', 'async_run'


def parse_config(conf=_CONF):
    res = json_obj()
    with open(conf) as f:
        exec(f.read(), res, res)
    del res['__builtins__']
    return res


class UserType(Enum):
    bot = 'bot_'
    user = ''


class ConvType(Enum):
    public_channel = 'public_channel'
    private_channel = 'private_channel'
    mpim = 'mpim'
    im = 'im'


def async_run(cor):
    if _loop.is_running():
        f = asyncio.run_coroutine_threadsafe(cor, _loop)
        f.result()
    else:
        _loop.run_until_complete(cor)
