from __future__ import annotations
import time
from collections import Counter
from itertools import product
from typing import NamedTuple, FrozenSet, Set, Optional

from utils.assets_path import ASSETS_PATH
from utils.core import Coord
import utils.core as U

__author__ = 'acushner'

_neighbor_offsets = {Coord(*xy) for xy in product(range(-1, 2), range(-1, 2))} - {Coord(0, 0)}


class BSRule(NamedTuple):
    """born/survive rulestring

    e.g.: B3/S23
    """
    born: FrozenSet[int]
    survive: FrozenSet[int]

    @classmethod
    def from_str(cls, s):
        b, s = s.split('/')
        to_fs = lambda _s: frozenset(map(int, _s[1:]))
        return cls(to_fs(b), to_fs(s))


class GameOfLife:
    """conway's game of life"""

    def __init__(self, rule: BSRule, alive: Set[Coord]):
        self.alive = alive
        self.rule = rule

    @classmethod
    def from_pattern(cls, p: Pattern):
        return cls(p.rule, p.start)

    def tick(self):
        living_neighbor_count = Counter(c + offset
                                        for c in self.alive
                                        for offset in _neighbor_offsets)
        res = {c
               for c, v in living_neighbor_count.items()
               if c not in self.alive and v in self.rule.born}
        res.update(c for c in self.alive if living_neighbor_count[c] in self.rule.survive)
        self.alive = res

    def display(self, size=10):
        res = [['.'] * size for _ in range(size)]
        for c in self.alive:
            res[c.y][c.x] = '\u2588'
        U.exhaust(map(print, (''.join(r) for r in res)))
        print('=' * size)


# ======================================================================================================================
# game of life patterns
# see https://www.conwaylife.com/wiki/Main_Page
# ======================================================================================================================

class Pattern(NamedTuple):
    rule: BSRule
    start: FrozenSet[Coord]

    @classmethod
    def _parse_file(cls, fname):
        with open(ASSETS_PATH / fname) as f:
            return frozenset(Coord(c_num, r_num)
                             for r_num, r in enumerate(l for l in f if not l.startswith('!'))
                             for c_num, v in enumerate(r)
                             if v == 'O')

    @classmethod
    def from_file(cls, rule: BSRule, fname: str):
        fname = fname.rstrip('.cells') + '.cells'
        return cls(rule, cls._parse_file(fname))


class _pattern:
    """class property that simplifies creating patterns

    if no filename is passed in, it will use the `name` as passed into `__set_name__`
    """

    def __set_name__(self, owner, name):
        p = Pattern.from_file(self._rule, self._fname or name)
        if self._offset != Coord(0, 0):
            p = Pattern(p.rule, frozenset(c + self._offset for c in p.start))
        self._pattern = p

    def __init__(self, rs: str = 'B3/S23', fname: Optional[str] = None, offset=Coord(0, 0)):
        self._rule = BSRule.from_str(rs)
        self._fname = fname
        self._offset = offset

    def __get__(self, instance, owner):
        return self._pattern


class PMeta(type):
    """simple metaclass to make `Patterns` iterable"""

    def __iter__(cls):
        return (getattr(cls, n) for n, p in vars(cls).items() if isinstance(p, _pattern))


class Patterns(metaclass=PMeta):
    glider = _pattern()
    beacon = _pattern(offset=Coord(1, 1))
    pulsar = _pattern(offset=Coord(1, 1))
    figure_eight = _pattern(offset=Coord(5, 5))
    pentadecathlon = _pattern(offset=Coord(3, 6))
    grmdat = _pattern(offset=Coord(2, 2))
    grmdat2 = _pattern(offset=Coord(5, 5))
    diamond = _pattern(offset=Coord(2, 3), fname='4812diamond')


class BigPatterns(Patterns, metaclass=PMeta):
    two_engine_cordership = _pattern()


def __main():
    gol = GameOfLife.from_pattern(Patterns.grmdat2)
    for _ in range(24):
        gol.display(16)
        gol.tick()
        time.sleep(.5)


if __name__ == '__main__':
    __main()
