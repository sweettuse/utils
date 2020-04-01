import random
import time
from dataclasses import dataclass
from typing import FrozenSet, Set, Dict, Union, Tuple

from lifxlan3 import Color, Colors
from lifxlan3.routines.tile.core import set_cm
from lifxlan3.routines.tile.tile_utils import ColorMatrix, RC, default_color

__author__ = 'acushner'

_colors = Colors.GREEN, Colors.PINK, Colors.BLUE, Colors.ORANGE, Colors.RED

tile_shape = RC(16, 16)
PADDLE_SIZE = 2
BLOCK_SIZE = 2


@dataclass
class Paddle:
    pos: FrozenSet[RC]
    color: Color = Colors.SNES_LIGHT_PURPLE

    def move(self, dir: RC):
        start = min(self.pos)
        start += dir
        print('before', self.pos)
        self.pos = _to_frozenset(start, PADDLE_SIZE)
        print('after', self.pos)


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


@dataclass
class Ball:
    pos: RC
    dir: RC = RC(-1, -1)
    color: Color = Colors.WHITE


class YouLose(Exception):
    """represent that you have died"""


class YouWin(Exception):
    """represent that you have died"""


def _to_frozenset(rc: RC, size=1):
    return frozenset(rc + RC(0, n) for n in range(size))


class Arkanoid:
    """the classic game, breakout"""

    def __init__(self, shape=tile_shape, *, block_size=BLOCK_SIZE):
        self._shape = shape
        self._blocks = self._init_blocks(self._shape, block_size)
        self._ball, self._paddle = self._init_ball_and_paddle(self._shape)
        self._cur_paddle_dir = RC(0, -1)

    @classmethod
    def _init_blocks(cls, shape, block_size) -> Dict[RC, Block]:
        res = {}
        for rc in RC(0, 0).to(RC(shape.r // 3, shape.c), col_inc=block_size):
            block = Block(_to_frozenset(rc, block_size), _colors[rc.r % len(_colors)])
            for v in block.pos:
                res[v] = block
        return res

    @classmethod
    def _init_ball_and_paddle(cls, shape) -> Tuple[Ball, Paddle]:
        start = RC(shape.r - 1, random.randrange(shape.c - PADDLE_SIZE))
        ball = Ball(start - RC(1, 0))
        return ball, Paddle(_to_frozenset(start, PADDLE_SIZE))

    @property
    def cm(self) -> ColorMatrix:
        colors = [self._get_color(rc) for rc in RC(0, 0).to(self._shape)]
        return ColorMatrix.from_colors(colors, self._shape)

    def _get_color(self, rc) -> Color:
        if rc in self._blocks:
            return self._blocks[rc].color
        elif self._ball.pos == rc:
            return self._ball.color
        elif rc in self._paddle.pos:
            return self._paddle.color
        return default_color

    def _paddle_dir(self) -> RC:
        res = None
        if min(self._paddle.pos).c == 0:
            res = RC(0, 1)
        if max(self._paddle.pos).c == self._shape.c - PADDLE_SIZE:
            res = RC(0, -1)
        if not res:
            res = random.choice([RC(0, -1), RC(0, 1)])
        print(res)
        return res

    def _update_paddle(self):
        self._paddle.move(self._paddle_dir())

    def _handle_collisions(self):
        """collide against adjacent blocks/wall if necessary

        return next ball position"""
        bd = self._ball.dir

        # check row and column
        next_dir = self._process_ball(RC(bd.r, 0)) + self._process_ball(RC(0, bd.c))

        if next_dir == bd:
            # check diagonal
            next_dir = self._process_ball(bd)

        self._ball.dir = next_dir
        self._ball.pos += next_dir

    def _process_ball(self, offset) -> RC:
        next_pos = self._ball.pos + offset
        if next_pos in self._blocks:
            offset = -offset
            block = self._blocks[next_pos]
            if not block.on_collision():
                self._remove_block(block)
        elif not next_pos.in_bounds(RC(0, 0), self._shape):
            if next_pos.r >= self._shape.r:
                raise YouLose('nice try, loser :)')
            offset = -offset
        elif next_pos in self._paddle.pos:
            if next_pos == min(self._paddle.pos):
                return RC(-1, -1)
            elif next_pos == max(self._paddle.pos):
                return RC(1, -1)
        return offset

    def _remove_block(self, block: Block):
        for rc in block.pos:
            del self._blocks[rc]

    def tick(self):
        self._update_paddle()
        self._handle_collisions()

    def display(self, in_terminal=True):
        set_cm(self.cm, in_terminal=in_terminal, verbose=False, strip=False)
        time.sleep(.5)


def __main():
    a = Arkanoid()
    for _ in range(30):
        a.display()
        a.tick()


if __name__ == '__main__':
    __main()
