__author__ = 'acushner'

import time
from collections import defaultdict
import random
from typing import Optional, NamedTuple

from lifxlan3 import Colors, timer
from lifxlan3.routines.tile.core import set_cm
from lifxlan3.routines.tile.tile_utils import RC, ColorMatrix

from utils.game_of_life import GameOfLife, Patterns, Pattern
from utils.lights.color_func import ColorFunc, BaseColorFunc, PhaseColorFunc, default_color_func


class TileGameOfLife:
    def __init__(self, pattern: Pattern = Patterns.glider, color_func: ColorFunc = default_color_func,
                 sleep_time=1, *, rotate_every: Optional[int] = None, shape=RC(16, 16), run_time_secs=60):
        self._gol = GameOfLife.from_pattern(pattern)
        self._color_func = color_func
        self._rotate_every = rotate_every
        self._sleep_time = sleep_time
        self._shape = shape

        self._cur_iteration = 0
        self._run_time_secs = run_time_secs

    @classmethod
    def from_pattern(cls, p: Pattern):
        return cls(p, **pattern_settings.get(p)._asdict())

    @classmethod
    def from_random(cls):
        return cls(random.choice(list(Patterns)), BaseColorFunc.from_random(), sleep_time=random.random() + 1.5,
                   rotate_every=random.randrange(4), run_time_secs=random.randint(30, 90))

    @property
    def _cur_colors(self):
        alive = {RC(*reversed(c)) % self._shape for c in self._gol.alive}
        return [self._color_func(rc, rc in alive, self._cur_iteration) for rc in RC(0, 0).to(self._shape)]

    @property
    @timer
    def cm(self):
        cm = ColorMatrix.from_colors(self._cur_colors, self._shape)
        if self._rotate_every:
            cm = cm.rotate_clockwise((self._cur_iteration // self._rotate_every) % 4)
        if self._shape != RC(16, 16):
            cm = cm.resize(RC(16, 16))
        return cm

    def tick(self):
        self._gol.tick()
        self._cur_iteration += 1

    def run(self):
        start = time.time()
        while True:
            set_cm(self.cm, strip=False)
            self.tick()
            if time.time() - start > self._run_time_secs:
                break
            time.sleep(self._sleep_time)


class TGOLSettings(NamedTuple):
    color_func: ColorFunc = default_color_func
    sleep_time: int = 1
    rotate_every: Optional[int] = None


pattern_settings = defaultdict(TGOLSettings)
pattern_settings[Patterns.pulsar] = TGOLSettings(color_func=PhaseColorFunc(Colors.COPILOT_BLUE_GREEN, 46),
                                                 rotate_every=1)


def __main():
    # TileGameOfLife.from_random().run()
    TileGameOfLife(Patterns.beacon).run()
    # print(PhaseColorFunc.from_random())
    # print(BaseColorFunc.from_random())
    # print(choice(list(Patterns)))
    # tgol = TileGameOfLife(Patterns.pulsar, color_func=DefaultColorFunc())
    # TileGameOfLife.from_pattern(Patterns.pulsar).run()


if __name__ == '__main__':
    __main()
