from __future__ import annotations

import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from contextlib import suppress
from itertools import product, cycle, count
from random import shuffle
from typing import Iterable

from rich import print
from rich.console import Console
from rich.table import Table

from utils.core import timer, chunk
from utils.crossword_gen.core import WordStart, BoardInfo, Grid, WordInfo, Board, gen_colors
from utils.crossword_gen.generate_constraints import ConstraintManager
from utils.crossword_gen.gif_recorder import GifRecorder

console = Console(record=True)


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
                      abort_after_secs=0.0,
                      gif_recorder: GifRecorder = None) -> BoardInfo:
    """heavy lifting of actually placing words and creating a BoardInfo

    if abort_after_secs is > 0, will only try for that amount of time and then bail
    reasoning is:
        that if you start with a really shitty word, it can take an
        incredibly long time to resolve.
        whereas if you start with a good word, it can be really quick
        better to bail if it's taking to long, re-shuffle, and try again than to
        go down the cursed path you accidentally chose with your bad
        random starting word
    """
    abort_after_secs = max(0.0, abort_after_secs)
    pc = time.perf_counter
    start = pc()
    clues = {}

    def _check_board_still_valid(remaining: list[WordStart],
                                 board: Board,
                                 seen):
        for ws in remaining:
            if not cm.matches(word_info[ws], board, seen, do_shuffle=False):
                return False
        return True

    def place(remaining: list[WordStart], board: Board, seen=frozenset()):
        """actually attempt to place words on the board.

        recursive backtracking algorithm"""
        if not remaining:
            return board

        if abort_after_secs and (pc() - start) > abort_after_secs:
            raise TimeoutError

        if board and not _check_board_still_valid(remaining, board, seen):
            return False

        shuffle(remaining)
        word_start, *remaining = remaining
        coords = word_info[word_start]

        board = board.copy()
        for w in cm.matches(coords, board, seen):
            for coord, char in zip(coords, w):
                board[coord] = char
            if gif_recorder:
                gif_recorder.record(board)
            if res := place(remaining, board, seen | {w}):
                clues[word_start] = w
                return res
        return False

    board = place(list(word_info), {})
    return BoardInfo.from_board_clues(board, clues)


@timer
def generate_crossword(cm: ConstraintManager, word_info: WordInfo,
                       retry_after_secs=0.0,
                       gif_recorder: GifRecorder = None) -> BoardInfo:
    """runs the function that actually generates the crossword"""
    for i in count():
        with suppress(TimeoutError):
            return _gen_xword_helper(cm, word_info, abort_after_secs=retry_after_secs,
                                     gif_recorder=gif_recorder)


def _words_and_freqs(words):
    """print a table showing word lengths and number of words of that len"""
    t = Table('word_len', 'count', 'running_total', border_style='blue')
    total = 0
    for k in sorted(words):
        cur = len(words[k])
        total += cur
        t.add_row(str(k), str(cur), str(total))
    print(t)


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


def run_parallel(g: Grid, cm: ConstraintManager, num_puzzles, retry_after_secs=0):
    pool = ProcessPoolExecutor(8)
    wi = _to_word_info(cm.len_to_words_dict, g)
    futures = [pool.submit(generate_crossword, cm, wi, retry_after_secs)
               for _ in range(num_puzzles)]
    return (f.result() for f in as_completed(futures))


def create_waffles(num_puzzles, size, filename, out_filename='/tmp/xwords.html'):
    """create waffles sequentially"""
    g = _create_waffle_grid(size)
    cm = ConstraintManager(filename)
    wi = _to_word_info(cm.len_to_words_dict, g)

    bis = (generate_crossword(cm, wi, retry_after_secs=2) for _ in range(num_puzzles))
    _to_html(g, bis, out_filename)


def create_waffles_parallel(num_puzzles, size, filename, out_filename='/tmp/xwords.html',
                            chunk_size=8):
    """create waffles in parallel"""
    g = _create_waffle_grid(size)
    cm = ConstraintManager(filename)
    for bis in chunk(run_parallel(g, cm, num_puzzles, retry_after_secs=30), chunk_size):
        _to_html(g, bis, out_filename, clear_html_buffer=False)


def _to_html(g: Grid, bis: Iterable[BoardInfo], out_filename, *, clear_html_buffer=True):
    tables = (bi.as_table(g, c)
              for c, bi in zip(gen_colors(), bis))
    console.print(*tables)
    console.save_html(out_filename, clear=clear_html_buffer)


def _run_one(*, size_or_grid: int | Grid = 5, to_gif=False, retry_after_secs=0.0):
    g = size_or_grid
    if isinstance(size_or_grid, int):
        g = _create_waffle_grid(size_or_grid)
    cm = ConstraintManager('qtyp.txt')
    wi = _to_word_info(cm.len_to_words_dict, g)
    gif_recorder = GifRecorder(g) if to_gif else None
    bi = generate_crossword(cm, wi, gif_recorder=gif_recorder, retry_after_secs=retry_after_secs)
    print(bi.as_table(g))
    if to_gif:
        gif_recorder.to_gif()


def generate_constraints(filename):
    cm = ConstraintManager(filename)
    cm.generate_constraints(lambda word_len: word_len == 11)


def gen_nines():
    return create_waffles_parallel(16, 9, 'qtyp.txt', out_filename='the_nines.html', chunk_size=1)


def gen_elevens():
    return create_waffles_parallel(4, 11, 'qtyp.txt', out_filename='the_elevens.html', chunk_size=1)


@timer
def __main():
    square = 6
    g = [[1] * square for _ in range(square)]
    # return _run_one(size_or_grid=g, to_gif=True, retry_after_secs=.1)
    for _ in range(3):
        _run_one(size_or_grid=11, to_gif=False, retry_after_secs=.15)
    return
    for _ in range(10):
        _run_one(size_or_grid=9, to_gif=False, retry_after_secs=.1)
    return

    return gen_elevens()
    return generate_constraints('qtyp.txt')
    return create_waffles_parallel(100, 7, 'silas_7.txt', out_filename='/tmp/silas_100_7.html')


if __name__ == '__main__':
    __main()
