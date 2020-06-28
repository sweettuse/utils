import atexit
import os
import pickle
import shelve
from collections import defaultdict
from concurrent.futures.thread import ThreadPoolExecutor
from contextlib import suppress
from functools import lru_cache, wraps
from itertools import count
from typing import Dict, List, NamedTuple, Set

import arrow
from cluegen import FrozenDatum

from utils.slack_api import incident_store_path

__author__ = 'acushner'


class Incident(NamedTuple):
    date: str
    desc: str

    @classmethod
    def from_desc(cls, desc):
        return cls(arrow.now().format('YYYY-MM-DD'), desc)

    @property
    def n_days(self):
        return (arrow.now().naive - arrow.get(self.date).naive).days

    def __str__(self):
        n = self.n_days
        s = 's' if n != 1 else ''
        return f'-{n}- day{s} since {self.desc}'

    def with_emoji(self, emoji):
        return f':{emoji}: {str(self)}'


class IncidentInfo(FrozenDatum):
    id: str
    user_name: str
    user_id: str
    channel_id: str
    incident: Incident

    def __getitem__(self, item):
        return getattr(self, item)

    def get(self, item):
        try:
            return self[item]
        except AttributeError:
            return None

    def update_date(self, date_str):
        attrs = 'id user_name user_id channel_id incident'.split()
        *same, inc = (getattr(self, a) for a in attrs)
        return type(self)(*same, Incident(date_str, inc.desc))


_pool = ThreadPoolExecutor(1)


def persist_deco(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        finally:
            f = lambda: self.persist() or os.system('. ~/.slack/_cp_slack.sh')
            _pool.submit(f)

    return wrapper


class IncidentStore:
    """# TODO: this is not multiprocess ready at all"""
    _key = '_incident_store'

    def __init__(self):
        self.incidents: Dict[str, IncidentInfo] = {}
        self._id_gen = count()

    @classmethod
    def from_path(cls) -> 'IncidentStore':
        with open(incident_store_path, 'rb') as f:
            return pickle.load(f)

    def persist(self):
        with open(incident_store_path, 'wb') as f:
            pickle.dump(self, f)

    @property
    def next_id(self) -> str:
        return f'inc_id_{next(self._id_gen):03}'

    @persist_deco
    def add(self, user_name, user_id, channel_id, desc: str) -> IncidentInfo:
        ii = IncidentInfo(self.next_id, user_name, user_id, channel_id, Incident.from_desc(desc))
        self.incidents[ii.id] = ii
        return ii

    @persist_deco
    def rm(self, ii_id, user_id) -> IncidentInfo:
        ii = self.incidents.get(ii_id)
        if ii is None:
            raise ValueError(f'unable to find id {ii_id}')

        if ii.user_id != user_id:
            raise PermissionError("unable to delete an incident that isn't yours!")

        del self.incidents[ii_id]
        return ii

    @persist_deco
    def update(self, ii_id, date_str):
        ii = self.incidents.get(ii_id)
        if not ii:
            raise ValueError(f'unable to find id {ii_id}')
        self.incidents[ii_id] = ii.update_date(date_str)

    def by_user_id(self, user_id) -> List[IncidentInfo]:
        return [ii for ii in self.incidents.values() if ii.user_id == user_id]

    def group_by_channel(self) -> Dict[str, Set[IncidentInfo]]:
        res = defaultdict(set)
        for ii in self.incidents.values():
            res[ii.channel_id].add(ii)
        return res


@lru_cache(1)
def init_incident_store() -> IncidentStore:
    incident_store = IncidentStore.from_path()
    atexit.register(incident_store.persist)
    return incident_store


def __main():
    pass


if __name__ == '__main__':
    __main()
