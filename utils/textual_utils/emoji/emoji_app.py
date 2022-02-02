from textual import events
from textual.app import App

from utils.rich_utils import random_emoji
from utils.textual_utils.core import FocusHandler, TextBox
from utils.textual_utils.emoji.emoji_results import EmojiResults


class EmojiApp(App):
    """filter/copy emoji easily

    no grid, instead use easier layout"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tb = TextBox('textbox', self._tb_title)
        self.er = EmojiResults(60)
        self._focus_handler = FocusHandler(self, self.tb, self.er)

    @property
    def _tb_title(self):
        e = random_emoji(3)
        return f'{e} emoji time {e}'

    async def on_mount(self):
        await self.set_focus(self.tb)
        await self.view.dock(self.tb, size=3)
        await self.view.dock(self.er, edge='top', size=40)

    async def on_key(self, event: events.Key) -> None:
        self.log('>>>>> i am here')
        await self._focus_handler.on_key(event)

        if not self.er.has_focus:
            await self.er.on_key(event)

    async def on_textbox_change(self, event):
        self.tb.title = self._tb_title
        self.er.data = event.value


if __name__ == '__main__':
    EmojiApp.run(log='/tmp/textuse.txt')
