from __future__ import annotations
from misty_py.utils import json_obj
from utils.core import exhaust
from utils.web.notion import Pages, Block, get


def parse_text(text: list[json_obj]) -> str:
    res = []
    for t in text:
        cur = t.plain_text
        if t.annotations.code:
            cur = f'`{cur}`'
        res.append(cur)
    return ''.join(res)


def get_page(page: Pages):
    blocks = Block.from_id(page.value)
    cur = []

    for b in blocks:
        if b.type == 'toggle':
            pass
        data = b[b.type]

        t = data.get('text')
        print('=============')
        print(b.type, data.keys())
        if t:
            print(parse_text(t))
        print('=============')


if __name__ == '__main__':
    get_page(Pages.wth)
