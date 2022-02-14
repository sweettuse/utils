from typing import Any

from rich.align import Align
from rich.color import Color, ANSI_COLOR_NAMES
from rich.console import RenderableType
from rich.panel import Panel
from rich.style import Style
from textual import events
from textual.app import App
from textual.reactive import Reactive
from textual.widget import Widget
from utils.lights.font_to_bitmap import load_font, Fonts

font = load_font(Fonts.courier_new, 12)


def num_to_str(n) -> str:
    fill = '\u2588'
    # fill = random_emoji()
    bits = font.render_text(str(n)).bits
    return '\n'.join(''.join(fill if v else ' ' for v in row) for row in bits)


class Clickable(Widget):
    count: Reactive[int] = Reactive(95)
    title: Reactive[str] = Reactive('')
    color: Reactive[Any] = Reactive(None)

    def __init__(self, name, color):
        super().__init__(name)
        self.title = name
        self.color = color

    def render(self) -> RenderableType:
        return Panel(
            Align.center(num_to_str(self.count), vertical='middle'),
            title=self.title,
            style=Style(bgcolor=self.color)
        )

    async def on_click(self, event: events.Click) -> None:
        self.count += 1


class ClickTracker(App):
    async def on_mount(self):
        grid = await self.view.dock_grid()
        grid.add_row('row', repeat=4, min_size=10, max_size=20)
        grid.add_column('col', repeat=4, min_size=10, max_size=30)
        grid.place(Clickable('stuff', 'dark_green'))


if __name__ == '__main__':
    ClickTracker.run(log='/tmp/textuse.txt')
