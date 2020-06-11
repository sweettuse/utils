from enum import Enum
from itertools import starmap

from slack import WebClient

from utils.slack_app import parse_config, UserType, ConvType, async_run

__author__ = 'acushner'


class SlackAPI:
    def __init__(self, token):
        self.client = WebClient(token, run_async=True)
        async_run(self._async_init())

    @classmethod
    def from_user_type(cls, ut: UserType):
        return cls(parse_config()[ut.value + 'oauth_access_token'])

    async def _async_init(self):
        self._privates = await self._init_private_channels()

    async def _init_private_channels(self):
        res = await self.client.conversations_list(types=ConvType.private_channel)
        return {c['name']: c for c in res['channels']}

    def conv_id(self, conv_name):
        return self._privates[conv_name]['id']

    async def get_emoji(self):
        return (await self.client.emoji_list())['emoji']


def to_html(name, image):
    return f'{name}<br><img src="{image}"><br>'


async def run(sa: SlackAPI):
    emoji = await sa.get_emoji()
    print('\n'.join(starmap(to_html, sorted(emoji.items(), key=lambda s: s[0].lower()))))


def __main():
    sa = SlackAPI.from_user_type(UserType.bot)
    async_run(run(sa))


if __name__ == '__main__':
    __main()
