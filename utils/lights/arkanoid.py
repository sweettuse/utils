import random
from dataclasses import dataclass
from typing import FrozenSet, Set, Dict, Union

from lifxlan3 import Color, Colors
from lifxlan3.routines.tile.core import set_cm
from lifxlan3.routines.tile.tile_utils import ColorMatrix, RC, default_color

__author__ = 'acushner'

_colors = Colors.GREEN, Colors.PINK, Colors.BLUE, Colors.ORANGE, Colors.RED

tile_shape = RC(16, 16)


@dataclass
class Ball:
    pos: RC
    dir: RC = RC(-1, -1)
    color: Color = Colors.WHITE


@dataclass
class Paddle:
    pos: FrozenSet[RC]
    dir: RC = RC(0, 0)
    color: Color = Colors.SNES_LIGHT_PURPLE


@dataclass
class Block:
    pos: FrozenSet[RC]
    color: Color
    hp: int = 1

    def on_collision(self):
        self.hp -= 1
        return self.is_alive

    @property
    def is_alive(self):
        return self.hp > 0


def _to_frozenset(rc: RC, size=1):
    return frozenset(rc + RC(0, n) for n in range(size))


class Arkanoid:
    """the classic game, breakout"""

    def __init__(self, shape=tile_shape, *, block_size=2):
        self._shape = shape
        self._board = self._init_board(self._shape, block_size)
        self._cur_paddle_dir = RC(0, -1)

    @classmethod
    def _init_board(cls, shape, block_size) -> Dict[RC, Union[Ball, Paddle, Block]]:
        res = cls._init_blocks(shape, block_size)
        res.update(cls._init_paddle_and_ball(shape))
        return res

    @classmethod
    def _init_blocks(cls, shape, block_size) -> Dict[RC, Block]:
        res = {}
        for rc in RC(0, 0).to(RC(shape.r // 2, shape.c), col_inc=block_size):
            block = Block(_to_frozenset(rc, block_size), _colors[rc.r % len(_colors)])
            for v in block.pos:
                res[v] = block
        return res

    @classmethod
    def _init_paddle_and_ball(cls, shape):
        res = {}
        start = RC(shape.r - 1, random.randrange(shape.c - 3))
        ball = Ball(start - RC(1, 0))
        res[ball.pos] = ball

        paddle = Paddle(_to_frozenset(start, 3))
        res.update((rc, paddle) for rc in paddle.pos)
        return res

    def _get_color(self, rc) -> Color:
        if rc in self._board:
            return self._board[rc].color
        return default_color

    @property
    def cm(self) -> ColorMatrix:
        colors = [self._get_color(rc) for rc in RC(0, 0).to(self._shape)]
        return ColorMatrix.from_colors(colors, self._shape)

    def _handle_collisions(self) -> RC:
        """collide against adjacent blocks/wall if necessary

        return next ball position"""

    def tick(self):
        ball_pos = self._handle_collisions()


def __main():
    a = Arkanoid()
    set_cm(a.cm, in_terminal=True, verbose=False, strip=False)


if __name__ == '__main__':
    __main()
