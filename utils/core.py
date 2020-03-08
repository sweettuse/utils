import os
import pickle
from collections import deque
from functools import wraps
from io import BytesIO
from tempfile import NamedTemporaryFile
from types import ModuleType
from typing import Dict, Union, Tuple, List, Set, Iterable, Any
import sys
from inspect import isfunction

__author__ = 'acushner'


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
    """consume an iterable. mostly used for side effects"""
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
    """make it so property functions do not need `self` if defined at module level"""
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


def __main():
    pass


if __name__ == '__main__':
    __main()
