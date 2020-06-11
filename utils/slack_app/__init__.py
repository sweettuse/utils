import asyncio
from enum import Enum
from pathlib import Path

import uvloop
from misty_py.utils import json_obj

uvloop.install()

_CONF = Path('~/.slack/config').expanduser()

_loop = asyncio.get_event_loop()

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


class ConvType:
    public_channel = 'public_channel'
    private_channel = 'private_channel'
    mpim = 'mpim'
    im = 'im'


def async_run(cor):
    _loop.run_until_complete(cor)
