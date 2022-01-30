from __future__ import annotations

from typing import Callable

from rich import box
from rich.align import Align
from rich.panel import Panel
from textual.reactive import Reactive
from textual.widget import Widget
from string import printable
from utils.textual_utils.mixins import FocusMixin

printable = set(printable)


class TextBox(Widget, FocusMixin):
    style: Reactive[str] = Reactive('')
    data: Reactive[str] = Reactive('')
    height: Reactive[int | None] = Reactive(3)
    width: Reactive[int | None] = Reactive(None)

    def __init__(self, width=40, height=3):
        super().__init__()
        self.width = width
        self.height = height
        self._cbs = []

    async def on_key(self, event):
        k = event.key
        if k in {'delete', 'ctrl+h'}:
            self.data = self.data[:-1]
        elif k in printable:
            self.data += k
        else:
            return False
        return True

    @property
    def _display_str(self):
        return self.data[-self.width:]

    def render(self):
        return Panel(
            Align.left(
                self._display_str,
                vertical="top"
            ),
            title='textbox',
            border_style="blue",
            box=box.HEAVY if self._has_focus else box.ROUNDED,
            style=self.style,
            height=self.height,
            width=self.width
        )

    def watch_data(self, value: str) -> None:
        """update registered callbacks"""
        for cb in self._cbs:
            cb(value)

    def register(self, *cb: Callable[[str], None]):
        """register callbacks to be alerted when data is updated"""
        self._cbs.extend(cb)
