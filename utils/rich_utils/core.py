from __future__ import annotations
from rich.color import ANSI_COLOR_NAMES

GOOD_COLORS = [name for name in ANSI_COLOR_NAMES
               if 'grey' not in name
               and 'gray' not in name]


def good_color(idx: int | str):
    if isinstance(idx, str):
        idx = hash(idx)
    return GOOD_COLORS[idx % len(GOOD_COLORS)]

