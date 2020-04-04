import os
import pickle
import sys
from collections import deque
from functools import wraps
from io import BytesIO
from itertools import islice
from tempfile import NamedTemporaryFile
from typing import Iterable, Any, NamedTuple

__author__ = 'acushner'

_sentinel = object()


class Pickle:
    def __init__(self, base_dir='/tmp/.pydata'):
        self._base_dir = base_dir

    def filename(self, name):
        return f'{self._base_dir}/{name}.pkl'

    def read(self, *names):
        res = []
        for n in names:
            with open(self.filename(n), 'rb') as f:
                res.append(pickle.load(f))
        return res[0] if len(res) == 1 else res

    def write(self, **name_value_pairs):
        for name, val in name_value_pairs.items():
            with open(self.filename(name), 'wb') as f:
                pickle.dump(val, f)


def exhaust(it: Iterable[Any]):
    """consume an iterable. used for side effects"""
    deque(it, maxlen=0)


def play_sound(file_or_path):
    if isinstance(file_or_path, BytesIO):
        file_or_path = file_or_path.read()
    if isinstance(file_or_path, bytes):
        with NamedTemporaryFile('wb') as f:
            f.write(file_or_path)
            return os.system(f'afplay {f.name}')
    return os.system(f'afplay {file_or_path}')


def _wrap_property(prop):
    """make it so module property functions do not need `self` if defined at module level"""
    new_props = {}

    def _create_func(func):
        return wraps(func)(lambda self, *args, **kwargs: func(*args, **kwargs))

    for name in 'fget fset fdel'.split():
        f = getattr(prop, name)
        if f:
            new_props[name] = _create_func(f)

    return property(**new_props)


def enable_module_properties():
    """
    allow properties to be used at the module level

    to use, in the module, do something like:
    >>> _b = 14
    >>>
    >>> @property
    >>> def b():
    >>>     return _b
    >>>
    >>> @b.setter
    >>> def b(val)
    >>>     global _b
    >>>     _b = val
    >>>
    >>> if __name__ != '__main__':
    >>>     enable_module_properties()
    """
    globs = sys._getframe(1).f_globals
    name = globs['__name__']
    mod = sys.modules[name]
    props, body = {}, {}
    for n, v in vars(mod).items():
        if isinstance(v, property):
            props[n] = _wrap_property(v)
        else:
            body[n] = v

    new = sys.modules[name] = type(name, (type(mod),), props)(name)
    for k, v in body.items():
        setattr(new, k, v)


class SliceableDeque(deque):
    def __getitem__(self, item):
        if isinstance(item, slice):
            return self._get_slice(item)
        return super().__getitem__(item)

    def __setitem__(self, key, value):
        if isinstance(key, slice):
            return self._set_slice(key, value)
        return super().__setitem__(key, value)

    def _get_slice(self, item: slice):
        return type(self)(islice(self, item.start, item.stop, item.step))

    def _set_slice(self, key: slice, value):
        vals = self[key]
        offset = key.start or 0
        self.rotate(-offset)
        for _ in range(len(vals)):
            self.popleft()
        self.extendleft(reversed(make_iter(value)))
        self.rotate(offset)


def make_iter(v, base_type=(str, bytes)):
    if isinstance(v, base_type):
        return [v]
    try:
        iter(v)
        return v
    except TypeError:
        return [v]


class Coord(NamedTuple):
    x: int
    y: int

    def __add__(self, other):
        return Coord(self.x + other[0], self.y + other[1])

    @property
    def manhattan(self):
        return abs(self.x) + abs(self.y)


def __main():
    pass


if __name__ == '__main__':
    __main()
