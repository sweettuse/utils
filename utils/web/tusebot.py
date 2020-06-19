import asyncio
import random
from functools import partial
from typing import NamedTuple, Optional, Any, Callable
from concurrent.futures import ThreadPoolExecutor

from flask import Flask, request
from misty_py.utils import json_obj
import requests

from utils.slack_api import UserType
from utils.slack_api.api import SlackAPI
from utils.slack_api.text_to_emoji import text_to_emoji
from more_itertools import first

app = Flask(__name__)

mock_form = dict([('token', '6fjPtJCoLaAdfpgGC0VHvKLE'), ('team_id', 'T03UGBWK0'), ('team_domain', 'xaxis'),
                  ('channel_id', 'D19MABAKC'), ('channel_name', 'directmessage'), ('user_id', 'U09HB810D'),
                  ('user_name', 'adam.cushner'), ('command', '/tuse'), ('text', 'emojify yo man :lee:'),
                  ('response_url', 'https://hooks.slack.com/commands/T03UGBWK0/1201237651329/Iy4HNul5nFY4VnyLP7fCa3B3'),
                  ('trigger_id', '1173871285479.3968404646.627c7ec9a1973dbbe2f467f992da46df')])

_services = {}
_slack_emoji = []
_pool = ThreadPoolExecutor(32)


# TODO: use slack secrets
#    - https://api.slack.com/authentication/verifying-requests-from-slack
# TODO: change to use https:
#    - integrate with slack ca_cert check
#    - https://blog.miguelgrinberg.com/post/running-your-flask-application-over-https
# TODO: run multithreaded
# TODO: split message smartly - slack does autosplitting so might end up with malformed lines on split
# TODO: store user requests for analysis
# TODO: add emoji from web
#    - resize automatically
# TODO: add hints/resources for sprintly tests
# TODO: any help with triage report?


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

    def __getattr__(self, item):
        return data[item]

    @classmethod
    def from_data(cls, data):
        data = json_obj(data)
        cmd, *argstr = data.text.strip().split(maxsplit=1)
        return cls(cmd, first(argstr, ''), data)


def register_service(func: Optional[Callable[[SlackInfo], Any]] = None, *, name: Optional[str] = None):
    if not func:
        return partial(register_service, name=name)

    if name is None:
        name = func.__name__

    name = name.lower()
    _services[name] = func

    return func


def _send_messages(response_url, *msgs, in_channel=True):
    """send multiple messages using a response url from a slack request"""
    addl = {}
    if in_channel:
        addl['response_type'] = 'in_channel'

    def to_send():
        for msg in msgs:
            requests.post(response_url, json={'text': msg, **addl})

    _pool.submit(to_send)
    return ''


@app.route('/slack', methods=['POST'])
def _dispatch():
    si = SlackInfo.from_data(request.form)
    print(f'dispatching to {si.cmd!r}')
    return _services[si.cmd](si)


@register_service
def emojify(si: SlackInfo, reverse=False):
    text, *emoji = si.argstr.rsplit(maxsplit=1)
    emoji = first(emoji, '')
    if not (emoji.startswith(':') and emoji.endswith(':')):
        text = f'{text} {emoji}'.strip()
        emoji = random.choice(_slack_emoji)
    return _send_messages(si.response_url, *text_to_emoji(text, emoji, reverse=reverse))


@register_service
def emojify_r(si: SlackInfo):
    return emojify(si, True)


@register_service
def ping(si: SlackInfo):
    return _send_messages(si.response_url, f'sending {si.argstr!r} 1', f'sending {si.argstr!r} 2')



