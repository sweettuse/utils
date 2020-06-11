__author__ = 'acushner'

from random import choice

import arrow

from utils.slack_app.app import SlackAPI
from utils.slack_app import UserType, async_run

LAST_DRAG_DOWN_INCIDENT = arrow.get('2020-05-19')
LAST_TOBY_MISINFORMATION = arrow.get('2020-06-12')


def _get_days():
    now = arrow.utcnow()
    return ((now - i).days + 1 for i in (LAST_DRAG_DOWN_INCIDENT, LAST_TOBY_MISINFORMATION))


async def update_days_since(sa: SlackAPI, group='poc_crew'):
    drag_down, misinform = _get_days()

    emoji = choice(list(await sa.get_emoji()))
    topic = f":{emoji}: it's been -{drag_down}- days since an excel drag-down related incident and -{misinform}- days since misinformation"
    print(topic)
    await sa.client.conversations_setTopic(channel=sa.conv_id(group), topic=topic)


async def run(sa: SlackAPI):
    await sa.client.chat_postMessage(channel=sa.conv_id('poc_crew'), text='testing linking @john.hoffman!',
                                     link_names=True)


def __main():
    sa = SlackAPI.from_user_type(UserType.bot)
    async_run(update_days_since(sa))


if __name__ == '__main__':
    __main()
