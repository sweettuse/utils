from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from contextlib import suppress
from datetime import datetime
from random import shuffle

from dataclasses import dataclass
from functools import cache, partial
from operator import itemgetter

from rich import print
from itertools import combinations, chain
from typing import NamedTuple

from utils.core import timer, Pickle, localtimer, first


@cache
def powerset_idxs(n):
    return [c for i in range(1, n + 1)
            for c in combinations(range(n), i)]


class ConstraintInfo(NamedTuple):
    idxs: tuple[int, ...]
    chars: str

    @classmethod
    def from_coords_and_board(cls, coords, board):
        idxs, chars = zip(*((i, v) for i, coord in enumerate(coords) if (v := board.get(coord))))
        return cls(idxs, ''.join(chars))


ConstraintDict = dict[int, dict[ConstraintInfo, set[str]]]


def _word_at(w, t: tuple[int, ...]) -> str:
    return ''.join(w[i] for i in t)


def get_constraint_powerset(w) -> list[ConstraintInfo]:
    return [ConstraintInfo(t, _word_at(w, t)) for t in powerset_idxs(len(w))]


class ConstraintManager:
    filename: str
    num_cores: int = 4
    _cache = {}

    def __init__(self, filename: str, num_cores: int = 4):
        if filename in self._cache:
            self.__dict__ = self._cache[filename]
            return

        self.filename = filename
        self.num_cores = num_cores
        from utils.crossword_gen.generate_crosswords import read_words
        self.len_to_words_dict = read_words(self.filename)
        self._cache[filename] = self.__dict__

    @timer
    def generate_constraints(self, max_len=9):
        """EXPENSIVE!"""
        pool = ProcessPoolExecutor(self.num_cores)
        words = {l: words for l, words in self.len_to_words_dict.items() if l <= max_len}
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
    def _get_pickle(self, word_len):
        print('reading len', word_len)
        res = Pickle.read(self._gen_pickle_name(word_len))
        print('reading complete')
        return res

    def matches(self, coords, board, seen):
        """get constraints based on already-placed letters in the positions we're checking"""
        try:
            ci = ConstraintInfo.from_coords_and_board(coords, board)
            res = self._get_pickle(len(coords)).get(ci, set())
        except ValueError:
            res = self.len_to_words_dict[len(coords)]

        res = list(res - seen)
        shuffle(res)
        return res


def do_the_thing():
    board = {
        (0, 1): 'a',
        (0, 3): 'm',
    }
    # board = {}
    coords = [(0, i) for i in range(4)]
    cm = ConstraintManager('qtyp.txt')
    print(cm.matches(coords, board, set()))

    # cm.create_constraints()
    # words = read_words('qtyp.txt')
    # words = dict(sorted(words.items(), reverse=True))
    # words = {l: words for l, words in words.items() if l in {4, 5}}
    #
    # constraints = create_constraint_dict(words)
    # # constraints = create_constraint_dict(words[7])
    # with localtimer():
    #     Pickle.write(constraints=constraints)


if __name__ == '__main__':
    # _test_creation()
    do_the_thing()
    # words = read_words('silas_7.txt')
    # # print(list(chain.from_iterable(words.values())))
    # constraints = create_constraint_dict(chain.from_iterable(words.values()))
    #
    # # Pickle.write(constraints=constraints)
    # # print(list(words))
    # print(powerset_idxs(3))
    # print(get_constraint_powerset('jeb'))
