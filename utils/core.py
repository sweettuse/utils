import os
from collections import deque
from io import BytesIO
from tempfile import NamedTemporaryFile
from typing import Dict, Union, Tuple, List, Set, Iterable, Any

__author__ = 'acushner'


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
