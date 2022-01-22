import asyncio

import utils.core as U

from misty_py.utils import json_obj
from slackblocks import SectionBlock, DividerBlock, Text

__author__ = 'acushner'

from utils.web.slack_api import UserType
from utils.web.slack_api.api import SlackAPI


def _iter_triage(t):
    fields = ['*start_date*', '*end_date*', t.start_date, t.end_date]
    header = SectionBlock(text=t.title, fields=[Text(f)._resolve() for f in fields])
    yield header
    yield from t.currently_failing
    yield from t.eventually_succeeded


async def _triage(sa, channel):
    t = json_obj(U.Pickle().read('err_dict'))
    header, *msgs = _iter_triage(t)
    await sa.post_message(channel, blocks=header)
    for msg in msgs:
        await sa.post_message(channel, blocks=DividerBlock())
        if msg:
            await sa.post_message(channel, text=msg)


async def run(channel='fake'):
    sa = await SlackAPI.from_user_type(UserType.bot)
    await _triage(sa, channel)


def __main():
    asyncio.run(run('fake'))


if __name__ == '__main__':
    __main()
