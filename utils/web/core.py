import asyncio
import hmac
import time
from concurrent.futures.thread import ThreadPoolExecutor
from functools import partial, lru_cache, wraps
from hashlib import sha256
from textwrap import dedent
from typing import Optional, Any, Callable, Dict

import requests
from misty_py.utils import json_obj, asyncpartial
from sanic import Sanic
from sanic.response import empty, text

from utils.slack_api import UserType, parse_config
from utils.slack_api.api import SlackAPI
from utils.web.slack_info import SlackInfo

app = Sanic(__name__)

_sanic_form = {'token': ['6fjPtJCoLaAdfpgGC0VHvKLE'], 'team_id': ['T03UGBWK0'], 'team_domain': ['xaxis'],
               'channel_id': ['G012L1HJQCX'], 'channel_name': ['privategroup'], 'user_id': ['U09HB810D'],
               'user_name': ['adam.cushner'], 'command': ['/tuse'], 'text': ['test'],
               'response_url': ['https://hooks.slack.com/commands/T03UGBWK0/1219939910880/NNwD1GRbfpXMxLRSkCbo5xOo'],
               'trigger_id': ['1181361063527.3968404646.1edcd81f4f78cefdaafc1df868a9a656']}

_cmds = {}
_CMD = '/tuse'


async def send_to_channel(si: SlackInfo, *msgs, delay_in_secs=0.):
    """send msgs to channel in the background"""

    delay_in_secs = max(0.0, float(si.kwargs.get('delay', delay_in_secs)))
    if si.channel_id.startswith('D'):
        # dealing with direct message: can only use response_url and send up to 5 messages total
        msg_args = (dict(json=dict(text=msg)) for msg in msgs[:5])
        request_fn = asyncpartial(request_in_loop, 'POST', si.response_url)
    else:
        msg_args = (dict(text=msg) for msg in msgs)
        request_fn = asyncpartial(slack_api.post_message, si.channel_id)

    async def _helper():
        for msg in msg_args:
            await request_fn(**msg)
            if delay_in_secs > 0:
                await asyncio.sleep(delay_in_secs)

    asyncio.create_task(_helper())


def register_cmd(func: Optional[Callable[[SlackInfo], Any]] = None,
                 *, name: str = ''):
    """decorator to register cmd to be accessible from slack command

    if passed a name, use that as cmd name, otherwise just use name of function"""
    if not func:
        return partial(register_cmd, name=name)

    if not name:
        name = func.__name__

    name = name.lower()
    _cmds[name] = func

    return func


def no_dm(func):
    """decorator that disallows cmds on direct messages"""

    @wraps(func)
    async def wrapper(si: SlackInfo, **kwargs):
        if si.channel_id.startswith('D'):
            return text(f"due to slack limitations, i can't run _{si.cmd!r}_ for direct messages")
        return await func(si, **kwargs)

    return wrapper


@lru_cache(1)
def gen_help_str():
    def _parse_doc(d):
        return dedent('\n'.join(l for l in d.splitlines() if l.strip()))

    help_str = '\n'.join(f'{_CMD} _*{cmd}*_ {_parse_doc(fn.__doc__)}'
                         for cmd, fn in sorted(_cmds.items())
                         if not cmd.startswith('_'))

    return f'unloose the *tuse*:\n\n{help_str}'


# @app.route('/test', methods=['POST'])
# async def inspect(request):
#     breakpoint()


@app.route('/slack', methods=['POST'])
async def _dispatch(request):
    """main entry point for slack requests

    will inspect form and dispatch to the appropriate registered cmd"""
    if not _validate_message(request):
        return text("i don't think so", status=401)

    si = SlackInfo.from_form_data(request.form)
    print(si)
    try:
        cmd = _cmds[si.cmd]
    except KeyError:
        return text(f'invalid cmd _{si.cmd!r}_\n\n{gen_help_str()}')

    res = await cmd(si)
    return empty() if res is None else res


def _validate_message(request):
    ts = request.headers['x-slack-request-timestamp']
    if abs(time.time() - int(ts)) > 10:
        print('message too late')
        return False

    sig = request.headers['x-slack-signature']
    body = request.body.decode()
    return sig == 'v0=' + hmac.new(_signing_secret, f'v0:{ts}:{body}'.encode(), sha256).hexdigest()


async def request_in_loop(method, url, json=None,
                          *, _headers: Optional[Dict[str, str]] = None):
    """make requests work in asyncio"""
    req_kwargs = json_obj.from_not_none(json=json, headers=_headers)
    f = partial(requests.request, method, url, **req_kwargs)
    return await asyncio.get_running_loop().run_in_executor(_pool, f)


# ======================================================================================================================

class _SlackAPIProxy:
    def __getattribute__(self, item):
        return getattr(_slack_api, item)


slack_api: SlackAPI = _SlackAPIProxy()

_slack_api: SlackAPI = None
_signing_secret = parse_config().signing_secret.encode()
_pool = ThreadPoolExecutor(32)


async def init_slack_api():
    global _slack_api
    _slack_api = await SlackAPI.from_user_type(UserType.bot)
