from functools import reduce
from typing import List

from misty_py.utils import RGB
import operator as op

__author__ = 'acushner'


class ColorsMeta(type):
    """make `Colors` more accessible"""

    def __iter__(cls):
        return (name
                for name, val in vars(cls).items()
                if isinstance(val, RGB))

    def keys(cls):
        return list(cls)

    def values(cls):
        return [getattr(cls, n) for n in cls]

    def items(cls):
        return {n: getattr(cls, n) for n in cls}

    def __getitem__(cls, item):
        return cls.__dict__[item]

    def __str__(cls):
        colors = '\n\t'.join(map(str, cls))
        return f'{cls.__name__}:\n\t{colors}'

    def sum(cls, *colors: RGB) -> RGB:
        """average together all colors provided"""
        return reduce(op.add, colors)

    def by_name(cls, name) -> List[RGB]:
        """get colors if they contain `name` in their name"""
        name = name.lower()
        return [c for n, c in cls if name in n.lower()]


class Colors(metaclass=ColorsMeta):
    RED = RGB(255, 0, 0)
    ORANGE = RGB.from_hex(0xffa500)
    YELLOW = RGB(255, 255, 0)
    GREEN = RGB(0, 255, 0)
    CYAN = RGB(0, 255, 255)
    BLUE = RGB(0, 0, 255)
    PURPLE = RGB(128, 0, 128)
    MAGENTA = RGB.from_hex(0xff00ff)
    PINK = RGB.from_hex(0xffc0cb)

    BROWN = RGB.from_hex(0xa0522d)

    COPILOT_BLUE = RGB.from_hex(0x00b4e3)
    COPILOT_BLUE_GREEN = RGB.from_hex(0x00827d)
    COPILOT_BLUE_GREY = RGB.from_hex(0x386e8f)
    COPILOT_DARK_BLUE = RGB.from_hex(0x193849)

    HANUKKAH_BLUE = RGB.from_hex(0x09239b)

    MARIO_BLUE = RGB.from_hex(0x049cd8)
    MARIO_YELLOW = RGB.from_hex(0xfbd000)
    MARIO_RED = RGB.from_hex(0xe52521)
    MARIO_GREEN = RGB.from_hex(0x43b047)

    PYTHON_LIGHT_BLUE = RGB.from_hex(0x4b8bbe)
    PYTHON_DARK_BLUE = RGB.from_hex(0x306998)
    PYTHON_LIGHT_YELLOW = RGB.from_hex(0xffe873)
    PYTHON_DARK_YELLOW = RGB.from_hex(0xffd43b)
    PYTHON_GREY = RGB.from_hex(0x646464)

    SNES_BLACK = RGB.from_hex(0x211a21)
    SNES_DARK_GREY = RGB.from_hex(0x908a99)
    SNES_DARK_PURPLE = RGB.from_hex(0x4f43ae)
    SNES_LIGHT_GREY = RGB.from_hex(0xcec9cc)
    SNES_LIGHT_PURPLE = RGB.from_hex(0xb5b6e4)

    STEELERS_BLACK = RGB.from_hex(0x101820)
    STEELERS_BLUE = RGB.from_hex(0x00539b)
    STEELERS_GOLD = RGB.from_hex(0xffb612)
    STEELERS_RED = RGB.from_hex(0xc60c30)
    STEELERS_SILVER = RGB.from_hex(0xa5acaf)

    XMAS_GOLD = RGB.from_hex(0xe5d08f)
    XMAS_GREEN = RGB.from_hex(0x18802b)
    XMAS_RED = RGB.from_hex(0xd42426)

    YALE_BLUE = RGB.from_hex(0xf4d92)


def __main():
    pass


if __name__ == '__main__':
    __main()
