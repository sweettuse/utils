__author__ = 'acushner'

from random import choice

import arrow

from utils.slack_app.app import SlackAPI
from utils.slack_app import UserType, async_run

# actually one day ahead
LAST_DRAG_DOWN_INCIDENT = arrow.get('2020-05-19')
LAST_TOBY_MISINFORMATION = arrow.get('2020-06-13')


def _get_days():
    now = arrow.utcnow()
    return ((now - i).days + 1 for i in (LAST_DRAG_DOWN_INCIDENT, LAST_TOBY_MISINFORMATION))


async def update_days_since(group='poc_crew'):
    sa = await SlackAPI.from_user_type(UserType.bot)
    drag_down, misinform = _get_days()

    emoji = choice(list(await sa.get_emoji()))
    topic = f":{emoji}: it's been -{drag_down}- days since an excel drag-down related incident and -{misinform}- days since misinformation"
    print(topic)
    await sa.client.conversations_setTopic(channel=sa.conv_id(group), topic=topic)


async def run():
    sa = await SlackAPI.from_user_type(UserType.bot)
    await sa.client.chat_postMessage(channel=sa.conv_id('copilot-test'), text='testing linking @john.hoffman!',
                                     link_names=True)


def __main():
    async_run(update_days_since())


if __name__ == '__main__':
    __main()
