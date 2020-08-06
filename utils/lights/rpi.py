__author__ = 'acushner'

import random
import time
from contextlib import suppress

from lifxlan3.routines.tile.cli import run_animate
from lifxlan3.routines.tile.snek import run_as_ambiance

from utils.lights.tile_game_of_life import TileGameOfLife

gol = lambda: TileGameOfLife.from_random().run()
anim = lambda: run_animate(sleep_secs=2, in_terminal=False, as_ambiance=True, duration_secs=60)
funcs = [run_as_ambiance, gol, gol, anim, anim]


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
