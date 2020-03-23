from __future__ import annotations
import time
from collections import Counter
from itertools import product
from pathlib import Path
from typing import NamedTuple, FrozenSet, Set, Optional

from utils.core import Coord
import utils.core as U

__author__ = 'acushner'


class BSRule(NamedTuple):
    """born/survive rulestring

    e.g.: B3/S23
    """
    born: FrozenSet[int]
    survive: FrozenSet[int]

    @classmethod
    def from_str(cls, s):
        b, s = s.split('/')
        return cls(frozenset(int(v) for v in b[1:]), frozenset(int(v) for v in s[1:]))


_offsets = {Coord(*xy) for xy in product(range(-1, 2), range(-1, 2))}
_offsets.remove(Coord(0, 0))


class GameOfLife:
    def __init__(self, rule: BSRule, init_coords: Set[Coord]):
        self.alive = init_coords
        self.rule = rule

    @classmethod
    def from_pattern(cls, p: Pattern):
        return cls(p.rule, p.start)

    def tick(self):
        neighbors = Counter(c + offset for c in self.alive for offset in _offsets)
        res = {c for c, v in neighbors.items() if v in self.rule.born and c not in self.alive}
        res.update(c for c in self.alive if neighbors[c] in self.rule.survive)
        self.alive = res

    def display(self, size=10):
        res = [['.'] * size for _ in range(size)]
        for c in self.alive:
            res[c.y][c.x] = '\u2588'
        U.exhaust(map(print, (''.join(r) for r in res)))
        print('=' * size)


class Pattern(NamedTuple):
    rule: BSRule
    start: FrozenSet[Coord]

    @classmethod
    def _parse_file(cls, fn):
        with open(Path(__file__).parent / 'assets' / fn) as f:
            return {Coord(c_num, r_num)
                    for r_num, r in enumerate(l for l in f if not l.startswith('!'))
                    for c_num, v in enumerate(r)
                    if v == 'O'}

    @classmethod
    def from_file(cls, rule: BSRule, fn: str):
        fn = fn.rstrip('.cells') + '.cells'
        return cls(rule, cls._parse_file(fn))


class _pattern:
    """class property that simplifies creating patterns

    if no `fn` is passed in, it will use the `name` as passed into `__set_name__`
    """

    def __set_name__(self, owner, name):
        p = Pattern.from_file(self._rule, self._fn or name)
        if self._offset != Coord(0, 0):
            p = Pattern(p.rule, frozenset(c + self._offset for c in p.start))
        self._pattern = p

    def __init__(self, rs: str = 'B3/S23', fn: Optional[str] = None, offset=Coord(0, 0)):
        self._rule = BSRule.from_str(rs)
        self._fn = fn
        self._offset = offset

    def __get__(self, instance, owner):
        return self._pattern


class PMeta(type):
    """simple Patterns metaclass"""
    def __iter__(cls):
        return (getattr(cls, n) for n, p in vars(cls).items() if isinstance(p, _pattern))


class Patterns(metaclass=PMeta):
    """good for tile use"""
    glider = _pattern()
    beacon = _pattern(offset=Coord(1, 1))
    pulsar = _pattern(offset=Coord(1, 1))
    figure_eight = _pattern(offset=Coord(5, 5))
    pentadecathlon = _pattern(offset=Coord(3, 6))


class BigPatterns(Patterns):
    two_engine_cordership = _pattern()


def __main():
    gol = GameOfLife.from_pattern(Patterns.pentadecathlon)
    for _ in range(15):
        gol.display(20)
        gol.tick()
        time.sleep(1)


if __name__ == '__main__':
    __main()