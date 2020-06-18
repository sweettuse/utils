__author__ = 'acushner'

from itertools import count

from utils.font_to_bitmap import load_font, Font
from utils.slack_api import UserType, async_run
from utils.slack_api.api import SlackAPI


def text_to_emoji(s: str, emoji='blob-turtle', font: Font = load_font(), *, multiline=True, reverse=False) -> str:
    emoji = f':{emoji.replace(":", "")}:'
    fn = (lambda v: not v) if reverse else bool

    def helper(cur, n=0):
        res = font.render_text(cur)
        num_spaces = 6
        res = [_adjust_spaces([emoji if fn(c) else num_spaces * ' ' for c in row]) for row in res.bits]
        prefix = ''
        if not n and _is_space(res[0][0]):
            prefix = '.\n'
        return prefix + '\n'.join(map(''.join, res))

    if multiline:
        return (5 * '\n').join(helper(*args) for args in zip(s.split(), count()))
    return helper(s)


def _adjust_spaces(row):
    """it's slightly less than 6 spaces per emoji, so we need to account for that"""
    n = 0
    for i, v in enumerate(row):
        if _is_space(v):
            n += 1
            if not n % 4:
                row[i] = v[:-1]
            # if not n % 20:
            #     row[i] = row[i][:-1]
    return row


def _is_space(v):
    return len(set(v)) == 1


def size_check(emoji='cushparrot'):
    width = 31
    num_spaces = 6
    emoji = f':{emoji.replace(":", "")}:'
    with_spaces = _adjust_spaces([num_spaces * ' '] * (width - 1) + [emoji])
    with_emoji = [emoji] * width
    assert len(with_spaces) == len(with_emoji), 'fuck'
    res = [with_spaces, with_emoji]
    res = '\n'.join(map(''.join, res))
    return '.\n' + res


async def run(channel: str, text: str):
    sa = await SlackAPI.from_user_type(UserType.bot)
    await sa.client.chat_postMessage(channel=channel, text=text)


def __main():
    font = load_font('Courier New.ttf', 13)
    font = load_font('Comic Sans MS.ttf', 13)
    # font = load_font('Menlo.ttc', 13)
    s = text_to_emoji('HH!', 'mustashman', font)
    s = text_to_emoji('way 2 go', 'thumbsup', font)
    # s = text_to_emoji('TUSE', 'otomatone', load_font('Menlo.ttc', 9))
    # for emoji in 'tuse karl cushparrot'.split():
    #     print(size_check(emoji))
    print(s)
    # async_run(run('dynamic-intelligent-line-items', s))


if __name__ == '__main__':
    __main()
