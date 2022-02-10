from __future__ import annotations

from functools import partial

from textual.events import Event


class MyEvent(Event):
    _event_names = set()

    __slots__ = ()

    @classmethod
    def make_new(cls, name, bound):
        if name in cls._event_names:
            raise ValueError(f'collision in creating event named: {name!r}')
        cls._event_names.add(name)
        typ = type(name, (cls,), {})
        return partial(typ, bound)


class ValueEvent(MyEvent):
    """event that has a value"""
    __slots__ = ['value']

    def __init__(self, sender, value):
        super().__init__(sender)
        self.value = value


def __main():
    pass


if __name__ == '__main__':
    __main()
