import time
from collections import Counter
from itertools import product
from typing import NamedTuple, FrozenSet, Set

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


class Board:
    def __init__(self, rule: BSRule, init_coords: Set[Coord]):
        self.board = init_coords
        self.rule = rule

    def tick(self):
        neighbors = Counter(c + offset for c in self.board for offset in _offsets)
        res = {c for c, v in neighbors.items() if v in self.rule.born and c not in self.board}
        res.update(c for c in self.board if neighbors[c] in self.rule.survive)
        self.board = res

    def display(self, size=10):
        res = [['.'] * size for _ in range(size)]
        for c in self.board:
            res[c.y][c.x] = '\u2588'
        U.exhaust(map(print, (''.join(r) for r in res)))
        print('=' * size)


def __main():
    rule = BSRule.from_str('B3/S23')
    start = {Coord(2, 1), Coord(3, 2), Coord(1, 3), Coord(2, 3), Coord(3, 3)}
    b = Board(rule, start)
    for _ in range(15):
        b.display()
        b.tick()
        time.sleep(.5)


if __name__ == '__main__':
    __main()
