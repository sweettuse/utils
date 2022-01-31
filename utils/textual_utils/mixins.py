from __future__ import annotations

from textual import events
from textual.reactive import Reactive


class FocusMixin:
    has_focus: Reactive[bool] = Reactive(False)

    async def on_focus(self, event: events.Focus) -> None:
        self.has_focus = True

    async def on_blur(self, event: events.Blur) -> None:
        self.has_focus = False


class MouseOverMixin:
    mouse_over: Reactive[bool] = Reactive(False)

    async def on_enter(self, event: events.Enter) -> None:
        self.mouse_over = True

    async def on_leave(self, event: events.Leave) -> None:
        self.mouse_over = False

