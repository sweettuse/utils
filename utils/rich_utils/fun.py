from collections import defaultdict
from random import choice

from rich import print
from rich.console import Console
from rich.emoji import Emoji, EMOJI
from rich.table import Table
from utils.lights.font_to_bitmap import load_font, Fonts
from utils.core import generate__all__

__excluded = set(globals())

_console = Console(width=200)

_emoji_to_name = {v: k for k, v in EMOJI.items()}
_emoji_name_map = _emoji_to_name


def _get_inconsistent_width_emoji():
    def _inconsistent_width(n):
        return (n.startswith(('flag_for', 'regional_indicator'))
                or n.endswith('skin_tone'))
    return {e for name, e in EMOJI.items() if _inconsistent_width(name)}


def _init_emoji_list():
    return list(set(EMOJI.values()) - _get_inconsistent_width_emoji())


_emoji_list = _init_emoji_list()


def random_emoji():
    return choice(_emoji_list)


def _convert_bits(bits, emoji, flip) -> list[str]:
    return [''.join(emoji if flip ^ v else '  ' for v in row) for row in bits]


def _with_border(bits) -> list[list[int]]:
    width = len(bits[0]) + 2

    res = [[0] * width]
    res.extend([0, *v, 0] for v in bits)
    res.append([0] * width)
    return res


def emoji_text(*lines: str,
               emoji: str = None,
               font: Fonts = Fonts.courier_new,
               size: int = 13,
               flip: bool = False):
    print('before', emoji)
    emoji = emoji or random_emoji()
    print('after', emoji)
    if emoji.isascii():
        print('i am ascii')
        emoji = str(Emoji(emoji.strip(':')))
    font = load_font(font, size)
    res = []
    for line in lines:
        bits = font.render_text(line).bits
        bits = _with_border(bits)
        res.append('\n'.join(_convert_bits(bits, emoji, flip)))
    print(_emoji_name_map[emoji])
    return res


def display_emoji(s=''):
    for name, emoji in EMOJI.items():
        if s in name:
            print(emoji, name)


def sample_emoji_text(text,
                      emoji='exploding_head',
                      size_range=range(11, 16),
                      fonts=tuple(Fonts)):
    t = Table('font', 'size', 'text', width=175)
    temp = [((), {})]

    def store_row(*args, **kwargs):
        temp.append((args, kwargs))

    for s in size_range:
        temp[-1][1]['end_section'] = True
        for f in fonts:
            store_row()
            res = emoji_text(text, emoji=emoji, font=f, size=s, flip=False)
            store_row(f.name, str(s), '\n'.join(res))
            store_row()
    for a, kw in temp[1:]:
        t.add_row(*a, **kw)
    return t


def __main():
    print(random_emoji())
    print(*emoji_text('jygify', flip=False, size=20, font=Fonts.comic_sans))


if __name__ == '__main__':
    __main()

__all__ = generate__all__(globals(), __excluded)
