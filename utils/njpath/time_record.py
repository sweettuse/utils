import asyncio
import os
from contextlib import suppress
from enum import Enum
from typing import List, Dict
from pathlib import Path

import pandas as pd
from misty_py.utils import asyncpartial
from more_itertools import always_iterable, flatten

from utils.aio.core import run_in_executor

__author__ = 'acushner'

import requests

base_url = 'https://path.api.razza.dev/v1/stations/{}/realtime'


class Station(Enum):
    newark = 'newark'
    harrison = 'harrison'
    journal_square = 'journal_square'
    grove_street = 'grove_street'
    exchange_place = 'exchange_place'
    world_trade_center = 'world_trade_center'
    newport = 'newport'
    hoboken = 'hoboken'
    christopher_street = 'christopher_street'
    ninth_street = 'ninth_street'
    fourteenth_street = 'fourteenth_street'
    twenty_third_street = 'twenty_third_street'
    thirty_third_street = 'thirty_third_street'

    @property
    def url(self):
        return base_url.format(self.value)


t = requests.get(Station.grove_street.url).json()


async def _get_all():
    cmds = (run_in_executor(_get1, s) for s in Station)
    res = await asyncio.gather(
        *cmds
    )
    return flatten(r for r in res if r)


def _get1(s: Station):
    j = requests.get(s.url).json()
    return j.get('upcomingTrains')


_f = None
_fn = '~/.njpath/data.csv'


def _write_out(res: List[Dict]):
    header = False
    global _f
    if not _f:
        fn = Path(_fn).expanduser()
        header = not os.path.exists(fn)
        os.makedirs(Path(_fn).parent.expanduser(), exist_ok=True)
        _f = open(fn, 'a')

    pd.DataFrame(res).to_csv(_f, index=False, header=header)


async def _run():
    with suppress(Exception):
        res = await _get_all()
        return await run_in_executor(_write_out, res)


async def run(run_every_secs=30):
    while True:
        await asyncio.gather(
            _run(),
            asyncio.sleep(run_every_secs),
        )


def __main():
    return asyncio.run(run())
    # _write_out('snth')
    # return
    t = list(asyncio.run(_get_all()))
    t = t
    print(t)
    pass


if __name__ == '__main__':
    __main()
