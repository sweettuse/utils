import asyncio
from enum import Enum
from functools import lru_cache
from pathlib import Path

import uvloop
from misty_py.utils import json_obj

__all__ = 'parse_config', 'UserType', 'ConvType', 'async_run', 'incident_store_path'

uvloop.install()

SLACK_CONF_DIR = Path('~/.slack').expanduser()
SLACK_CONF = SLACK_CONF_DIR / 'config'
_loop: uvloop.Loop = asyncio.get_event_loop()
incident_store_path = str(SLACK_CONF_DIR / 'incident_store.pkl')


@lru_cache()
def parse_config(conf=SLACK_CONF):
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
        return f.result()
    else:
        return _loop.run_until_complete(cor)
