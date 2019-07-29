from __future__ import annotations

from contextlib import contextmanager
from typing import Optional

__author__ = 'acushner'


class State:
    _cache = set()

    def __init__(self, name):
        self.name = name
        self.children = set()
        self.parents = set()
        self.root: Optional[State] = None  # will be set later
        self._cache.add(self)

    def add_child(self, state: State):
        self.children.add(state)

    def add_parent(self, state: State):
        self.parents.add(state)

    def __rshift__(self, state: State):
        self.add_child(state)
        state.add_parent(self)
        return state

    def __lshift__(self, state):
        state >> self
        return state

    def __eq__(self, other: State):
        return self.name == other.name and self.children is other.children and self.parents is other.parents

    def __hash__(self):
        return hash(self.name) ^ hash(id(self.children)) ^ hash(id(self.parents))

    def __repr__(self):
        return f'{type(self).__name__}({self.name})'

    __str__ = __repr__

    def display(self):
        print(f'{self.parents} -> <{self}> -> {self.children}')

    def parse(self, chars):
        # check children
        if not chars:
            return self
        c, *rest = chars
        for child in self.children:
            if child.name.startswith(c):
                return child.parse(rest)

        to_parse = rest if self.root is self else chars
        return self.root.parse(to_parse)

    @classmethod
    @contextmanager
    def create_machine(cls, name):
        yield
        root = StateRoot(name)
        for s in cls._cache:
            root.add_child(s)
            s.root = root
        cls._cache.clear()


class StateRoot(State):
    pass


with State.create_machine('__root__'):
    jeb = State('jeb')
    tuse = State('tuse')

    head = State('head')
    pitch = head >> State('pitch')
    yaw = head >> State('yaw')
    roll = head >> State('roll')

head.parse('yyhp').display()

# head.display()
# yaw.display()
