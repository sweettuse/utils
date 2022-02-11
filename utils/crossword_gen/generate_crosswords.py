from __future__ import annotations

from collections import defaultdict
from copy import deepcopy
from enum import Enum
from itertools import product, count
from random import shuffle, randint
from typing import NamedTuple

from rich import box, print
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from utils.core import timer, take


class Dir(Enum):
    down = 'down'
    right = 'right'


class WordStart(NamedTuple):
    rc: Coord
    dir: Dir


Coord = tuple[int, int]  # row, col
Grid = list[list[int]]
WordInfo = dict[WordStart, list[Coord]]


def read_words(filename='qtyp.txt') -> dict[int, set[str]]:
    res = defaultdict(set)
    with open(filename) as f:
        for l in f:
            l = l.strip().lower()
            res[len(l)].add(l)
    return res


def _matches(words, constraints, seen=frozenset()):
    return (w for w in words
            if w not in seen
            and all(w[offset] == char for offset, char in constraints))


def _order_dict_by_word_len_freq(words, word_starts: WordInfo):
    freqs = {length: len(ws) for length, ws in words.items()}
    freqs = sorted(freqs, key=freqs.__getitem__)
    return dict(sorted(word_starts.items(), key=lambda kv: freqs.index(len(kv[1]))))


def _to_word_grid(words, g: Grid) -> WordInfo:
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
    rights = set()
    downs = set()
    num_rows = len(g)
    num_cols = len(g[0])

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
        if ((r, c) not in rights
                and _valid(r, c + 1)
                and g[r][c + 1]):
            word_coords = list(_chain_right(r, c))
            res[WordStart((r, c), Dir.right)] = word_coords
            rights.update(word_coords)

        if ((r, c) not in downs
                and _valid(r + 1, c)
                and g[r + 1][c]):
            word_coords = list(_chain_down(r, c))
            res[WordStart((r, c), Dir.down)] = word_coords
            downs.update(word_coords)

    res = dict(sorted(res.items(), key=lambda kv: len(kv[1])))
    # order by connectivity
    return _order_dict_by_word_len_freq(words, res)


@timer
def wafflify(words, word_starts: WordInfo) -> dict[Coord, str]:
    """generate crossword!

    so-named after silas' original idea that kinda looks like a waffle:
    [
        [1, 1, 1, 1, 1],
        [1, 0, 1, 0, 1],
        [1, 1, 1, 1, 1],
        [1, 0, 1, 0, 1],
        [1, 1, 1, 1, 1],
    ]
    """
    len_to_words = {k: list(v) for k, v in words.items()}
    for words in len_to_words.values():
        shuffle(words)

    def _constraints(coords, board):
        return [(i, v) for i, coord in enumerate(coords)
                if (v := board.get(coord))]

    def place(remaining: list[WordStart], board: dict[Coord, str], seen=frozenset()):
        if not remaining:
            return board

        word_start, *remaining = remaining
        coords = word_starts[word_start]
        constraints = _constraints(coords, board)

        board = board.copy()
        for w in _matches(len_to_words[len(coords)], constraints, seen):
            for coord, char in zip(coords, w):
                board[coord] = char
            if res := place(remaining, board, seen | {w}):
                return res
        return False

    return place(list(word_starts), {})


def _to_table(starting_grid, board, color) -> Table:
    num_rows = len(starting_grid)
    num_cols = len(starting_grid[0])
    res = [[None] * num_cols for _ in range(num_rows)]

    for r, c in product(range(num_rows), range(num_cols)):
        cell = board.get((r, c), Text(' ', style=f'{color} on {color}', justify='center'))
        res[r][c] = Text.assemble(' ', cell, ' ')
    table = Table(show_header=False, box=box.HEAVY, border_style=color, padding=0)
    for row in res:
        table.add_row(*row, end_section=True)
    return table


def __main():
    g = [
        [1, 1, 1, 1, 1],
        [1, 0, 1, 0, 1],
        [1, 1, 1, 1, 1],
        [1, 0, 1, 0, 1],
        [1, 1, 1, 1, 1],

    ]
    words = read_words('qtyp.txt')
    wg = _to_word_grid(words, g)
    colors = gen_colors()
    tables = []
    for c in take(1, colors):
        waffled = wafflify(words, wg)
        tables.append(_to_table(g, waffled, c))
        tables.append(31 * '=')

    console = Console(record=True)
    tables.pop()
    console.print(*tables)
    console.save_html('/tmp/xwords.html')


def _words_and_freqs():
    t = Table('word_len', 'count', border_style='blue')

    words = read_words()
    for k in sorted(words):
        t.add_row(str(k), str(len(words[k])))
        if len(words[k]) <= 8:
            print(words[k])
    print(t)


def gen_colors():
    from utils.rich_utils import good_color
    for idx in count(randint(0, 100000), randint(1, 120)):
        yield good_color(idx)


def playaround():
    g = [
        [1, 0, 0, 0, 1],
        [1, 0, 0, 0, 1],
        [1, 1, 1, 1, 1],
        [1, 0, 0, 1, 1],
        [1, 1, 1, 1, 1],
        [0, 0, 1, 0, 1],
    ]
    # g = [[1] * 3 for _ in range(3)]
    words = read_words()
    wg = _to_word_grid(words, g)
    colors = gen_colors()
    for _ in range(100):
        waffled = wafflify(words, wg)
        print(_to_table(g, waffled, next(colors)))
    print(list(product(range(3), range(3))))


if __name__ == '__main__':
    __main()

    # playaround()
    # __main()
