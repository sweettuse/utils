from __future__ import annotations

from string import printable
from typing import Callable, NamedTuple

from rich import box
from rich.align import Align
from rich.panel import Panel
from rich.table import Table
from textual import events
from textual.app import App
from textual.reactive import Reactive
from textual.widget import Widget
from textual.widgets import Button

from utils.core import identity, pairwise
from utils.rich_utils import random_emoji
from utils.textual_utils.events import ValueEvent
from utils.textual_utils.mixins import FocusMixin

valid_chars = set(printable)


class TextBoxOrig(Widget, FocusMixin):
    """base text box. replaced by the new `TextBox`"""

    style: Reactive[str] = Reactive('')
    data: Reactive[str] = Reactive('')
    height: Reactive[int | None] = Reactive(3)
    width: Reactive[int | None] = Reactive(None)
    title: Reactive[str] = Reactive('')

    def __init__(self, title='textbox', width=40, height=3):
        super().__init__()
        self.width = width
        self.height = height
        self.title = title
        self._cbs = []

    async def on_key(self, event):
        k = event.key
        if k in {'delete', 'ctrl+h'}:
            self.data = self.data[:-1]
        elif k in valid_chars:
            self.data += k
        else:
            return False
        return True

    @property
    def _display_str(self):
        return self.data[-self.width:]

    def render(self):
        return Panel(
            Align.left(self._display_str, vertical='top'),
            title=self.title,
            border_style='blue',
            box=box.HEAVY if self.has_focus else box.ROUNDED,
            style=self.style,
            height=self.height,
            width=self.width,
        )

    def register(self, *cb: Callable[[str], None]):
        """register callbacks to be alerted when data is updated"""
        self._cbs.extend(cb)

    def watch_data(self, value: str) -> None:
        """update registered callbacks"""
        for cb in self._cbs:
            cb(value)


class FocusHandler:
    """allow easily cycling of focus through widgets in order

    usage:
    class MyApp(App):
        def __init__(self):
            self.w1 = Widget()
            self.w2 = Widget()
            self._focus_handler = FocusHandler(self, self.w1, self.w2)

        async def on_key(self, event):
            await self._focus_handler.on_key(event)
            ...
    """

    def __init__(self, app: App, *widgets: Widget):
        self._app = app
        self._widgets = 2 * widgets

    async def _set(self, set_prev=False):
        for cur, nxt in pairwise((reversed if set_prev else identity)(self._widgets)):
            if self._app.focused is cur:
                await self._app.set_focus(nxt)
                return

    async def set_next(self):
        await self._set()

    async def set_prev(self):
        await self._set(True)

    async def on_key(self, event):
        if event.key == 'ctrl+i':  # tab
            await self.set_next()
        elif event.key == 'shift+tab':
            await self.set_prev()


# ==================================================================================================


class TextBox(Widget, FocusMixin):
    """textbox

    to subscribe to events, simply add `on_<name>_change` function to your widget/app

    e.g.:
    def __init__(self):
        self.tb = TextBox('hello_world')

    def on_hello_world_change(self, event):
        self.log(event.value)
    """
    value: Reactive[str] = Reactive('')
    title: Reactive[str] = Reactive('')

    def __init__(self, name: str, title=''):
        super().__init__(name)
        self.title = title
        self.name = name
        self._height = 3
        self._text_change_event = ValueEvent.make_new(f'{self.name}_change', bound=type(self))

    def render(self):
        return Panel(
            Align.left(self._display_str),
            title=self.title,
            border_style='blue',
            box=box.DOUBLE if self.has_focus else box.ROUNDED,
            # style=None,
            height=self._height,
        )

    @property
    def _display_str(self):
        return self.value

    async def on_key(self, event):
        k = event.key
        changed = True
        if k in {'delete', 'ctrl+h'}:
            self.value = self.value[:-1]
        elif k == 'escape':
            self.value = ''
        elif k in valid_chars:
            self.value += k
        else:
            changed = False

        if changed:
            await self.post_message(self._text_change_event(value=self.value))


class CheckStyle(NamedTuple):
    unchecked: str
    checked: str
    width: int = 1

    @classmethod
    def random(cls):
        return cls('[ ]', f'[{random_emoji()}]', 3)


check_styles = (
    CheckStyle('🔳', '✅'),
    CheckStyle('◻', '◼'),
    CheckStyle('▫', '▪'),
    CheckStyle('◻', '✖'),
    CheckStyle('[ ]', '[X]', 3)
)


class CheckBox(Button):
    checked: Reactive[bool] = Reactive(False)

    def __init__(self, label, name: str = '', check_style: CheckStyle = None):
        name = name or label
        super().__init__(label, name or label)
        self.checked = False
        self.check_style = check_style or CheckStyle.random()
        self._event = ValueEvent.make_new(f'{self.name}_change', bound=type(self))

    def render(self):
        t = Table('check', 'label', show_header=False, border_style=None, box=None)
        t.add_row(self.check_style[self.checked], self.label)
        return t

    async def on_click(self, event: events.Click) -> None:
        self.checked = not self.checked
        await self.post_message(self._event(self.checked))
