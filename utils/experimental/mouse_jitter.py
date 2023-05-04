import time

import pyautogui
from itertools import cycle


def move_mouse():
    for o in cycle((1, -1)):
        x, y = pyautogui.position()
        pyautogui.moveTo(x + o, y + o)
        time.sleep(1)


if __name__ == '__main__':
    move_mouse()
