from textual import events
from textual.app import App
from textual_inputs import TextInput

from utils.textual_utils.emoji.emoji_results import EmojiResults


class EmojiAppTI(App):
    """filter/copy emoji easily"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tb = TextInput()
        self.er = EmojiResults(50)

    async def on_mount(self):
        await self.set_focus(self.tb)

        self.tb.on_change_handler_name = 'handle_tb'

        grid = await self.view.dock_grid(edge='left', name='left')
        grid.add_row(name='r_textbox', max_size=3)
        grid.add_row(name='r_emoji_results', max_size=1000)
        grid.add_column(name='col', max_size=50)
        grid.add_areas(tb_area='col,r_textbox', er_area='col,r_emoji_results')
        grid.place(tb_area=self.tb, er_area=self.er)

    async def handle_tb(self, msg):
        self.er.data = msg.sender.value


if __name__ == '__main__':
    EmojiAppTI.run(log='/tmp/textuseti.txt')
