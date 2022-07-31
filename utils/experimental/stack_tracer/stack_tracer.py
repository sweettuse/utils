from __future__ import annotations
import inspect
from operator import itemgetter
import sys
from types import FrameType
from typing import Any, Literal, Optional
from typing_extensions import TypeAlias
from rich import print

EventType = Literal['call', 'line', 'return', 'exception', 'opcode']

CodeStackKey: TypeAlias = tuple[str, str]
CodeStackEntry: TypeAlias = tuple[CodeStackKey, inspect.Traceback]
CodeStackEntries: TypeAlias = list[CodeStackEntry]


class CodeStack:
    def __init__(self):
        self._stack: CodeStackEntries = []
        self._last_action: Optional[Literal['add', 'remove']] = None

    def add(self, tb: inspect.Traceback) -> None:
        self._stack.append((self._make_key(tb), tb))
        self._last_action = 'add'

    def remove(self, tb: inspect.Traceback) -> Optional[CodeStackEntries]:
        if not self._stack:
            return

        key = self._make_key(tb)
        last_key, _ = self._stack[-1]
        if key != last_key:
            return

        res = None
        if self._last_action == 'add':
            res = self._stack.copy()
        self._last_action = 'remove'

        self._stack.pop()
        return res

    @staticmethod
    def _make_key(tb: inspect.Traceback) -> CodeStackKey:
        return tb.filename, tb.function

    def __bool__(self):
        return bool(self._stack)

    def __repr__(self) -> str:
        res = ['=' * 20]
        res.extend(map(itemgetter(0), self._stack))
        res.append('=' * 20)
        return '\n'.join(map(str, res))


class StackTracer:
    """context manager to trace stacks of calls within

    useful for debugging what code paths your code is taking when you can't easily set a breakpoint
    """

    def __init__(self, num_lines_context=0):
        self._code_stack = CodeStack()
        self._stacks = []
        self._num_lines_context = num_lines_context
        self._in_context = False  # are we within the context manager. don't want to display while within, can cause recursion issues...

    def _local(self, frame: FrameType, event: EventType, arg: Any) -> None:
        """local tracing function used to record return/exceptions"""
        tb = inspect.getframeinfo(frame, context=self._num_lines_context)
        if event in {'return', 'exception'}:
            if res := self._code_stack.remove(tb):
                self._stacks.append(res)

    def __call__(self, frame: FrameType, event: EventType, arg: Any) -> None:
        """actual global tracing function"""

        # only trace functions in our codebase
        if 'sweettuse/utils/utils' not in frame.f_code.co_filename:
            return
        tb = inspect.getframeinfo(frame, context=0)
        self._code_stack.add(tb)

        # set local tracing func
        frame.f_trace = self._local
        frame.f_trace_lines = False

    def __enter__(self):
        self._in_context = True
        sys.settrace(self)
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self._in_context = False
        sys.settrace(None)

    def display(self) -> None:
        if self._in_context:
            return
        print('=========')
        for stack in self._stacks:
            print(*(s[0][1] for s in stack))
            # print(*map(itemgetter(0), stack))
        print('=========')
