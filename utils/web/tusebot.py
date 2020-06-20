import asyncio
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from typing import NamedTuple, Optional, Any, Callable

from misty_py.utils import json_obj
from more_itertools import first
from sanic import Sanic
from sanic.response import empty

from utils.slack_api import UserType
from utils.slack_api.api import SlackAPI
from utils.slack_api.text_to_emoji import text_to_emoji

app = Sanic(__name__)

mock_form = dict([('token', '6fjPtJCoLaAdfpgGC0VHvKLE'), ('team_id', 'T03UGBWK0'), ('team_domain', 'xaxis'),
                  ('channel_id', 'D19MABAKC'), ('channel_name', 'directmessage'), ('user_id', 'U09HB810D'),
                  ('user_name', 'adam.cushner'), ('command', '/tuse'), ('text', 'emojify yo man :lee:'),
                  ('response_url', 'https://hooks.slack.com/commands/T03UGBWK0/1201237651329/Iy4HNul5nFY4VnyLP7fCa3B3'),
                  ('trigger_id', '1173871285479.3968404646.627c7ec9a1973dbbe2f467f992da46df')])

sanic_form = {'token': ['6fjPtJCoLaAdfpgGC0VHvKLE'],
              'team_id': ['T03UGBWK0'],
              'team_domain': ['xaxis'],
              'channel_id': ['G012L1HJQCX'],
              'channel_name': ['privategroup'],
              'user_id': ['U09HB810D'],
              'user_name': ['adam.cushner'],
              'command': ['/tuse'],
              'text': ['test'],
              'response_url': ['https://hooks.slack.com/commands/T03UGBWK0/1219939910880/NNwD1GRbfpXMxLRSkCbo5xOo'],
              'trigger_id': ['1181361063527.3968404646.1edcd81f4f78cefdaafc1df868a9a656']}

_services = {}
_pool = ThreadPoolExecutor(32)


class SlackInfo(NamedTuple):
    cmd: str
    argstr: str
    data: json_obj

    def __getattr__(self, item):
        return self.data[item]

    @classmethod
    def from_data(cls, data):
        data = json_obj(data)
        cmd, *argstr = data.text.strip().split(maxsplit=1)
        return cls(cmd, first(argstr, ''), data)


def register_service(func: Optional[Callable[[SlackInfo], Any]] = None, *, name: Optional[str] = None):
    """register service to be accessible from slack command

    if passed a name, use that as service name, otherwise just use name of function"""
    if not func:
        return partial(register_service, name=name)

    if name is None:
        name = func.__name__

    name = name.lower()
    _services[name] = func

    return func


def _flatten_form(form):
    """transform {k: [v]} -> {k: v}"""
    return json_obj((k, first(v) if len(v) == 1 else v) for k, v in form.items())


@app.route('/slack', methods=['POST'])
async def _dispatch(request):
    """main entry point for slack requests

    will inspect form and dispatch to the appropriate registered service"""
    form = _flatten_form(request.form)
    si = SlackInfo.from_data(form)
    print(si)
    print(f'dispatching to {si.cmd!r}')
    res = await _services[si.cmd](si)
    return empty() if res is None else res


async def _send_to_channel(channel, *msgs):
    """send msgs to channel in the background"""

    async def _helper():
        for msg in msgs:
            await _slack_api.post_message(channel, text=msg)

    asyncio.create_task(_helper())


@register_service
async def emojify(si: SlackInfo, reverse=False):
    data, *emoji = si.argstr.rsplit(maxsplit=1)
    emoji = first(emoji, '')
    if not (emoji.startswith(':') and emoji.endswith(':')):
        data = f'{data} {emoji}'.rstrip()
        emoji = await _slack_api.random_emoji

    msgs = text_to_emoji(data, emoji, reverse=reverse)
    await _send_to_channel(si.channel_id, *msgs)


@register_service
async def emojify_r(si: SlackInfo):
    await emojify(si, True)


@register_service
async def ping(si: SlackInfo):
    await _send_to_channel(si.channel_id, f'sending {si.argstr!r} 1', f'sending {si.argstr!r} 2')


@register_service
async def spam(si: SlackInfo):
    await _send_to_channel(si.channel_id, *map(str.upper, si.argstr.split()))


# ======================================================================================================================


_slack_api: SlackAPI = None


async def _init_slack_api():
    global _slack_api
    _slack_api = (await SlackAPI.from_user_type(UserType.bot))


def _run_server():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    server = app.create_server(host="0.0.0.0", port=31415, return_asyncio_server=True)
    loop.create_task(_init_slack_api())
    loop.create_task(server)
    loop.run_forever()


if __name__ == '__main__':
    _run_server()
