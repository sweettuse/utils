__author__ = 'acushner'

from operator import attrgetter
from random import choice
from typing import NamedTuple

import arrow

from utils.slack_api.api import SlackAPI
from utils.slack_api import UserType, async_run


class Incident(NamedTuple):
    date: str
    desc: str

    @property
    def n_days(self):
        return (arrow.utcnow() - arrow.get(self.date)).days

    def __str__(self):
        n = self.n_days
        s = 's' if n != 1 else ''
        return f'-{n}- day{s} since {self.desc}'

    def with_emoji(self, emoji):
        return f':{emoji}: {str(self)}'


_incidents = [
    Incident('2020-05-18', 'an excel drag-down related incident'),
    Incident('2020-06-12', 'misinformation'),
    Incident('2020-06-22', 'a considerable brain fart'),
]


async def update_days_since(channel='poc_crew'):
    sa = await SlackAPI.from_user_type(UserType.bot)
    strs = [i.with_emoji(await sa.random_emoji) for i in sorted(_incidents, key=attrgetter('date'), reverse=True)]
    topic = "it's been " + ' '.join(strs)
    print(topic)
    await sa.client.conversations_setTopic(channel=sa.channel_id(channel), topic=topic)


async def run():
    sa = await SlackAPI.from_user_type(UserType.bot)
    await sa.client.chat_postMessage(channel=sa.channel_id('poc_crew'), text='thank you, @john.hoffman!',
                                     link_names=True)


def __main():
    # print(list(_get_days()))
    async_run(update_days_since())


if __name__ == '__main__':
    __main()
