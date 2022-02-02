from __future__ import annotations

from typing import Callable

from rich import box
from rich.align import Align
from rich.panel import Panel
from textual.app import App
from textual.events import Event
from textual.reactive import Reactive
from textual.widget import Widget
from string import printable

from utils.core import identity, pairwise
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

class ValueEvent(Event):
    """event that has a value"""

    def __init__(self, sender, value):
        super().__init__(sender)
        self.value = value


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
        self._text_change_event = type(f'{self.name}_change',
                                       (ValueEvent,),
                                       dict(__slots__=['value']))

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
        elif k in valid_chars:
            self.value += k
        else:
            changed = False

        if changed:
            await self.post_message(self._text_change_event(self, value=self.value))
