from enum import Enum
from typing import Union

import arrow
import keyring
import requests
from misty_py.utils import json_obj

__author__ = 'acushner'

from utils.core import exhaust

notion_secret = keyring.get_password('notion', 'secret')

endpoint = 'https://api.notion.com/v1/{service}/{id}'
headers = {
    'Notion-Version': '2021-05-13',
    'Authorization': f'Bearer {notion_secret}'
}
page_size = 100


class CopyError(Exception):
    """error when copying block via api

    only certain block types are supported. see https://developers.notion.com/reference/block#block-object-keys
    """


class Pages(Enum):
    # todays_tasks = 'ce83353286b844c1b7230525b3fffdcd'
    todo = '2a717cb595454735956a1bb9e70803ae'
    test = 'c433dbbc623744078e379d3bec6b28b6'
    work_todo = 'd0f14c9fc8f34d66aface25c73289dc9'
    sachith = '86c3ac785c0b41d4848c9a928f3748b6'
    coding_questions = '05d955889a4e449f9df3e9810d0eb768'
    wth = '27a05db9f7504b78b0b74adc18b3f4d2'
    today_todo = 'bbfc4954778f4935a27603e7867e593a'

    @property
    def page(self):
        return endpoint.format(service='pages', id=self.value)

    @property
    def blocks(self):
        return endpoint.format(service='blocks', id=self.value) + '/children'

    @property
    def is_todo(self):
        return self is not self.wth


def get(url):
    """handle pagination"""
    opt_start_cursor = dict()
    res = []
    while True:
        r = requests.get(url, headers=headers, params={**opt_start_cursor, 'page_size': page_size}).json()
        if 'results' in r:
            res.extend(r['results'])
            if not r['has_more']:
                break
            opt_start_cursor = dict(start_cursor=r['next_cursor'])

        else:
            return r

    return res


def date_obj(d=None):
    if d is None:
        d = arrow.now()
    else:
        d = arrow.get(d)

    return json_obj(type='mention', mention=json_obj(type='date', date=json_obj(start=d.isoformat()), end=None))


def find_key(d_or_l: Union[dict, list], key):
    """search a dict in a recursive fashion for a nested key
    return the first value found"""

    class KeyFound(Exception):
        pass

    def _helper(d_or_l=d_or_l):
        if isinstance(d_or_l, list):
            exhaust(_helper, d_or_l)

        elif isinstance(d_or_l, dict):
            if key in d_or_l:
                raise KeyFound(d_or_l[key])
            exhaust(_helper, d_or_l.values())

    try:
        _helper()
    except KeyFound as e:
        return e.args[0]


class Block:
    def __init__(self, block):
        self._block = json_obj(block)
        self._children = []

    def append(self, obj):
        self._children.append(obj)

    @classmethod
    def from_id(cls, block_id: str, get_children=True):
        b = cls(get(endpoint.format(service='blocks', id=block_id)))
        if not get_children:
            return b

        def _helper(cur):
            if not cur.has_children:
                return

            for child in map(Block, get(endpoint.format(service='blocks', id=cur.id) + '/children')):
                cur.append(child)
                _helper(child)

        _helper(b)
        return b

    def __getattr__(self, item):
        return getattr(self._block, item)

    def __getitem__(self, item):
        return getattr(self, item)

    def __iter__(self):
        yield self
        for c in self._children:
            yield from c

    def __str__(self):
        return f'{type(self).__name__}({self._block.id}): {self._children}'

    __repr__ = __str__

    def is_completed(self):
        """check if block is to-do block and it and all its children are completed"""
        first_run = True

        def _is_completed(b):
            if b.type == 'to_do':
                return b.to_do.checked
            return not first_run

        for b in self:
            if not _is_completed(b):
                return False
            first_run = False
        return True

    def copy_to(self, target_id):
        child_url = endpoint.format(service='blocks', id=target_id) + '/children'
        # block.to_do.text.append(date_obj())
        r = requests.patch(child_url, json=dict(children=[self._block]), headers=headers)
        if not r.ok:
            error = r.content.decode()
            if 'Fix one: body.children[0].heading_1' in error:
                error = f'unsupported block type in notion api {self.type!r}.\n' \
                        f'see https://developers.notion.com/reference/block#block-object-keys for more info'
            raise CopyError(f'{target_id}: {error}')

        if not self._children:
            return

        new_target = get(child_url)[-1]['id']
        for c in self._children:
            c.copy_to(new_target)

    def delete(self):
        requests.delete(f'https://api.notion.com/v1/blocks/{self._block.id}', headers=headers)
