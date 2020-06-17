import asyncio
import random
from functools import partial
from typing import NamedTuple, Optional, Any, Callable

from flask import Flask, request
from misty_py.utils import json_obj

from utils.slack_api import UserType
from utils.slack_api.api import SlackAPI
from utils.slack_api.text_to_emoji import text_to_emoji

app = Flask(__name__)

mock_form = dict([('token', '6fjPtJCoLaAdfpgGC0VHvKLE'), ('team_id', 'T03UGBWK0'), ('team_domain', 'xaxis'),
                  ('channel_id', 'D19MABAKC'), ('channel_name', 'directmessage'), ('user_id', 'U09HB810D'),
                  ('user_name', 'adam.cushner'), ('command', '/tuse'), ('text', 'emojify yo man :lee:'),
                  ('response_url', 'https://hooks.slack.com/commands/T03UGBWK0/1201237651329/Iy4HNul5nFY4VnyLP7fCa3B3'),
                  ('trigger_id', '1173871285479.3968404646.627c7ec9a1973dbbe2f467f992da46df')])

_services = {}
_slack_emoji = []


def _init_emoji():
    async def helper():
        sa = await SlackAPI.from_user_type(UserType.bot)
        _slack_emoji[:] = list(await sa.get_emoji())

    asyncio.run(helper())


_init_emoji()


class SlackInfo(NamedTuple):
    cmd: str
    argstr: str
    data: json_obj

    @classmethod
    def from_data(cls, data):
        data = json_obj(data)
        return cls(*data.text.strip().split(maxsplit=1), data)


def register_service(func: Optional[Callable[[SlackInfo], Any]] = None, *, name: Optional[str] = None):
    if not func:
        return partial(register_service, name=name)

    if name is None:
        name = func.__name__

    _services[name] = func
    return func


@app.route('/slack/<service>', methods=['POST'])
def _dispatch(service):
    return _services[service](SlackInfo.from_data(request.form))


@register_service
def emojify(si: SlackInfo):
    text, emoji = si.argstr.rsplit(maxsplit=1)
    if not (emoji.startswith(':') and emoji.endswith(':')):
        emoji = random.choice(_slack_emoji)
    return text_to_emoji(text, emoji)


