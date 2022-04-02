from __future__ import annotations

from collections import defaultdict
from enum import Enum
from functools import partial
from itertools import count, product
from random import randint
from typing import NamedTuple

from rich import box
from rich.console import Group
from rich.table import Table, Column
from rich.text import Text


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
        res: dict[str, dict[int, str]] = defaultdict(dict)
        for ws, w in clues.items():
            res[ws.dir.value][ws.clue_num] = w
        return cls(board, {dir: dict(sorted(v.items())) for dir, v in res.items()})

    def board_to_table(self, starting_grid: Grid, color=None) -> Table:
        color = color or random_color()
        num_rows = len(starting_grid)
        num_cols = len(starting_grid[0])
        res: list[list[Text | None]] = [[None] * num_cols for _ in range(num_rows)]  

        for r, c in product(range(num_rows), range(num_cols)):
            cell = self.board.get((r, c))
            if not cell:
                if starting_grid[r][c]:
                    cell = ' '
                else:
                    cell = Text(' ', style=f'{color} on {color}', justify='center')
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


def gen_colors():
    from utils.rich_utils import good_color
    for idx in count(randint(0, 1000), randint(1, 120)):
        yield good_color(idx)


def random_color():
    return next(gen_colors())
