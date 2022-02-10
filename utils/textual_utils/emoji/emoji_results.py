from __future__ import annotations

from functools import partial

import pyperclip
from more_itertools import take
from rich.emoji import EMOJI
from rich.align import Align
from rich.panel import Panel
from textual import events
from textual.reactive import Reactive
from textual.widget import Widget

from utils.textual_utils.mixins import FocusMixin

_emoji = dict(sorted((name, e) for name, e in EMOJI.items() if not name.startswith('regional')))


class EmojiResults(Widget, FocusMixin):
    """filtered panel of emoji"""

    width: Reactive[int | None] = Reactive(None)
    data: Reactive[str] = Reactive('')
    style: Reactive[str] = Reactive('')
    offset: Reactive[int] = Reactive(0)

    def __init__(self, width=50):
        super().__init__()
        self._emoji = []
        self._title_override = ''
        self.border_style = 'red'
        self.width = width
        self._orig_border_style = self.border_style

        # keeps border updating functions from overlapping
        self._last_copied_cxl_ref = [False]

    @property
    def _title_str(self):
        return self._title_override or f'emoji results ({self._num_matching})'

    @property
    def _num_matching(self):
        return sum(self.data.lower() in s.lower() for s in _emoji)

    @property
    def height(self):
        return self.size.height

    def render(self):
        return Panel(
            Align.left(self._emoji_str),
            title=self._title_str,
            border_style=self.border_style,
            style=self.style,
            height=min(self.height, len(self._emoji) + 2),
            width=self.width,
        )

    @property
    def _emoji_str(self) -> str:
        self._emoji = self._get_emoji(self.data, limit=self.height, offset=self.offset)
        return '\n'.join(s[: self.width - 10] for s in self._emoji)

    async def on_key(self, event):
        k = event.key
        if k == 'down':
            self.down()
        elif k == 'up':
            self.up()
        else:
            self.offset = 0

    async def on_mouse_scroll_up(self, event):
        self.down(3)

    async def on_mouse_scroll_down(self, event):
        self.up(3)

    async def on_click(self, event: events.Click) -> None:
        """copy emoji to clipboard"""
        info = val = None
        try:
            idx = event.y - 1
            if idx < self.height - 2:
                # subtract 2 for the borders
                val = self._emoji[idx].split()[0]
                pyperclip.copy(val)
                info = f'copied {val} to clipboard'
                border_style = 'green'
        except IndexError:
            pass
        except Exception:
            val = 'error'
            info = 'unable to copy'
            border_style = 'purple'

        if info:
            self._alert_copied(info, border_style)  # noqa
        self.log(f'bleep {val}')

    def _alert_copied(self, info, border_style):
        """change border/title to reflect that copying has occurred"""
        self._title_override = info
        self.border_style = border_style
        self.refresh()

        self._last_copied_cxl_ref[0] = True
        self._last_copied_cxl_ref = canceled = [False]

        def _reset_title():
            if canceled[0]:
                return

            self._title_override = ''
            self.border_style = self._orig_border_style
            self.refresh()

        self.set_timer(1, _reset_title)

    def down(self, amount=1):
        if len(self._emoji) > 1:
            self.offset += amount

    def up(self, amount=1):
        self.offset -= amount

    def validate_offset(self, v):
        return max(v, 0)

    @staticmethod
    def _get_emoji(s='', limit=0, offset=0):
        s = s.lower()
        limited = list
        if limit > 0:
            limited = partial(take, limit)
        emoji = (f'{e} {name}' for name, e in _emoji.items() if s in name.lower())
        take(offset, emoji)
        return limited(emoji)
