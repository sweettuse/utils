from __future__ import annotations
from collections import Counter

from operator import attrgetter
import random
import time
from dataclasses import dataclass
from typing import FrozenSet, Set, Dict, Union, Tuple

from lifxlan3 import Color, Colors
from lifxlan3.routines.tile.core import set_cm
from lifxlan3.routines.tile.tile_utils import ColorMatrix, RC, default_color

__author__ = 'acushner'

_colors = Colors.GREEN, Colors.PINK, Colors.BLUE, Colors.ORANGE, Colors.RED

HEIGHT = 16
WIDTH = 16
tile_shape = RC(HEIGHT, WIDTH)
PADDLE_SIZE = 4
BLOCK_SIZE = 2


def _to_frozenset(rc: RC, size=1):
    return frozenset(rc + RC(0, n) for n in range(size))

@dataclass
class ObjBase:
    pos: RC
    width: int
    color: Color = Colors.SNES_LIGHT_PURPLE

    def __init_subclass__(cls) -> None:
        dataclass(cls)

    @property
    def coords(self):
        return _to_frozenset(self.pos, self.width)

    def __contains__(self, rc: RC):
        return rc in self.coords

    def __iter__(self):
        return iter(self.coords)

class Paddle(ObjBase):
    def move(self, dist: RC):
        self.pos += dist
        if self.left_pos < 0:
            self.pos = self.pos._replace(c=0)
        elif self.right_pos >= WIDTH:
            self.pos = self.pos._replace(c=WIDTH - self.width)

    @property
    def left_pos(self):
        return self.pos.c

    @property
    def right_pos(self):
        return self.pos.c + self.width - 1
    
    @property
    def coords(self):
        return _to_frozenset(self.pos, self.width)


class Block(ObjBase):
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


class EndGame(Exception):
    pass
class YouLose(EndGame):
    """represent that you have died"""


class YouWin(EndGame):
    """represent that you have won"""


class Arkanoid:
    """the classic game, breakout"""

    def __init__(self, shape=tile_shape, *, block_size=BLOCK_SIZE):
        self._shape = shape
        self._blocks = self._init_blocks(self._shape, block_size)
        self._ball, self._paddle = self._init_ball_and_paddle(self._shape)
        print(self._paddle)
        self._cur_paddle_dir = RC(0, -1)

    @classmethod
    def _init_blocks(cls, shape, block_size) -> Dict[RC, Block]:
        res = {}
        fill_pct = random.randint(50, 100) / 100
        for rc in RC(0, 0).to(RC(shape.r // 3, shape.c), col_inc=block_size):
            if random.random() < fill_pct:
                block = Block(rc, block_size, _colors[rc.r % len(_colors)])
                for v in block:
                    res[v] = block
        return res

    @classmethod
    def _init_ball_and_paddle(cls, shape) -> Tuple[Ball, Paddle]:
        start = RC(shape.r - 1, random.randrange(shape.c - PADDLE_SIZE))
        ball = Ball(start - RC(1, 0))
        return ball, Paddle(start, PADDLE_SIZE)

    @property
    def cm(self) -> ColorMatrix:
        colors = [self._get_color(rc) for rc in RC(0, 0).to(self._shape)]
        return ColorMatrix.from_colors(colors, self._shape)

    def _get_color(self, rc) -> Color:
        if rc in self._blocks:
            return self._blocks[rc].color
        elif rc == self._ball.pos:
            return self._ball.color
        elif rc in self._paddle:
            return self._paddle.color
        return default_color

    def _paddle_dir(self) -> RC:
        res = random.choice([RC(0, -1), RC(0, 1)])
        return res

    def _update_paddle(self):
        self._paddle.move(self._paddle_dir())

    def _handle_collisions(self):
        """collide against adjacent blocks/wall if necessary

        return next ball position"""
        bd = self._ball.dir

        # check row and column
        next_dir = self._process_ball(RC(bd.r, 0)) + self._process_ball(RC(0, bd.c))

        # if it hasn't changed, check the diagonal
        if next_dir == bd:
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
            if not self._blocks:
                raise YouWin('congrats, you have won!!')

        elif next_pos in self._paddle:
            if next_pos.c == self._paddle.left_pos:
                return RC(-1, -1)  # up and left
            elif next_pos.c == self._paddle.right_pos:
                return RC(-1, 1)  # up and right
            # todo @cush: better way to not get stuck up and down
            # todo @cush if it's gone up and down once or twice AND the paddle hasn't moved, go a different direction
            return RC(-1, random.choice([-1, 0, 1]))

        elif not next_pos.in_bounds(RC(0, 0), self._shape):
            if next_pos.r >= self._shape.r:
                raise YouLose('nice try! :)')
            offset = -offset
        return offset

    def _remove_block(self, block: Block):
        for rc in block:
            del self._blocks[rc]

    def tick(self):
        self._update_paddle()
        self._handle_collisions()

    def display(self, in_terminal=True):
        set_cm(self.cm, in_terminal=in_terminal, verbose=False, strip=False)


class ArkanoidSmartish(Arkanoid):
    def _paddle_dir(self) -> RC:
        ball_col = self._ball.pos.c
        speed = random.choice(list(range(1, self._paddle.width)))
        offset = RC(0, 0)
        if ball_col <= self._paddle.left_pos:
            offset = RC(0, -speed)
        elif ball_col >= self._paddle.right_pos:
            offset = RC(0, speed)
        print(f'{offset=}')
        return offset


def __main():
    a = ArkanoidSmartish()
    for _ in range(1000):

        a.display()
        # print(a._ball.pos)

        a.tick()
        print('==============================')
        time.sleep(0.1)


if __name__ == '__main__':
    __main()
