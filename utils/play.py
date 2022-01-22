from collections import deque
from utils.core import *

from utils.core import SliceableDeque
def __main():
    sd = SliceableDeque([1, 2, 3])
    d = deque([1, 2, 3])
    sd[2:2] = [4, 5, 6]
    print(sd)


if __name__ == '__main__':
    __main()
