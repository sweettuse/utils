__author__ = 'acushner'

from typing import List

from utils.core import chunks, exhaust
from utils.font_to_bitmap import load_font, Font, Bitmap
from utils.web.slack_api import UserType
from utils.web.slack_api.api import SlackAPI

NUM_SPACES = 6


def _add_border(bm: Bitmap) -> List[List[int]]:
    top_bottom = (bm.width + 1) * [0]
    middle = ([0, *row] for row in bm.bits)
    return [top_bottom, *middle, top_bottom]


def text_to_emoji(s: str, emoji='blob-turtle', font: Font = load_font(),
                  *, reverse=False) -> List[str]:
    emoji = f':{emoji.replace(":", "")}:'
    if reverse:
        transform_bit = lambda v: not v
        transform_bitmap = _add_border
    else:
        transform_bit = bool
        transform_bitmap = lambda v: v.bits

    def _to_emoji_list(text: str) -> List[List[str]]:
        """return list of strings representing each row of a single line of emoji text"""
        res = font.render_text(text)
        return [_adjust_spaces([emoji if transform_bit(c) else NUM_SPACES * ' ' for c in row])
                for row in transform_bitmap(res)]

    rows = [_to_emoji_list(word) for word in s.split()]
    msgs = _split_to_msgs(rows)
    return msgs


def _split_to_msgs(words: List[List[List[str]]]) -> List[str]:
    res = []
    for word in words:
        cur_msg = ''
        for row in word:
            if not cur_msg:
                _adjust_for_init_whitespace(row)

            next_line = ''.join(row)

            if len(cur_msg) + len(next_line) >= 3998:
                res.append(cur_msg)
                _adjust_for_init_whitespace(row)
                cur_msg = ''.join(row)
            else:
                prefix = '\n' if cur_msg else ''
                cur_msg += f'{prefix}{next_line}'
        if cur_msg:
            res.append(cur_msg)
    return res


def _adjust_for_init_whitespace(l: List[str]):
    if _is_space(l[0]):
        l[0] = '.' + l[0][1:]


def _adjust_spaces(row):
    """it's slightly less than 6 spaces per emoji, so we need to account for that"""
    n = 0
    for i, v in enumerate(row):
        if _is_space(v):
            n += 1
            if not n % 4:
                row[i] = v[:-1]
    return row


def _is_space(v):
    return len(set(v)) == 1


async def _blocks_time():
    sa = await SlackAPI.from_user_type(UserType.user)
    font = load_font('Comic Sans MS.ttf', 13)
    blocks = text_to_emoji('abcdef', 'thumbsup', font, reverse=False)
    print(len(blocks))
    for cur_blocks in chunks(blocks, 50):
        await sa.post_message('fake', blocks=cur_blocks)


async def determine_msg_size():
    """send message to slack and see how much fits before a message splits"""
    msg = '|'.join(f'{n:04}' for n in range(1000))
    # msg = [f'|{n:04}' for n in range(1000))
    sa = await SlackAPI.from_user_type(UserType.bot)
    await sa.post_message('fake', text=msg)


async def run(channel: str, text: str):
    sa = await SlackAPI.from_user_type(UserType.bot)
    await sa.client.chat_postMessage(channel=channel, text=text)


def play():
    msg = '|'.join(f'{n:04}' for n in range(1000))


def __main():
    # return async_run(determine_msg_size())
    # return async_run(_blocks_time())
    font = load_font('Courier New.ttf', 13)
    font = load_font('Comic Sans MS.ttf', 13)
    # font = load_font('Menlo.ttc', 13)
    # s = text_to_emoji('h i', 'mustashman', font)
    s = text_to_emoji('aaaaaaaaaaaaaaaa', 'mustashman', font, reverse=True)
    exhaust(print, s)
    return
    s = text_to_emoji('way 2 go', 'thumbsup', font, reverse=True)
    # s = text_to_emoji('TUSE', 'otomatone', load_font('Menlo.ttc', 9))
    # for emoji in 'tuse karl cushparrot'.split():
    #     print(size_check(emoji))
    print(s)


if __name__ == '__main__':
    __main()

# blocks playaround:
# def text_to_emoji(s: str, emoji='blob-turtle', font: Font = load_font(),
#                   *, multiline=True, reverse=False) -> Union[str, List[SectionBlock]]:
#     emoji = f':{emoji.replace(":", "")}:'
#     if reverse:
#         transform_bit = lambda v: not v
#         transform_bitmap = _add_border
#     else:
#         transform_bit = bool
#         transform_bitmap = lambda v: v.bits
#
#     def helper(cur) -> List[SectionBlock]:
#         rendered = font.render_text(cur)
#         res = []
#         for row in transform_bitmap(rendered):
#             emoji_lst = [emoji if transform_bit(c) else NUM_SPACES * ' ' for c in row]
#             res.append(SectionBlock(Text(_adjust_spaces(emoji_lst), TextType.PLAINTEXT, emoji=True)))
#         return res
#
#     if multiline:
#         return [block for word in s.split() for block in helper(word)]
#     return helper(s)
#
#
# def _adjust_spaces(row):
#     """it's slightly less than 6 spaces per emoji, so we need to account for that"""
#     n = 0
#     for i, v in enumerate(row):
#         if _is_space(v):
#             if i == 0:
#                 row[0] = '.' + v[1:]
#             n += 1
#             if not n % 4:
#                 row[i] = v[:-1]
#             # if not n % 20:
#             #     row[i] = row[i][:-1]
#     return ''.join(row)
#
#
