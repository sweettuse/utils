from concurrent.futures import ThreadPoolExecutor, wait, Future, ProcessPoolExecutor
from typing import Optional, List, Union, Any
from threading import local

import logging

__author__ = 'acushner'

log = logging.getLogger(__name__)

PoolOrNumThreads = Optional[Union[int, ThreadPoolExecutor, ProcessPoolExecutor]]


class WaitPool:
    """
    pool that allows easy waiting using a `with` block.

        >>> import time

        >>> def f(s):
        >>>     print('starting', s)
        >>>     time.sleep(s)
        >>>     print('finishing', s)
        >>>     return s ** 2

        >>> with WaitPool(8) as wp:
        >>>     for s in range(8):
        >>>         wp.submit(f, s)
        >>> print('done')
        >>> print('\\n'.join(map(str, wp.results)))

    the `with` block won't be exited until all futures have completed

    if passed a pool (Thread/Process), will use that pool.
    if passed an `int`, will create a new ThreadPoolExecutor with that many threads
    """
    _threads_per_pool = 8

    def __init__(self,
                 pool: PoolOrNumThreads = None):
        self._pool = self._init_pool(pool)
        self._local = local()

    @staticmethod
    def _init_pool(pool: PoolOrNumThreads):
        if isinstance(pool, (ProcessPoolExecutor, ThreadPoolExecutor)):
            return pool

        if isinstance(pool, int):
            num_threads = pool
        elif pool is None:
            num_threads = WaitPool._threads_per_pool
        else:
            raise ValueError(f'invalid value for `pool`: {pool!r}')

        return ThreadPoolExecutor(num_threads)

    @property
    def futures(self) -> List[Future]:
        try:
            f = self._local.futures
        except AttributeError:
            f = self._local.futures = []
        return f

    @property
    def results(self) -> List[Any]:
        return [f.result() for f in self.futures]

    def wait(self):
        wait(self.futures)

    def __getattr__(self, item):
        """proxy for underlying pool object"""
        desc = type(self).__dict__.get(item)
        if hasattr(desc, '__get__'):
            return desc.__get__(self)
        return getattr(self._pool, item)

    def submit(self, fn, *args, **kwargs):
        fut = self._pool.submit(fn, *args, **kwargs)
        self.futures.append(fut)
        return fut

    def map(self, fn, *iterables):
        self.futures.extend(self._pool.submit(fn, *args) for args in zip(*iterables))

    def dispatch(self, fn, *args, **kwargs):
        """
        fire and forget
        run on thread pool but don't wait for completion
        """
        return self._pool.submit(fn, *args, **kwargs)

    def __enter__(self):
        self.futures.clear()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.wait()


__all__ = ['WaitPool']


def __main():
    help(WaitPool)


if __name__ == '__main__':
    __main()
