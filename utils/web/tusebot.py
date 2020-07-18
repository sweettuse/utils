import asyncio
from concurrent.futures.thread import ThreadPoolExecutor
from io import BytesIO
from pathlib import Path

from lifxlan3 import timer
from more_itertools import first
from sanic.response import text

from utils.slack_api import parse_config
from utils.slack_api.big_emoji import resize_image, resize_gif
from utils.slack_api.text_to_emoji import text_to_emoji
from utils.web.core import register_cmd, SlackInfo, slack_api, app, init_slack_api, gen_help_str, send_to_channel, \
    request_in_loop, no_dm

__author__ = 'acushner'

from utils.web.incident import IncidentInfo, init_incident_store

_admins = parse_config().admin_id_name_map
DEFAULT_MULT = 6.
MAX_MULT = 15.


@register_cmd
@no_dm
async def embiggen(si: SlackInfo):
    """emoji [size_multiple]
    [size_multiple]: multiple to scale up/down emoji size by"""
    emoji, *rest = si.argstr.split()
    mult = min(MAX_MULT, float(first(rest, DEFAULT_MULT)))
    if mult <= 0:
        return text(f'invalid mult: {mult}')

    all_emoji = await slack_api.get_emoji()
    try:
        emoji_url = all_emoji[emoji.strip(':')]
    except KeyError:
        return text(f"unable to find emoji {emoji!r} - this usually occurs because "
                    f"you're trying to use a built-in emoji, and this only works on custom emoji due "
                    f"to slack not including built-in emoji in its `emoji_list` call.")

    async def _embiggen_helper():
        resp = await request_in_loop('GET', emoji_url)
        data = BytesIO(resp.content)

        if emoji_url.endswith('gif'):
            filetype = 'gif'
            res = resize_gif(data, mult)
        else:
            filetype = 'jpeg'
            res = resize_image(data, mult)

        filename = f'embiggened {emoji.strip(":")!r} for {si.user_name}'
        await slack_api.client.files_upload(file=res.read(), channels=si.channel_id, filetype=filetype,
                                            filename=filename)

    # TODO: run in process
    asyncio.create_task(_embiggen_helper())
    return text(f'emoji: {emoji} mult: {mult}')


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
    await send_to_channel(si, *msgs)


@register_cmd
async def emojify_i(si: SlackInfo):
    """text [emoji]
    inverted form of _*emojify*_"""
    await emojify(si, reverse=True)


@register_cmd
async def _ping(si: SlackInfo):
    """text
    stupid test function"""
    await send_to_channel(si, f'sending {si.argstr!r} 1', f'sending {si.argstr!r} 2')


@register_cmd
async def spam(si: SlackInfo):
    """text [--delay=delay_in_secs]
    send each word in _text_ to channel, uppercase, one word per line
    optional delay: how many secs between sending each line"""
    await send_to_channel(si, *map(str.upper, si.argstr.split()))


@register_cmd(name='help')
async def help_(_=None):
    """
    show this message"""
    return text(gen_help_str())


_incident_store = init_incident_store()


@register_cmd
@no_dm
async def incident(si: SlackInfo):
    """
    desc [--list] [--del=id]
        register incident that occurred. e.g. 'an excel drag-down issue', 'a considerable brain fart'
        this will update the channel daily on how many days it's been since this issue, starting from today
        optional: with _--list_: show all incidents you've created
        optional: with _--del=id_: delete incident with _id_
    """
    is_admin = si.user_id in _admins and 'basic' not in si.flags

    if 'list' in si.flags:
        if is_admin:
            incidents = map(str, _incident_store.incidents.values())
        else:
            incidents = map(_format_incident_info, _incident_store.by_user_id(si.user_id))
        res = '*your incidents:*\n\n' + ('\n'.join(incidents) or 'no incidents found')
        return text(res)

    elif 'del' in si.kwargs:
        try:
            ii = _incident_store.rm(si.kwargs['del'], si.user_id, is_admin=is_admin)
            return text(f'removed {_format_incident_info(ii)}')
        except (ValueError, PermissionError):
            return text(f"error: either id {si.kwargs['del']!r} doesn't exist in the system "
                        f"or you don't have permission to remove that")

    res = _incident_store.add(si.user_name, si.user_id, si.channel_id, si.argstr)
    if res:
        return text(_format_incident_info(res))
    return text('must pass in a non-empty description')


def _format_incident_info(ii: IncidentInfo):
    return f'*{ii.id}*: _{repr(ii.incident)}_'


def _run_server():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    server = app.create_server(host='0.0.0.0', port=31415, return_asyncio_server=True)
    # server = app.create_server(host='127.0.0.1', port=31415, return_asyncio_server=True)
    loop.run_until_complete(init_slack_api())
    loop.create_task(server)
    loop.run_forever()


def __main():
    _run_server()


if __name__ == '__main__':
    __main()
