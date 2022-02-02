from __future__ import annotations

from textual import events
from textual.app import App
from textual.widgets import Placeholder  # noqa
import logging

from utils.textual_utils.core import TextBoxOrig, FocusHandler
from utils.textual_utils.emoji.emoji_results import EmojiResults


log = logging.getLogger(__name__)


class EmojiAppGrid(App):
    """filter/copy emoji easily"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tb = TextBoxOrig()
        self.er = EmojiResults()
        self._focus_handler = FocusHandler(self, self.tb, self.er)

    async def on_mount(self):
        await self.set_focus(self.tb)

        def _set_er(v):
            self.er.data = v

        self.tb.register(_set_er)

        grid = await self.view.dock_grid(edge='left', name='left')
        grid.add_row(name='r_textbox', max_size=self.tb.height)
        grid.add_row(name='r_emoji_results', max_size=1000)
        grid.add_column(name='col')
        grid.add_areas(tb_area='col,r_textbox', er_area='col,r_emoji_results')
        grid.place(tb_area=self.tb, er_area=self.er)

    async def on_key(self, event: events.Key) -> None:
        await self._focus_handler.on_key(event)

        if self.tb.has_focus:
            await self.er.on_key(event)


# print(EmojiResults._get_emoji('nerd'))
if __name__ == '__main__':
    EmojiAppGrid.run(log='/tmp/textuse.txt')
