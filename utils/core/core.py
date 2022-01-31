from __future__ import annotations

import time
from collections import deque
from functools import partial, wraps
from itertools import islice, tee
from typing import Iterable, Any

from memoize.wrapper import memoize

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


def timer(func):
    """timing decorator"""
    total = 0
    ncalls = 0

    @wraps(func)
    def wrapper(*args, **kwargs):
        nonlocal total, ncalls
        ncalls += 1
        start = time.perf_counter()
        try:
            return func(*args, **kwargs)
        finally:
            cur = time.perf_counter() - start
            total += cur
            print(f'{func.__name__!r} took {(cur):.6f} seconds, '
                  f'ncalls={ncalls} for {total:.3f} seconds')

    return wrapper


def pairwise(iterable):
    it1, it2 = tee(iter(iterable))
    next(it2, None)
    return zip(it1, it2)


__all__ = generate__all__(globals(), _do_not_export)
