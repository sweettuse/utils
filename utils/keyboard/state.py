from __future__ import annotations

from contextlib import contextmanager
from typing import Optional, NamedTuple, List, Set

from more_itertools import always_iterable

__author__ = 'acushner'


class StateChars(NamedTuple):
    state: State
    used_chars: List[str]


class State:
    _cache = set()

    def __init__(self, name, key_char_override=None):
        self.name = name
        self.children: Set[State] = set()
        self.parents: Set[State] = set()
        self.root: Optional[State] = None  # will be set later
        self.key_char = key_char_override or name[0]
        self._cache.add(self)

    def display(self):
        print(f'{self.parents} -> <{self}> -> {self.children}')

    @staticmethod
    def _transform_key(key):
        return getattr(key, 'char', key)

    def _parse_one(self, char) -> State:
        c_transformed = self._transform_key(char)
        for child in self.children:
            if child.key_char == c_transformed:
                return child
        if self.root.key_char == c_transformed:
            return self.root
        return self

    def parse(self, chars, used_chars: List = None) -> StateChars:
        used = []
        prev = new = self
        for c in always_iterable(chars):
            new = prev._parse_one(c)
            if new != prev:
                print('NEW STATE:', new)
                used.append(c)
        return StateChars(new, used)

    @classmethod
    @contextmanager
    def create_machine(cls, root: State):
        yield
        for s in cls._cache:
            if s is not root and not s.parents:
                root >> s
            s.root = root
        cls._cache.clear()

    def __rshift__(self, state: State):
        self.children.add(state)
        state.parents.add(self)
        return state

    def __lshift__(self, state: State):
        state >> self
        return state

    def __eq__(self, other: State):
        return self.name == other.name and self.children is other.children and self.parents is other.parents

    def __hash__(self):
        return hash(self.name) ^ hash(id(self.children)) ^ hash(id(self.parents))

    def __repr__(self):
        return f'{type(self).__name__}({self.name})'

    def __bool__(self):
        return True

    __str__ = __repr__
