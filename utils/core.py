import os
import pickle
from collections import deque
from io import BytesIO
from tempfile import NamedTemporaryFile
from typing import Dict, Union, Tuple, List, Set, Iterable, Any

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


def __main():
    pass


if __name__ == '__main__':
    __main()
