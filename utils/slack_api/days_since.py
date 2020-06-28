import asyncio
import random
from typing import List

from utils.slack_api import UserType
from utils.slack_api.api import SlackAPI
from utils.web.incident import Incident, init_incident_store

__author__ = 'acushner'

# _incidents = [
#     Incident('2020-05-18', 'an excel drag-down related incident'),
#     Incident('2020-06-12', 'misinformation'),
#     Incident('2020-06-22', 'a considerable brain fart'),
# ]


async def _update_channel(sa: SlackAPI, channel_id, incidents: List[Incident], n=3):
    # strs = [i.with_emoji(await sa.random_emoji) for i in sorted(incidents, key=attrgetter('date'), reverse=True)[:n]]
    random.shuffle(incidents)
    strs = [i.with_emoji(await sa.random_emoji) for i in incidents[:n]]
    topic = "it's been " + ' '.join(strs)
    print(topic)
    await sa.client.conversations_setTopic(channel=sa.channel_id(channel_id), topic=topic)


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
    # async_run(update_days_since())
    fix_dates()


if __name__ == '__main__':
    __main()
