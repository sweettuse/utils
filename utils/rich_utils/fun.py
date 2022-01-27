from rich import print
from rich.console import Console
from rich.emoji import Emoji, EMOJI
from rich.table import Table
from utils.lights.font_to_bitmap import load_font, Fonts
from utils.core import generate__all__

_excluded = set(globals())
console = Console(width=200)


def _convert_bits(bits, emoji, flip) -> list[str]:
    return [''.join(emoji if flip ^ v else '  ' for v in row) for row in bits]


def _with_border(bits) -> list[list[int]]:
    width = len(bits[0]) + 2

    res = [[0] * width]
    res.extend([0, *v, 0] for v in bits)
    res.append([0] * width)
    return res


def emoji_text(*lines: str,
               emoji: str = 'saxophone',
               font: Fonts = Fonts.courier_new,
               size: int = 11,
               flip: bool = False):
    emoji = str(Emoji(emoji.strip(':')))
    font = load_font(font, size)
    res = []
    for line in lines:
        bits = font.render_text(line).bits
        bits = _with_border(bits)
        res.append('\n'.join(_convert_bits(bits, emoji, flip)))
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
    print(*emoji_text('abcdefghijklmno', emoji='poop', flip=True))


if __name__ == '__main__':
    __main()

__all__ = generate__all__(globals(), _excluded)
