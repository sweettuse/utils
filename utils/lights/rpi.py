__author__ = 'acushner'

import random
import time
from contextlib import suppress

from lifxlan3.routines.tile.snek import run_as_ambiance, SnekSucceeds, SnekDead

from utils.lights.tile_game_of_life import TileGameOfLife


gol = lambda: TileGameOfLife.from_random().run()
funcs = [run_as_ambiance, gol, gol]


def run_on_rpi():
    random.seed(time.time())
    while True:
        with suppress(Exception):
            random.choice(funcs)()
            time.sleep(.5)


def __main():
    run_on_rpi()


if __name__ == '__main__':
    __main()
