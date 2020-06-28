from collections import ChainMap
from enum import Enum
from pathlib import Path
from random import choice
from typing import Optional, List, Set, Iterable, Union

from slack import WebClient
from slackblocks import Message
from slackblocks.blocks import Block

from utils.core import aobject, async_memoize, make_iter, DataStore
from utils.slack_api import parse_config, UserType, async_run

__author__ = 'acushner'


class ChannelType(Enum):
    public = 'public_channel'
    private = 'private_channel'
    group = 'mpim'
    direct = 'im'


class SlackAPI(aobject):
    # this weird formulation is due to the fact that pycharm thinks `__init__` can't be async...
    async def _async_init(self, token):
        self.client = WebClient(token, run_async=True)
        self._channels = await self._init_channels()

    __init__ = _async_init

    @classmethod
    async def from_user_type(cls, ut: UserType) -> 'SlackAPI':
        return await cls(parse_config()[ut.value + 'oauth_access_token'])

    async def _init_channels(self) -> DataStore:
        res = await self.get_channels(list(ChannelType))
        return DataStore.from_data(res, 'name', 'id')

    async def get_channels(self, types: Union[ChannelType, List[ChannelType]]):
        """get all channels of specified `types`"""
        types = ','.join(ct.value for ct in make_iter(types))
        return await self._paginate(self.client.conversations_list, _response_key='channels', types=types,
                                    exclude_archived=True, limit=500)

    def channel_id(self, channel_name):
        """convert channel name/id into channel id"""
        channel_data = self._channels.get(channel_name)
        if channel_data:
            return channel_data['id']
        return channel_name

    @async_memoize
    async def get_users(self) -> DataStore:
        """get all non-deleted users. still include deactivated"""
        users = await self._paginate(self.client.users_list, _response_key='members')
        users = [u for u in users if not u['deleted']]
        return DataStore.from_data(users, 'id', 'name', 'real_name')

    @async_memoize
    async def get_emoji(self):
        """get a list of all available emoji"""
        emoji_dicts = await self._paginate(self.client.emoji_list, _response_key='emoji')
        return ChainMap(*emoji_dicts)

    @property
    async def random_emoji(self):
        """get a random emoji from all available emoji"""
        return choice(list(await self.get_emoji()))

    # async def get_user_groups(self):
    #     return await self.client.usergroups_list()['usergroups']
    #
    # async def get_copilot_groups(self):
    #     excluded = {'UK Copilot SME', 'Copilot Helios | Xaxis Italy'}
    #     ugs = await self.get_user_groups()

    @async_memoize
    async def get_channel_members(self, channel: str) -> Set[str]:
        """get user_ids for a particular conversation"""
        channel = self.channel_id(channel)
        res = await self._paginate(self.client.conversations_members, _response_key='members', channel=channel)
        return set(res)

    @async_memoize
    async def get_copilot_users(self):
        """use oasis to get data about all copilot users"""
        user_ids = await self.get_channel_members('oasis')
        return await self._user_ids_to_data(user_ids)

    async def post_message(self, channel,
                           *, text: Optional[str] = None,
                           blocks: Optional[Union[Block, List[Block]]] = None):
        channel = self.channel_id(channel)
        if (text is not None) + (blocks is not None) != 1:
            raise ValueError('set exactly one of `text` and `blocks`')
        if blocks:
            msg = Message(channel=channel, blocks=make_iter(blocks))
            await self.client.chat_postMessage(**msg)
        else:
            await self.client.chat_postMessage(channel=channel, text=text)

    async def _user_ids_to_data(self, user_ids: Iterable[str], user_data: Optional[DataStore] = None):
        """given an iterable of user ids, create a DataStore with the user data"""
        user_data = user_data or await self.get_users()
        return DataStore.from_data([user_data[uid] for uid in user_ids], 'name', 'id', 'real_name')

    async def post_file(self, channel: str, fname: str, file_type: str = 'txt'):
        """post file from local file system"""
        with open(fname) as f:
            content = f.read()
        title = Path(fname).name
        await self.post_in_mem_file(channel, content, title, file_type)

    async def post_in_mem_file(self, channel, content: str, title='from python', file_type='txt'):
        """post file whose contents are in memory"""
        await self.client.files_upload(content=content, channels=self.channel_id(channel), filetype=file_type,
                                       title=title)

    @staticmethod
    async def _paginate(client_func, *args, _response_key: Optional[str] = None, **kwargs):
        res = []
        cursor = {}
        while True:
            cur = await client_func(*args, **kwargs, **cursor)
            res.extend(make_iter(cur[_response_key])) if _response_key else res.append(cur)

            try:
                cursor['cursor'] = cur.data['response_metadata']['next_cursor']
                print(cursor)
            except KeyError:
                cursor['cursor'] = None

            if not cursor['cursor']:
                break
        return res


async def run():
    sa = await SlackAPI.from_user_type(UserType.bot)


def __main():
    async_run(run())


if __name__ == '__main__':
    __main()
