import asyncio

from more_itertools import first
from sanic.response import text

from utils.slack_api import ssl_dict
from utils.slack_api.text_to_emoji import text_to_emoji
from utils.web.core import register_cmd, SlackInfo, slack_api, app, init_slack_api, gen_help_str, _cmds

__author__ = 'acushner'


@register_cmd
async def emojify(si: SlackInfo, *, reverse=False):
    """text [emoji]
    transform text into emoji representation in slack"""
    data, *emoji = si.argstr.rsplit(maxsplit=1)
    emoji = first(emoji, '')
    if not (emoji.startswith(':') and emoji.endswith(':')):
        data = f'{data} {emoji}'.rstrip()
        emoji = await slack_api.random_emoji

    msgs = text_to_emoji(data, emoji, reverse=reverse)
    await _send_to_channel(si.channel_id, *msgs)


@register_cmd
async def emojify_i(si: SlackInfo):
    """text [emoji]
    inverted form of _*emojify*_"""
    await emojify(si, reverse=True)


@register_cmd
async def _ping(si: SlackInfo):
    """text
    stupid test function"""
    await _send_to_channel(si.channel_id, f'sending {si.argstr!r} 1', f'sending {si.argstr!r} 2')


@register_cmd
async def spam(si: SlackInfo):
    """text [--delay=delay_in_secs]
    send each word in _text_ to channel, uppercase, one word per line"""
    delay = int(si.kwargs.get('delay', 0))
    await _send_to_channel(si.channel_id, *map(str.upper, si.argstr.split()), delay=delay)


@register_cmd
async def _days_since(si: SlackInfo):
    """desc
    register incident that occurred. e.g. 'an excel drag-down issue', 'a considerable brain fart'
    this will update the channel daily on how many days it's been since this issue"""


@register_cmd(name='help')
async def help_(_=None):
    """
    show this message"""
    return text(gen_help_str())


async def _send_to_channel(channel, *msgs, delay=0):
    """send msgs to channel in the background"""

    async def _helper():
        for msg in msgs:
            await slack_api.post_message(channel, text=msg)
            if delay > 0:
                await asyncio.sleep(delay)

    asyncio.create_task(_helper())


def _run_server(*, enable_ssl=False):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    ssl = ssl_dict if enable_ssl else None
    server = app.create_server(host='0.0.0.0', port=31415, return_asyncio_server=True, ssl=ssl)
    loop.run_until_complete(init_slack_api())
    loop.create_task(server)
    loop.run_forever()


if __name__ == '__main__':
    _run_server(enable_ssl=False)
