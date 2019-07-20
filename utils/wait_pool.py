from concurrent.futures import ThreadPoolExecutor, wait
from contextlib import contextmanager
from typing import Optional

import logging

__author__ = 'acushner'

log = logging.getLogger(__name__)


class WaitPool:
    """
    allow jobs to be submitted to either an existing pool or a dynamically-created one,
    wait for it to complete, and have access to the futures outside the `with` block

    """
    threads_per_pool = 8

    def __init__(self, pool: Optional[ThreadPoolExecutor] = None):
        self._pool = pool or ThreadPoolExecutor(self.threads_per_pool)
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


def f():
    import time
    print('start f')
    time.sleep(1)
    print('end f')


print('start')
with WaitPool(ThreadPoolExecutor(3)) as wp:
    for _ in range(3):
        wp.submit(f)
print('done')

import sys

sys.exit()


@U.timer
def __main():
    pass


if __name__ == '__main__':
    __main()
