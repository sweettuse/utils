import os
import pickle
import smtplib
import sys
from collections import deque
from functools import wraps, partial
from io import BytesIO
from itertools import islice
from tempfile import NamedTemporaryFile
from typing import Iterable, Any, NamedTuple, List, Dict, Union

import keyring
from memoize.wrapper import memoize
from pydantic import BaseModel

__author__ = 'acushner'

from misty_py.utils import json_obj

_sentinel = object()


class Pickle:
    def __init__(self, base_dir='/tmp/.pydata'):
        os.makedirs(base_dir, exist_ok=True)
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


def exhaust(iterable_or_fn, *args: Iterable[Any]):
    """consume an iterable. used for side effects.

    if `args`, treat `iterable_or_fn` as fn and `map(fn, *args)`
    """
    if args:
        iterable_or_fn = map(iterable_or_fn, *args)
    deque(iterable_or_fn, maxlen=0)


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
    # >>> _b = 14
    # >>>
    # >>> @property
    # >>> def b():
    # >>>     return _b
    # >>>
    # >>> @b.setter
    # >>> def b(val)
    # >>>     global _b
    # >>>     _b = val
    # >>>
    # >>> if __name__ != '__main__':
    # >>>     enable_module_properties()
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


def make_iter(v, base_type=(str, bytes, dict)):
    if isinstance(v, base_type):
        return [v]
    if v is None:
        return []
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
        return sum(map(abs, self))


class aobject:
    """enable async init of objects"""

    async def _async__new__(cls, *args, **kwargs):
        instance = super().__new__(cls)
        await instance.__init__(*args, **kwargs)
        return instance

    __new__ = _async__new__
    __await__: None  # for pycharm type hinting


def chunks(iterable: Iterable[Any], chunksize: int, return_type=list):
    yield from iter(lambda it=iter(iterable): return_type(islice(it, chunksize)), return_type())


def async_memoize(func=None, *, configuration=None):
    if func is None:
        return partial(async_memoize, configuration=configuration)

    return memoize(configuration=configuration)(func)


class DataStore(json_obj):
    """mapping of one or more of a dict's keys to the dict itself"""

    def __new__(cls, *_, **__):
        return super().__new__(cls)

    def __init__(self):
        super().__init__()

    @classmethod
    def from_data(cls, data: Union[Dict[str, Any], List[Dict[str, Any]]], key: str, *keys: str):
        res = cls()
        res.update(data, key, *keys)
        return res

    def update(self, data: List[Dict[str, Any]], *keys):
        data = make_iter(data)
        for d in data:
            self.add(d, *keys)

    def add(self, d: Dict[str, Any], *keys):
        for k in keys:
            cur_key = d.get(k)
            if cur_key:
                self[cur_key] = d


class PosBaseModel(BaseModel):
    """pydantic BaseModel that allows positional args

    typically, you can't pass positional args to models. this fixes that
    """

    def __init_subclass__(cls, **kwargs):
        PosBaseModel._make_pos(cls)

    @staticmethod
    def _make_pos(cls):
        kwargs = {}
        for c in reversed(cls.__mro__):
            kwargs.update(getattr(c, '__annotations__', {}))

        sentinel = object()
        argstr = ','.join(f'{k}=sentinel' for k in kwargs)
        body = (
            f'def __init__(self, {argstr}, **from_subclasses):\n'
            '    l = locals()\n'
            '    new_args = ((k, l[k]) for k in kwargs)\n'
            '    super(cls, self).__init__(**from_subclasses, **dict(na for na in new_args if na[1] is not sentinel))\n'
        )
        exec(body, locals())
        cls.__init__ = locals()['__init__']
        return cls

    def __init__(self, *_for_pycharm_only, **kwargs):
        """fake __init__ to keep pycharm from bitching about positional args.

        gets overridden dynamically, so no need to call `super().__init__`"""
        super().__init__(**kwargs)


def sms(to: Union[str, List[str]], msg: str):
    if isinstance(to, str):
        to = [to]

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.ehlo()
        from_email = keyring.get_password('email', 'main-address')
        server.login(from_email, keyring.get_password('email', 'main'))
        server.sendmail(from_email, to, msg)


def __main():
    class Model(PosBaseModel):
        a: int
        b: float

    class Under(Model):
        c: str
        d: Any

    m = Model(a=1, b=2)
    u = Under(1, 2, 3, 4)
    print(m)
    print(u)
    return
    sd = SliceableDeque([1, 2, 3])
    d = deque([1, 2, 3])
    sd[2:2] = [4, 5, 6]
    print(sd)


if __name__ == '__main__':
    __main()
