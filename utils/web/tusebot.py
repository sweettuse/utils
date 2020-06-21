import asyncio
from concurrent.futures import ThreadPoolExecutor
from functools import partial, lru_cache
from typing import NamedTuple, Optional, Any, Callable

from misty_py.utils import json_obj
from more_itertools import first
from sanic import Sanic
from sanic.response import empty, text

from utils.slack_api import UserType
from utils.slack_api.api import SlackAPI
from utils.slack_api.text_to_emoji import text_to_emoji

app = Sanic(__name__)

sanic_form = {'token': ['6fjPtJCoLaAdfpgGC0VHvKLE'], 'team_id': ['T03UGBWK0'], 'team_domain': ['xaxis'],
              'channel_id': ['G012L1HJQCX'], 'channel_name': ['privategroup'], 'user_id': ['U09HB810D'],
              'user_name': ['adam.cushner'], 'command': ['/tuse'], 'text': ['test'],
              'response_url': ['https://hooks.slack.com/commands/T03UGBWK0/1219939910880/NNwD1GRbfpXMxLRSkCbo5xOo'],
              'trigger_id': ['1181361063527.3968404646.1edcd81f4f78cefdaafc1df868a9a656']}

_cmds = {}
_pool = ThreadPoolExecutor(32)
_CMD = '/tuse'


class SlackInfo(NamedTuple):
    """store request information from slack"""
    cmd: str
    argstr: str
    data: json_obj

    def __getattr__(self, item):
        return self.data[item]

    @classmethod
    def from_data(cls, data):
        data = _flatten_form(data)
        cmd, *argstr = data.text.strip().split(maxsplit=1)
        return cls(cmd, first(argstr, ''), data)


def register_cmd(func: Optional[Callable[[SlackInfo], Any]] = None, *, name: Optional[str] = None):
    """register cmd to be accessible from slack command

    if passed a name, use that as cmd name, otherwise just use name of function"""
    if not func:
        return partial(register_cmd, name=name)

    if name is None:
        name = func.__name__

    name = name.lower()
    _cmds[name] = func

    return func


def _flatten_form(form):
    """transform {k: [v]} -> {k: v}"""
    return json_obj((k, first(v) if len(v) == 1 else v) for k, v in form.items())


@app.route('/slack', methods=['POST'])
async def _dispatch(request):
    """main entry point for slack requests

    will inspect form and dispatch to the appropriate registered cmd"""
    si = SlackInfo.from_data(request.form)
    print(si)
    try:
        cmd = _cmds[si.cmd]
    except KeyError:
        return text(f'invalid cmd {si.cmd!r}\n\n{_gen_help_str()}')

    res = await cmd(si)
    return empty() if res is None else res


async def _send_to_channel(channel, *msgs):
    """send msgs to channel in the background"""

    async def _helper():
        for msg in msgs:
            await _slack_api.post_message(channel, text=msg)

    asyncio.create_task(_helper())


@register_cmd
async def emojify(si: SlackInfo, *, reverse=False):
    """text [emoji]
    transform text into emoji representation in slack"""
    data, *emoji = si.argstr.rsplit(maxsplit=1)
    emoji = first(emoji, '')
    if not (emoji.startswith(':') and emoji.endswith(':')):
        data = f'{data} {emoji}'.rstrip()
        emoji = await _slack_api.random_emoji

    msgs = text_to_emoji(data, emoji, reverse=reverse)
    await _send_to_channel(si.channel_id, *msgs)


@register_cmd
async def emojify_i(si: SlackInfo):
    """text [emoji]
    inverted form of `emojify`"""
    await emojify(si, reverse=True)


@register_cmd
async def ping(si: SlackInfo):
    """text
    stupid test function"""
    await _send_to_channel(si.channel_id, f'sending {si.argstr!r} 1', f'sending {si.argstr!r} 2')


@register_cmd
async def spam(si: SlackInfo):
    """text
    send each word in `text` to channel, uppercase, one word per line"""
    await _send_to_channel(si.channel_id, *map(str.upper, si.argstr.split()))


@register_cmd(name='help')
async def help_(_: SlackInfo):
    """
    show this message"""
    return text(f'what can _*tuse*_ do for you?\n\n{_gen_help_str()}')


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


@lru_cache(1)
def _gen_help_str():
    return '\n'.join(f'{_CMD} _*{cmd}*_ {fn.__doc__}'
                     for cmd, fn in sorted(_cmds.items())
                     if not cmd.startswith('_'))


if __name__ == '__main__':
    # print(_gen_help_str())
    _run_server()
