import asyncio
from concurrent.futures.thread import ThreadPoolExecutor

from more_itertools import first
from sanic.response import text

from utils.slack_api import ssl_dict, parse_config
from utils.slack_api.text_to_emoji import text_to_emoji
from utils.web.core import register_cmd, SlackInfo, slack_api, app, init_slack_api, gen_help_str, send_to_channel

__author__ = 'acushner'

from utils.web.incident import IncidentInfo, init_incident_store

_admins = parse_config().admin_id_name_map


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
    delay = int(si.kwargs.get('delay', 0))
    await send_to_channel(si, *map(str.upper, si.argstr.split()), delay_in_secs=delay)


@register_cmd(name='help')
async def help_(_=None):
    """
    show this message"""
    return text(gen_help_str())


_incident_store = init_incident_store()


def _format_incident_info(ii: IncidentInfo):
    return f'*{ii.id}*: _{repr(ii.incident)}_'


@register_cmd
async def incident(si: SlackInfo):
    """
    desc [--list] [--del=id]
        register incident that occurred. e.g. 'an excel drag-down issue', 'a considerable brain fart'
        this will update the channel daily on how many days it's been since this issue, starting from today
        optional: with _--list_: show all incidents you've created
        optional: with _--del=id_: delete incident with _id_
    """
    if si.channel_id.startswith('D'):
        return text("due to slack limitations, i can't do this for direct messages")

    if 'list' in si.flags:
        if si.user_id in _admins and 'basic' not in si.flags:
            incidents = map(str, _incident_store.incidents.values())
        else:
            incidents = map(_format_incident_info, _incident_store.by_user_id(si.user_id))
        res = '*your incidents:*\n\n' + '\n'.join(incidents)
        return text(res or 'no incidents found for you')

    elif 'del' in si.kwargs:
        try:
            # TODO: make sure a user can remove only their own incidents
            ii = _incident_store.rm(si.kwargs['del'], si.user_id)
            return text(f'removed {_format_incident_info(ii)}')
        except (ValueError, PermissionError):
            return text(f"error: either id {si.kwargs['del']!r} doesn't exist in the system "
                        f"or you don't have permission to remove that")

    res = _incident_store.add(si.user_name, si.user_id, si.channel_id, si.argstr)
    return text(_format_incident_info(res))


def _run_server(*, enable_ssl=False):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    ssl = ssl_dict if enable_ssl else None
    server = app.create_server(host='0.0.0.0', port=31415, return_asyncio_server=True, ssl=ssl)
    loop.run_until_complete(init_slack_api())
    loop.create_task(server)
    loop.run_forever()


def __main():
    _run_server(enable_ssl=False)


if __name__ == '__main__':
    __main()
