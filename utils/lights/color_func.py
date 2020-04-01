import random
from abc import ABC, abstractmethod
from collections import deque
from itertools import cycle
from typing import Callable

from lifxlan3 import Color, Themes, Theme, Colors
from lifxlan3.routines.tile.tile_utils import RC, default_color

__author__ = 'acushner'

ColorFunc = Callable[[RC, bool, int], Color]


# default_color = Colors.SNES_DARK_GREY


def _choose_from(c_or_t):
    return random.choice(list(c_or_t))[1]


def default_color_func(rc: RC, alive: bool, iteration: int) -> Color:
    t = list(Themes.rainbow_2)
    if alive:
        return t[sum(map(abs, rc)) % len(t)]
    return default_color


class BaseColorFunc(ABC):
    _registered = set()

    def __init_subclass__(cls, **kwargs):
        cls._registered.add(cls)

    @abstractmethod
    def __call__(self, rc: RC, alive: bool, iteration: int) -> Color:
        """return color based on position, whether it's alive, and iteration"""

    @classmethod
    @abstractmethod
    def from_random(cls):
        """instantiate an instance of the class with random settings"""
        return random.choice(list(cls._registered)).from_random()


class DefaultColorFunc(BaseColorFunc):
    """wend way through theme of colors"""

    def __init__(self, theme: Theme = Themes.rainbow):
        self._colors = deque(256 * list(theme))
        self._color_iter = iter(self._colors)
        self._cur_iteration = None

    def __call__(self, rc: RC, alive: bool, iteration: int):
        if self._cur_iteration != iteration:
            self._cur_iteration = iteration
            self._colors.rotate(-2)
            self._color_iter = iter(self._colors)
        if alive:
            return next(self._color_iter)
        return default_color

    @classmethod
    def from_random(cls):
        return cls(_choose_from(Themes))


class PhaseColorFunc(BaseColorFunc):
    """move around color wheel in gradient"""

    def __init__(self, color: Color, step_degrees: int):
        self._colors = cycle(color.get_complements(step_degrees))
        self._cur_color = next(self._colors)
        self._cur_iteration = 0

    def __call__(self, rc: RC, alive: bool, iteration: int):
        if self._cur_iteration != iteration:
            self._cur_iteration = iteration
            self._cur_color = next(self._colors)
        if alive:
            return self._cur_color
        return default_color

    @classmethod
    def from_random(cls):
        return cls(_choose_from(Colors), random.randrange(13, 44))


class DistColorFunc(BaseColorFunc):
    """set colors based on distance from origin"""

    def __init__(self, theme: Theme, dist_func: Callable[[RC, int], int]) -> None:
        self._dist_func = dist_func
        self._colors = list(_choose_from(theme))

    def __call__(self, rc: RC, alive: bool, iteration: int) -> Color:
        if alive:
            return self._colors[(self._dist_func(rc, iteration)) % len(self._colors)]
        return default_color

    @classmethod
    def from_random(cls):
        return cls(_choose_from(Themes), random.choice(list(_dist_func_reg)))


_dist_func_reg = set()


def reg_dist_func(func):
    _dist_func_reg.add(func)
    return func


@reg_dist_func
def manhattan(rc: RC, iteration: int):
    return abs(rc.r) + abs(rc.c)


@reg_dist_func
def quadrant(rc: RC, iteration: int):
    res = 0
    if rc < RC(8, 8):
        res = 0
    elif rc < RC(16, 8):
        res = 1
    elif rc < RC(8, 16):
        res = 2
    elif rc < RC(16, 16):
        res = 3
    return res + iteration


# TODO: make inverted versions

def __main():
    pass


if __name__ == '__main__':
    __main()
