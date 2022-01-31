from __future__ import annotations
from functools import partial

from more_itertools import take
from rich.align import Align
from rich.emoji import EMOJI
from rich.panel import Panel
from textual import events
from textual.app import App
from textual.reactive import Reactive
from textual.widget import Widget
from textual.widgets import Placeholder  # noqa
import pyperclip
import logging

from utils.textual_utils.core import TextBox, FocusHandler

_emoji = dict(
    sorted((name, e) for name, e in EMOJI.items() if not name.startswith('regional'))
)

identity = lambda x: x
log = logging.getLogger(__name__)


class EmojiBox(App):
    """filter/copy emoji easily"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tb = TextBox()
        self.er = EmojiResults()
        self._focus_handler = FocusHandler(self, self.tb, self.er)

    async def on_mount(self):
        await self.set_focus(self.tb)

        def _set_er(v):
            self.er.data = v

        self.tb.register(_set_er)

        grid = await self.view.dock_grid(edge='left', name='left')
        grid.add_row(name='r_textbox', max_size=self.tb.height)
        grid.add_row(name='r_emoji_results')
        grid.add_column(name='col')
        grid.add_areas(tb_area='col,r_textbox', er_area='col,r_emoji_results')
        grid.place(tb_area=self.tb, er_area=self.er)

    async def on_key(self, event: events.Key) -> None:
        await self._focus_handler.on_key(event)

        if self.tb.has_focus:
            await self.er.on_key(event)


class EmojiResults(Widget):
    """filtered panel of emoji"""
    width: Reactive[int | None] = Reactive(None)
    height: Reactive[int | None] = Reactive(40)
    data: Reactive[str] = Reactive('')
    style: Reactive[str] = Reactive('')
    offset: Reactive[int] = Reactive(0)

    def __init__(self, width=50):
        super().__init__()
        self._emoji = []
        self.title = 'emoji results'
        self.border_style = 'red'
        self.width = width
        self._orig_title = self.title
        self._orig_border_style = self.border_style

        # keeps border updating functions from overlapping
        self._last_copied_cxl_ref = [False]

    def render(self):
        return Panel(
            Align.left(self._emoji_str),
            title=self.title,
            border_style=self.border_style,
            style=self.style,
            height=self.height,
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
        self.title = info
        self.border_style = border_style
        self.refresh()

        self._last_copied_cxl_ref[0] = True
        self._last_copied_cxl_ref = canceled = [False]

        def _reset_title():
            if canceled[0]:
                return

            self.title = self._orig_title
            self.border_style = self._orig_border_style

        self.set_timer(1, _reset_title)

    def down(self):
        self.offset += 1

    def up(self):
        self.offset -= 1

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


EmojiBox.run(log='/tmp/textuse.txt')
