from __future__ import annotations

import json
import os
import pickle
import smtplib
from collections import deque, ChainMap
from functools import partial
from io import BytesIO
from itertools import islice
from tempfile import NamedTemporaryFile
from typing import Any, NamedTuple, List, Dict, Union, Optional

import keyring

from .core import make_iter, identity, generate__all__

__author__ = 'acushner'
_sentinel = object()

_excluded = set(globals())


class json_obj(dict):
    """add `.` accessibility to dicts"""

    def __new__(cls, dict_or_list: Optional[Union[dict, list]] = None, **kwargs):
        if isinstance(dict_or_list, list):
            if kwargs:
                raise ValueError('cannot pass list with keyword args')
            return [(json_obj if isinstance(e, (dict, list)) else identity)(e)
                    for e in dict_or_list]

        new_dict = kwargs
        if isinstance(dict_or_list, dict):
            new_dict = ChainMap(kwargs, dict_or_list)
        elif dict_or_list is not None:
            # try to process as an iterable of tuples, a la regular dict creation
            new_dict = ChainMap(kwargs, {k: v for (k, v) in dict_or_list})

        res = super().__new__(cls)
        res._add(**new_dict)
        return res

    def __init__(self, _=None, **__):
        """need to suppress dict's default init, otherwise subdictionaries won't appear as json_obj types"""

    @classmethod
    def from_not_none(cls, **key_value_pairs):
        """create new obj and add only items that aren't `None`"""
        res = cls()
        res.add_if_not_none(**key_value_pairs)
        return res

    @classmethod
    def from_str(cls, s: str):
        return cls(json.loads(s))

    @property
    def json(self) -> str:
        return json.dumps(self)

    @property
    def pretty(self) -> str:
        return json.dumps(self, indent=4, sort_keys=True)

    def add_if_not_none(self, **key_value_pairs):
        self._add(_if_not_none=True, **key_value_pairs)

    def _add(self, _if_not_none=False, **key_value_pairs):
        for k, v in key_value_pairs.items():
            if not _if_not_none or v is not None:
                if isinstance(v, (list, dict)):
                    self[k] = json_obj(v)
                else:
                    self[k] = v

    def __setattr__(self, key, value):
        self._add(**{key: value})
        return value

    def __getattr__(self, key):
        return self[key]

    def __delattr__(self, key):
        del self[key]

    def __and__(self, other) -> set[Any]:
        return self.keys() & other.keys()

    def __or__(self, other) -> set[Any]:
        return self.keys() | other.keys()

    def __xor__(self, other) -> 'json_obj':
        cm = ChainMap(self, other)
        return type(self)((k, cm[k]) for k in self.keys() ^ other.keys())

    def __str__(self):
        strs = (f'{k}={v!r}' for k, v in self.items())
        return f'json_obj({", ".join(strs)})'

    __repr__ = __str__


class _default_class:
    """if descriptor is called from class, create instance on fly"""
    def __init__(self, f):
        self.f = f

    def __get__(self, instance, cls):
        if not instance:
            instance = cls()
        return partial(self.f, instance)


class Pickle:
    """make it easy to store data from say a running program
    and retrieve in say a jupyter console

    usage:
        # in running program:
        Pickle.write(important_data=data, context=context)

        # in jupyter console:
        data, ctx = Pickle.read('important_data', 'context')
    """
    def __init__(self, base_dir='/tmp/.pydata'):
        os.makedirs(base_dir, exist_ok=True)
        self._base_dir = base_dir

    @_default_class
    def filename(self, name):
        return f'{self._base_dir}/{name}.pkl'

    @_default_class
    def read(self, *names):
        res = []
        for n in names:
            with open(self.filename(n), 'rb') as f:
                res.append(pickle.load(f))
        return res[0] if len(res) == 1 else res

    @_default_class
    def write(self, **name_value_pairs):
        for name, val in name_value_pairs.items():
            with open(self.filename(name), 'wb') as f:
                pickle.dump(val, f)


def play_sound(file_or_path):
    if isinstance(file_or_path, BytesIO):
        file_or_path = file_or_path.read()
    if isinstance(file_or_path, bytes):
        with NamedTemporaryFile('wb') as f:
            f.write(file_or_path)
            return os.system(f'afplay {f.name}')
    return os.system(f'afplay {file_or_path}')


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


def sms(to: Union[str, List[str]], msg: str):
    """send message to people from keyring gmail address"""
    to = make_iter(to)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.ehlo()
        from_email = keyring.get_password('email', 'main-address')
        server.login(from_email, keyring.get_password('email', 'main'))
        server.sendmail(from_email, to, msg)


__all__ = generate__all__(globals(), _excluded)
