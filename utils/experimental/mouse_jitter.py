import time

import pyautogui
from itertools import cycle


def move_mouse():
    offsets = cycle((1, -1))
    while True:
        x, y = pyautogui.position()
        o = next(offsets)
        pyautogui.moveTo(x + o, y + o)
        time.sleep(60)


if __name__ == '__main__':
    move_mouse()
