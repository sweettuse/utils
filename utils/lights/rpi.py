__author__ = 'acushner'

import random
import time
from contextlib import suppress
from itertools import repeat, chain
from queue import Queue, Empty

from lifxlan3 import Dir, LifxLAN
from lifxlan3.routines.tile.cli import run_animate
from lifxlan3.routines.tile.core import get_tile_chain, translate
from lifxlan3.routines.tile.snek import run_as_ambiance

from utils.font_to_bitmap import load_font
from utils.lights.tile_game_of_life import TileGameOfLife
from utils.weather import weather

gol = lambda: TileGameOfLife.from_random().run()
anim = lambda: run_animate(sleep_secs=2, in_terminal=False, as_ambiance=True, duration_secs=60)

msg_queue = Queue()

fnt = load_font('Courier New.ttf', 50)


def display_msgs():
    with suppress(Empty):
        while True:
            msg = msg_queue.get_nowait()
            translate(fnt.to_color_matrix(f'!! {msg} !!'), in_terminal=False, split=False, dir=Dir.left, n_iterations=1,
                      pixels_per_step=2, sleep_secs=.05)
            time.sleep(.5)


def _get_weather():
    msg_queue.put(weather('07302'))


func_weights = {run_as_ambiance: 10,
                gol: 20,
                anim: 20,
                _get_weather: 5,
                }
# func_weights = {run_as_ambiance: 10}

funcs = [f for fn, num_times in func_weights.items() for f in repeat(fn, num_times)]


def run_on_rpi():
    random.seed(time.time())
    while True:
        with suppress(Exception):
            random.choice(funcs)()
            time.sleep(.5)
        display_msgs()


def __main():
    run_on_rpi()


if __name__ == '__main__':
    __main()
