from __future__ import annotations

from textual import events
from textual.reactive import Reactive


class FocusMixin:
    _has_focus: Reactive[bool] = Reactive(False)

    async def on_focus(self, event: events.Focus) -> None:
        self._has_focus = True

    async def on_blur(self, event: events.Blur) -> None:
        self._has_focus = False


class MouseOverMixin:
    _mouse_over: Reactive[bool] = Reactive(False)

    async def on_enter(self, event: events.Enter) -> None:
        self._mouse_over = True

    async def on_leave(self, event: events.Leave) -> None:
        self._mouse_over = False

