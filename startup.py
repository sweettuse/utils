import pandas as pd
import numpy as np
from functools import partial, wraps, cache
from collections import defaultdict, Counter, deque
from itertools import accumulate, chain, combinations, combinations_with_replacement, compress, count, cycle, dropwhile, filterfalse, groupby, islice, permutations, product, repeat, starmap, takewhile, tee, zip_longest
from operator import itemgetter, attrgetter


try:
    import silly
except:
    s = 'unable to import silly!'
else:
    s = '{} {} has {}'.format(silly.title(), silly.name(), silly.a_thing())

banner = len(s) * '='
try:
    from rich import print, inspect, box
    help_orig = help
    help = partial(inspect, methods=True, help=True)
    from rich.table import Table
    from rich.style import Style

except ModuleNotFoundError:
    s += '\nunable to import rich'
else:
    s += '\n:tada: [green on purple]rich[/] [red bold]installed :tada:'

print()
print(banner)
print(s)
print(banner)

