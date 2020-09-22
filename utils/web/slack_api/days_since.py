import asyncio
import random
from contextlib import suppress
from typing import List

from slack.errors import SlackApiError

from utils.web.slack_api import UserType, async_run
from utils.web.slack_api.api import SlackAPI
from utils.web.servers.incident import Incident, init_incident_store

__author__ = 'acushner'


async def _update_channel(sa: SlackAPI, channel_id, incidents: List[Incident], n=5):
    random.shuffle(incidents)
    while n > 0:
        strs = [i.with_emoji(await sa.random_emoji) for i in incidents[:n]]
        n -= 1
        topic = "it's been " + ' '.join(strs)
        print(channel_id, topic)
        with suppress(SlackApiError):
            await sa.client.conversations_setTopic(channel=sa.channel_id(channel_id), topic=topic)
            return


async def update_days_since():
    sa = await SlackAPI.from_user_type(UserType.bot)
    incidents = init_incident_store().group_by_channel()
    tasks = (asyncio.create_task(_update_channel(sa, channel, [ii.incident for ii in iis]))
             for channel, iis in incidents.items())
    await asyncio.gather(*tasks)


async def run():
    sa = await SlackAPI.from_user_type(UserType.bot)
    await sa.client.chat_postMessage(channel=sa.channel_id('poc_crew'), text='thank you, @john.hoffman!',
                                     link_names=True)


def fix_dates():
    i = init_incident_store()
    breakpoint()


def __main():
    # print(list(_get_days()))
    async_run(update_days_since())
    # fix_dates()


if __name__ == '__main__':
    __main()
