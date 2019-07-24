from concurrent.futures import ThreadPoolExecutor, wait
from typing import Optional

import logging

__author__ = 'acushner'

log = logging.getLogger(__name__)


class WaitPool:
    """
    pool that allows easy waiting using a `with` block.

    ===============================
    usage:
    import time

    def f(s):
        print('starting', s)
        time.sleep(s)
        print('finishing', s)
        return s ** 2

    with WaitPool() as wp:
        for s in range(8):
            wp.submit(f, s)
    print('done')
    print('\n'.join(map(str, (f.result() for f in wp.futures))))
    ===============================

    the `with` block won't be exited until all futures have completed
    """
    _threads_per_pool = 8

    def __init__(self, pool: Optional[ThreadPoolExecutor] = None):
        self._pool = pool or ThreadPoolExecutor(self._threads_per_pool)
        self._futures = []

    @property
    def futures(self):
        return self._futures

    def wait(self):
        wait(self._futures)

    def __getattr__(self, item):
        """proxy for underlying pool object"""
        return getattr(self._pool, item)

    def submit(self, fn, *args, **kwargs):
        fut = self._pool.submit(fn, *args, **kwargs)
        self._futures.append(fut)
        return fut

    def __enter__(self):
        self._futures.clear()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.wait()


def __main():
    pass


if __name__ == '__main__':
    __main()
