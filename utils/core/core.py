from __future__ import annotations

import time
from collections import deque
from contextlib import suppress
from functools import partial, wraps
from itertools import islice, tee
from typing import Iterable, Any

from memoize.wrapper import memoize
from rich.table import Table

_do_not_export = set(globals())


def generate__all__(globals, excluded):
    """create `__all__` values from globals
    first argument MUST be set to `globals()`
    exclude excluded and protected vals(i.e. `startswith('_')`)

    usage:
        from blah import jeb
        from tuse import hatch, thatch

        # store all above values for exclusion:
        _excluded = set(globals())

        def f(): ...

        def _g(): ...

        x = 4
        _y = 5

        __all__ = generate__all__(globals(), _excluded)
        # __all__ == ['f', 'x']
    """
    return [s
            for s in globals.keys() - excluded
            if not s.startswith('_')]


# =================================================
# funcs, etc
# =================================================
identity = lambda x: x


def mapt(fn, *args):
    """map fn to args and return as tuple of results"""
    return tuple(map(fn, *args))


def first(v):
    """get first item in iterable"""
    return next(iter(v))


def exhaust(iterable_or_fn, *args: Iterable[Any]):
    """consume an iterable. used for side effects.

    if `args`, treat `iterable_or_fn` as fn and `map(fn, *args)`
    """
    if args:
        iterable_or_fn = map(iterable_or_fn, *args)
    deque(iterable_or_fn, maxlen=0)


def make_iter(v, treat_as_not_iterable=(str, bytes, dict)):
    """make "non-iterables" iterable

    if already iterable, just return the value"""
    if isinstance(v, treat_as_not_iterable):
        return [v]
    if v is None:
        return []
    try:
        iter(v)
        return v
    except TypeError:
        return [v]


def chunk(iterable: Iterable[Any], chunksize: int, return_type=list):
    """chunk iterable into smaller bites"""
    yield from iter(lambda it=iter(iterable):
                    return_type(islice(it, chunksize)), return_type())


def async_memoize(func=None, *, configuration=None):
    """decorator to memoize an async function

    this is not smart.
    if multiple of the same calls go out concurrently, this will run them all"""
    if func is None:
        return partial(async_memoize, configuration=configuration)

    return memoize(configuration=configuration)(func)


class classproperty:
    """bind property to a class"""

    def __init__(self, f):
        self.f = f

    def __get__(self, instance, cls):
        return self.f(cls)


class localtimer:
    """context manager timer"""

    def __init__(self, name='', *, handler=print, prec=3):
        self.name = name or 'snippet'
        self.handler = handler
        self.prec = prec

    def __enter__(self):
        self.start = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.handler(f'{self.name} took {time.perf_counter() - self.start:.0{self.prec}f} seconds')


class _TimerObj:
    def __init__(self, name):
        self.name = name
        self.total = 0
        self.ncalls = 0
        self.min = float('inf')
        self.max = -float('inf')
        self.last = None

    def update(self, time):
        self.total += time
        self.ncalls += 1
        self.last = time
        self.min = min(self.min, time)
        self.max = max(self.max, time)

    @property
    def avg(self):
        if not self.ncalls:
            return 0
        return self.total / self.ncalls

    def __repr__(self):
        return (f'{self.name!r} took {(self.last):.6f}s, '
                f'ncalls={self.ncalls} for {self.total:.3f}s (avg: {self.avg:.3f}s)')

    def __rich__(self):
        from utils.rich_utils import good_color
        r3 = '{:.3f}'.format
        t = Table(*'name last avg min max ncalls total'.split(),
                  border_style=good_color(self.name))
        t.add_row(self.name,
                  *map(r3, (self.last, self.avg, self.min, self.max, self.ncalls, self.total)))
        return t


def timer(func, *, pretty=False):
    """timing decorator"""
    local_print = print
    if pretty:
        with suppress(Exception):
            from rich import print as rich_print
            local_print = rich_print

    to = _TimerObj(func.__name__)

    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        try:
            return func(*args, **kwargs)
        finally:
            cur = time.perf_counter() - start
            to.update(cur)
            local_print(to)

    return wrapper


def take(n, iterable):
    return list(islice(iterable, n))


def pairwise(iterable):
    it1, it2 = tee(iter(iterable))
    next(it2, None)
    return zip(it1, it2)


__all__ = generate__all__(globals(), _do_not_export)

if __name__ == '__main__':
    @timer
    def f():
        time.sleep(.002)


    @timer
    def g():
        time.sleep(.002)


    [(f(), g()) for _ in range(20)]
