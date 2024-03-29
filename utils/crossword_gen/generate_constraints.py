from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime
from functools import cache
from itertools import combinations
from random import shuffle
from typing import NamedTuple, Callable

from rich import print

from utils.core import timer, Pickle, localtimer, first, exhaust

MAX_NUM_WORDS = float('inf')


@cache
def powerset_idxs(n):
    return [c for i in range(1, n + 1)
            for c in combinations(range(n), i)]


def f():
    word = 'flyer'
    constraint_info_to_word = {
        ((0,), 'f'): 'flyer',
        ((0, 1), 'fl'): 'flyer',
        ((0, 1, 2), 'fly'): 'flyer',

    }




class ConstraintInfo(NamedTuple):
    idxs: tuple[int, ...]
    chars: str

    @classmethod
    def from_coords_and_board(cls, coords, board):
        if not board:
            return
        if not (t := [(i, v)
                      for i, coord in enumerate(coords)
                      if (v := board.get(coord))]
        ):
            return

        idxs, chars = zip(*t)
        return cls(idxs, ''.join(chars))


ConstraintDict = dict[int, dict[ConstraintInfo, set[str]]]


def _word_at(w, t: tuple[int, ...]) -> str:
    return ''.join(w[i] for i in t)


def get_constraint_powerset(w) -> list[ConstraintInfo]:
    return [ConstraintInfo(t, _word_at(w, t)) for t in powerset_idxs(len(w))]


def read_words(filename='qtyp.txt', num_words=MAX_NUM_WORDS) -> dict[int, set[str]]:
    res = defaultdict(set)
    with open(filename) as f:
        for i, l in enumerate(f):
            l = l.strip().lower()
            res[len(l)].add(l)
            if i > num_words:
                break
    return res


class ConstraintManager:
    filename: str
    num_cores: int = 4
    _cache = {}

    def __init__(self, filename: str, num_cores: int = 4, num_words=MAX_NUM_WORDS):
        if filename in self._cache:
            self.__dict__ = self._cache[filename]
            return

        self.filename = filename
        self.num_cores = num_cores
        self.len_to_words_dict = read_words(self.filename, num_words)
        self._cache[filename] = self.__dict__

    @timer
    def generate_constraints(self, pred: Callable[[int], bool] = lambda word_len: word_len <= 9):
        """EXPENSIVE!"""
        pool = ProcessPoolExecutor(self.num_cores)
        words = {l: words for l, words in self.len_to_words_dict.items() if pred(l)}
        res = {l: pool.submit(self._create_constraints_per_len, words,
                              self._gen_pickle_name(len(first(words))))
               for l, words in words.items()}
        return {k: f.result() for k, f in res.items()}

    @staticmethod
    def _create_constraints_per_len(words, out_name):
        """create a constraint mappings for words of the same len

        pickle out results"""
        res = defaultdict(set)
        assert len(set(map(len, words))) == 1, 'all words must have same len'

        mark = lambda s: print(datetime.now(), s, len(first(words)), len(words))

        mark('processing')
        for w in words:
            for ci in get_constraint_powerset(w):
                res[ci].add(w)
        mark('done')
        with localtimer(out_name):
            Pickle.write(**{out_name: res})

    def _gen_pickle_name(self, word_len):
        return f'{self.filename}_{word_len}'

    def __hash__(self):
        return hash(self.filename)

    def __eq__(self, other):
        return self.filename == other.filename

    @cache
    @timer
    def _get_pickle(self, word_len) -> dict[ConstraintInfo, set[str]]:
        print('reading len', word_len)
        res = Pickle.read(self._gen_pickle_name(word_len))
        print('reading complete')
        return res

    def matches(self, coords, board, seen, *, do_shuffle=True):
        """get constraints based on already-placed letters in the positions we're checking"""
        if ci := ConstraintInfo.from_coords_and_board(coords, board):
            res = self._get_pickle(len(coords))[ci]
        else:
            res = self.len_to_words_dict[len(coords)]

        res = res - seen
        if do_shuffle:
            res = list(res)
            shuffle(res)
        return res


if __name__ == '__main__':
    exhaust(print, get_constraint_powerset('dig'))
    # cm = ConstraintManager('qtyp.txt')
    # ci = ConstraintInfo((2, 3, 4), 'ake')
    # matches = cm._get_pickle(5)[ci]
    # exclude = set('wropdflcbvm')
    # for m in matches:
    #     if not any(c in m for c in exclude):
    #         print(m)
    #
    # pass
