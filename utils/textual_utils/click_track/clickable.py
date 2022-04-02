from __future__ import annotations
from typing import Any

from rich import box
from rich.align import Align
from rich.text import Text
from rich.color import Color, ANSI_COLOR_NAMES
from rich.console import RenderableType, Group, ConsoleOptions, Console
from rich.panel import Panel
from rich.style import Style, StyleType
from rich.table import Table
from textual import events
from textual.app import App
from textual.reactive import Reactive
from textual.widget import Widget
from textual.widgets import Button

from utils.lights.font_to_bitmap import load_font, Fonts
from utils.textual_utils.mixins import MouseOverMixin, FocusMixin

font = load_font(Fonts.courier_new, 12)


def num_to_str(n) -> str:
    fill = '\u2588'
    # fill = random_emoji()
    bits = font.render_text(str(n)).bits
    return '\n'.join(''.join(fill if v else ' ' for v in row) for row in bits)


class Clickable(Widget):
    """click tally"""
    count: Reactive[int] = Reactive(95)
    title: Reactive[str] = Reactive('')

    def __init__(self, name):
        super().__init__(name)
        self.title = name
        self._button = ResetButton()

    def render(self):
        return Align.center(num_to_str(self.count), vertical='middle', height=15)

    # def __rich_console__(self, console: Console, options: ConsoleOptions):
    #     yield Align.center(num_to_str(self.count), vertical='middle')

    def reset(self):
        self.log('RESETTING')
        self.count = 0

    async def on_click(self, event: events.Click) -> None:
        self.count += 1


class ResetButton(Widget, MouseOverMixin):
    """refresh button"""
    icon = '🔄'

    async def on_click(self, event: events.Click) -> None:
        self.log('RefreshButttuse')

    def render(self):
        style = None
        if self.mouse_over:
            style = 'bold'
        return Align.right(self.icon, height=2, style=style)


class ToTrack(Widget):
    clicker: Reactive[Clickable] = Reactive(None)
    button: Reactive[ResetButton] = Reactive(None)

    def __init__(self, name: str | None = None,
                 color='dark_green'
                 ) -> None:
        super().__init__(name)
        self.clicker = Clickable(name)
        self.color = color
        self.button = ResetButton()

    def render(self):
        # g = Group(self.clicker, self.button)
        # return Panel(
        #     g,
        #     style=Style(bgcolor='white'),
        # )
        st = Style(bgcolor=self.color)
        grid = Table(show_header=False, box=box.ROUNDED, show_lines=False, expand=True,
                     title=self.name, style=st)
        grid.add_row(self.clicker, style=st)
        grid.add_row(self.button, style=st)
        return grid

    def on_click(self, event: events.Click) -> None:
        self.log(f'I HAVE CLICKED: {self._refresh_button_clicked(event)}')
        if self._refresh_button_clicked(event):
            self.clicker.reset()
        else:
            self.clicker.count += 1

        self.refresh()

    def _refresh_button_clicked(self, event: events.Click):
        x, y = self.size
        self.log('>>>>>>>', event.x, event.y, x, y)

        return event.x in {35, 36} and event.y == 17
    # x - 4, x - 3, y - 5

    # def __rich__(self):


class ClickTracker(App):
    async def on_mount(self):
        grid = await self.view.dock_grid()
        # 2243grid.add_row('row', repeat=4, min_size=10, max_size=80)
        # grid.add_column('col', repeat=4, min_size=10, max_size=80)
        grid.add_row('row', repeat=4, min_size=10, max_size=25)
        grid.add_column('col', repeat=4, min_size=10)
        # grid.place(Clickable('stuff', 'dark_green'), Clickable('tuse', 'light_blue'))
        grid.place(
            ToTrack('tuse', 'blue'),
            ToTrack('stuff', 'dark_green'),
            ToTrack('tuse', 'blue'),
            ToTrack('tuse', 'blue'),
            ToTrack('tuse', 'blue'),
            ToTrack('stuff', 'dark_green'),
            ToTrack('stuff', 'dark_green'),
            ToTrack('stuff', 'dark_green'),
            ToTrack('tuse', 'blue'),
            ToTrack('stuff', 'dark_green'),
            ToTrack('stuff', 'dark_green'),
            ToTrack('stuff', 'dark_green'),
        )


if __name__ == '__main__':
    ClickTracker.run(log='/tmp/textuse.txt')
