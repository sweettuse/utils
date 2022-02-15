import os
from concurrent.futures import ProcessPoolExecutor
from itertools import count
from random import randint

import imgkit
from PIL import Image
from rich.console import Console
from rich.table import Table

from utils.crossword_gen.core import BoardInfo, Grid, Board, random_color

console = Console(width=60, force_terminal=True, file=open('/dev/null', 'w'),
                  record=True)


def _save(table: Table, html_name, img_name):
    console.print(table, width=60)
    console.save_html(html_name)
    return _write_img(html_name, img_name)


def _write_img(html_file, out_file):
    imgkit.from_file(html_file, out_file)
    return out_file


class GifRecorder:

    def __init__(self, grid: Grid, record_every=1):
        self._images = []
        self._id = randint(1, 100000)
        self._file_count = count()
        self._num_record_calls = count()
        self._record_every = record_every
        self._grid = grid
        self._futures = []
        self._pool = ProcessPoolExecutor(12)
        self._color = random_color()

    def record(self, board: Board):
        if next(self._num_record_calls) % self._record_every:
            return
        table = BoardInfo(board, None).board_to_table(self._grid, self._color)
        num = next(self._file_count)
        html_name = self._filename('html', num)
        img_name = self._filename('jpg', num)
        self._futures.append(
            self._pool.submit(_save, table, html_name, img_name)
        )

    def _write_img(self, html_file: str, num: int):
        out = self._filename('jpg', num)
        imgkit.from_file(html_file, out)
        self._images.append(out)

    def _filename(self, typ, num: int) -> str:
        return f'/tmp/gif_recorder_{self._id}_{typ}_{num:05d}.{typ}'

    @property
    def _tmp_files(self):
        for filename in sorted(os.listdir('/tmp')):
            if f'gif_recorder_{self._id}_jpg' in filename:
                yield filename

    def to_gif(self):
        self.to_gif_static(f.result() for f in self._futures)

    @staticmethod
    def to_gif_static(filenames):
        first, *rest = map(Image.open, filenames)
        first.save('/tmp/out.gif', save_all=True, append_images=rest,
                   duration=240, optimize=True, loop=64)


def from_tmp(gr_id: int):
    names = sorted(os.listdir('/tmp'))
    images = []
    for fname in names:
        if f'gif_recorder_{gr_id}_jpg_' in fname:
            images.append(f'/tmp/{fname}')
    GifRecorder.to_gif_static(images)

    pass


def __main():
    return from_tmp(19587)
    g = [
        [1, 1, 1],
        [1, 0, 1],
        [1, 1, 1],
    ]
    gr = GifRecorder(g)
    gr.record({(0, 0): 'a'})


if __name__ == '__main__':
    __main()
