from __future__ import annotations

import time
from collections import defaultdict
from contextlib import suppress
from enum import Enum
from functools import partial
from itertools import product, count, cycle, repeat
from random import shuffle, randint
from typing import NamedTuple, Iterable

from rich import box, print
from rich.console import Console, Group
from rich.table import Table, Column
from rich.text import Text

from utils.core import timer, interleave
from utils.crossword_gen.generate_constraints import ConstraintManager


class Dir(Enum):
    down = 'down'
    right = 'across'


class WordStart(NamedTuple):
    rc: Coord
    dir: Dir
    clue_num: int
    _right_count = count(1)
    _down_count = count(1)

    @classmethod
    def init(cls):
        cls._right_count = count(1)
        cls._down_count = count(1)

    @classmethod
    def new_right(cls, r, c):
        return cls((r, c), Dir.right, next(cls._right_count))

    @classmethod
    def new_down(cls, r, c):
        return cls((r, c), Dir.down, next(cls._down_count))


class BoardInfo(NamedTuple):
    """stores what a finished board looks like as well as the words used"""
    board: Board
    clues: dict[str, dict[int, str]]

    @classmethod
    def from_board_clues(cls, board: Board, clues: dict[WordStart, str]):
        res = defaultdict(dict)
        for ws, w in clues.items():
            res[ws.dir.value][ws.clue_num] = w
        return cls(board, {dir: dict(sorted(v.items())) for dir, v in res.items()})

    def board_to_table(self, starting_grid: Grid, color=None) -> Table:
        color = color or random_color()
        num_rows = len(starting_grid)
        num_cols = len(starting_grid[0])
        res = [[None] * num_cols for _ in range(num_rows)]

        for r, c in product(range(num_rows), range(num_cols)):
            cell = self.board.get(
                (r, c), Text(' ', style=f'{color} on {color}', justify='center')
            )
            res[r][c] = Text.assemble(' ', cell, ' ')
        table = Table(show_header=False, box=box.HEAVY, border_style=color, padding=0)
        for row in res:
            table.add_row(*row, end_section=True)
        return table

    def clues_to_table(self, color=None) -> Table:
        tables = []
        Col = partial(Column, justify='center')
        res = Table(
            *map(Col, self.clues), border_style=color or random_color(), box=box.MINIMAL
        )
        for d, num_word in self.clues.items():
            tables.append(Table(show_header=False, box=box.SIMPLE))
            t = tables[-1]
            for n, w in num_word.items():
                t.add_row(str(n), w)

        res.add_row(*tables)
        return res

    def as_table(self, starting_grid: Grid, color=None):
        color = color or random_color()
        return Group(
            self.board_to_table(starting_grid, color),
            self.clues_to_table(color),
        )


Coord = tuple[int, int]  # row, col
Grid = list[list[int]]
WordInfo = dict[WordStart, list[Coord]]
Board = dict[Coord, str]


def read_words(filename='qtyp.txt') -> dict[int, set[str]]:
    res = defaultdict(set)
    with open(filename) as f:
        for l in f:
            l = l.strip().lower()
            res[len(l)].add(l)
    return res


def _matches(words, constraints, seen=frozenset()):
    return (
        w
        for w in words
        if w not in seen and all(w[offset] == char for offset, char in constraints)
    )


def _order_dict_by_word_len_freq(words, word_info: WordInfo):
    freqs = {length: len(ws) for length, ws in words.items()}
    freqs = sorted(freqs, key=freqs.__getitem__)
    return dict(sorted(word_info.items(), key=lambda kv: freqs.index(len(kv[1]))))


def _to_word_info(words, g: Grid) -> WordInfo:
    """create a dict of WordStarts to the coords that word encompasses

    g looks something like:
    [
        [1, 1, 1],
        [1, 0, 0],
        [1, 0, 0],
    ]
    where 1 means you can place a letter and 0 means you can't

    figures out where words can start looking right and down
    """
    rights, downs = set(), set()
    num_rows, num_cols = len(g), len(g[0])
    WordStart.init()

    def _valid(r, c):
        return r < num_rows and c < num_cols

    def _chain_right(r, c):
        while _valid(r, c) and g[r][c]:
            yield r, c
            c += 1

    def _chain_down(r, c):
        while _valid(r, c) and g[r][c]:
            yield r, c
            r += 1

    res = {}
    for r, c in product(range(num_rows), range(num_cols)):
        val = g[r][c]
        if not val:
            continue
        if (r, c) not in rights and _valid(r, c + 1) and g[r][c + 1]:
            word_coords = list(_chain_right(r, c))
            res[WordStart.new_right(r, c)] = word_coords
            rights.update(word_coords)

        if (r, c) not in downs and _valid(r + 1, c) and g[r + 1][c]:
            word_coords = list(_chain_down(r, c))
            res[WordStart.new_down(r, c)] = word_coords
            downs.update(word_coords)

    res = dict(sorted(res.items(), key=lambda kv: len(kv[1])))
    # order by freq - maybe a good idea?
    return _order_dict_by_word_len_freq(words, res)


def _gen_xword_helper(cm: ConstraintManager, word_info: WordInfo,
                      abort_after_secs=0.0) -> BoardInfo:
    """heavy lifting of actually placing words and creating a BoardInfo

    if abort_after_secs is > 0, will only try for that amount of time and then bail
    reasoning is:
        that if you start with a really shitty word, it can take an
        incredibly long time to resolve.
        whereas if you start with a good word, it can be really quick
        better to bail if it's taking to long, re-shuffle, and try again then to
        go down the cursed path you accidentally chose with your bad
        random starting word
    """
    abort_after_secs = max(0.0, abort_after_secs)
    pc = time.perf_counter
    start = pc()
    clues = {}

    def place(remaining: list[WordStart], board: Board, seen=frozenset()):
        """actually attempt to place words on the board.

        recursive backtracking algorithm"""
        if not remaining:
            return board

        if abort_after_secs and (pc() - start) > abort_after_secs:
            raise TimeoutError

        word_start, *remaining = remaining
        coords = word_info[word_start]

        board = board.copy()
        for w in cm.matches(coords, board, seen):
            for coord, char in zip(coords, w):
                board[coord] = char
            clues[word_start] = w
            if res := place(remaining, board, seen | {w}):
                return res
        return False

    return BoardInfo.from_board_clues(place(list(word_info), {}), clues)


@timer
def generate_crossword(cm: ConstraintManager, word_info: WordInfo,
                       retry_after_secs=0.0) -> BoardInfo:
    """runs the function that actually generates the crossword"""
    while True:
        with suppress(TimeoutError):
            return _gen_xword_helper(cm, word_info, abort_after_secs=retry_after_secs)


def _words_and_freqs(words):
    """print a table showing word lengths and number of words of that len"""
    t = Table('word_len', 'count', 'running_total', border_style='blue')
    total = 0
    for k in sorted(words):
        cur = len(words[k])
        total += cur
        t.add_row(str(k), str(cur), str(total))
    print(t)


def gen_colors():
    from utils.rich_utils import good_color
    for idx in count(randint(0, 1000), randint(1, 120)):
        yield good_color(idx)


def random_color():
    return next(gen_colors())


def _create_waffle_grid(size):
    """the OG of all the puzzles
    [1, 1, 1, 1, 1],
    [1, 0, 1, 0, 1],
    [1, 1, 1, 1, 1],
    [1, 0, 1, 0, 1],
    [1, 1, 1, 1, 1],
    """
    assert size > 0 and size & 1, '`size` must be positive and odd'
    row1 = [1] * size
    row2 = [1] * size

    for i in range(1, size, 2):
        row2[i] = 0

    return [r for r, _ in zip(cycle((row1, row2)), range(size))]


def create_waffles(num_puzzles, size, filename, out_filename='/tmp/xwords.html'):
    g = _create_waffle_grid(size)
    cm = ConstraintManager(filename)
    wi = _to_word_info(cm.len_to_words_dict, g)

    bis = (generate_crossword(cm, wi, retry_after_secs=2) for _ in range(num_puzzles))
    _to_html(g, bis, out_filename)


def _to_html(g: Grid, bis: Iterable[BoardInfo], out_filename):
    tables = []
    for c, bi in zip(gen_colors(), bis):
        tables.append(bi.as_table(g, c))

    console = Console(record=True)
    *res, _ = interleave(tables, repeat(31 * '=', len(tables)))
    console.print(*res)
    console.save_html(out_filename)


@timer
def __main():
    return create_waffles(100, 5, 'qtyp.txt', '5_new.html')


def _run_one():
    g = _create_waffle_grid(9)
    cm = ConstraintManager('qtyp.txt')
    bi = generate_crossword(cm, _to_word_info(cm.len_to_words_dict, g))
    print(bi.as_table(g))


def generate_constraints(filename):
    cm = ConstraintManager(filename)
    cm.generate_constraints()


if __name__ == '__main__':
    # generate_constraints('silas_7.txt')
    # _words_and_freqs(read_words('qtyp.txt'))
    # _run_one()
    __main()
