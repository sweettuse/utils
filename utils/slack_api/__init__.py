import asyncio
import time
from enum import Enum
from pathlib import Path
from threading import Event
from typing import NamedTuple

import uvloop
from misty_py.utils import json_obj

uvloop.install()

_CONF_DIR = Path('~/.slack').expanduser()
_CONF = _CONF_DIR / 'config'

_loop: uvloop.Loop = asyncio.get_event_loop()

__all__ = 'parse_config', 'UserType', 'ConvType', 'async_run', 'ssl_dict'

ssl_dict = dict(cert=str(_CONF_DIR / 'cert.pem'), key=str(_CONF_DIR / 'key.pem'))


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
