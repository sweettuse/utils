from itertools import chain

from textual.app import App
from textual.widgets import Placeholder, Button

from utils.core import pairwise, identity
from utils.textual_utils.core import TextBox, CheckBox


class FocusHandler2:
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

    def __init__(self):
        self._fh_widgets = ()

    async def _fh_set(self, set_prev=False):
        widgets = chain(map(reversed if set_prev else identity,
                            (self._fh_widgets, self._fh_widgets)))
        for cur, nxt in pairwise(widgets):
            if self.focused is cur:
                await self.set_focus(nxt)
                return

    async def _fh_set_next(self):
        await self._fh_set()

    async def _fh_set_prev(self):
        await self._fh_set(True)

    async def on_key(self, event):
        if event.key == 'ctrl+i':  # tab
            await self._fh_set_next()
        elif event.key == 'shift+tab':
            await self._fh_set_prev()

    def register_focusable_widgets(self, *widgets):
        self._fh_widgets += widgets


class PlayApp(App):
    async def on_mount(self):
        self.log('we are here!')
        grid = await self.view.dock_grid()
        grid.add_row('row', repeat=4, min_size=10, max_size=20)
        grid.add_column('col', repeat=4, min_size=10, max_size=30)
        grid.add_areas(lower_right='col2-start|col3-end,row2-start|row3-end')

        phs = [TextBox(name=str(i)) for i in range(40)]

        grid.place(*phs)
        grid.place(lower_right=Placeholder(name='jeb'))
        # self.tb = TextBox('tb', 'a simple textbox')
        # self.tb2 = TextBox('tb2', 'another textbox')

        # await self.view.dock(self.tb, edge='top', size=3)
        # await self.view.dock(self.tb2, edge='right')

    def on_cb_change(self, event):
        self.log('CB CHANGE:', event.value)


class CBTest(App):
    async def on_mount(self):
        words = 'engage check this will look cool maybe'.split()
        await self.view.dock(*(CheckBox(w) for w in words))


def __main():
    # PlayApp.run(log='/tmp/textuse.txt')
    CBTest.run(log='/tmp/textuse.txt')


if __name__ == '__main__':
    __main()
