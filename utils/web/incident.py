import atexit
import shelve
from collections import defaultdict
from itertools import count

from cluegen import FrozenDatum, cluegen as cluegen_deco

from utils.core import DataStore
from utils.slack_api import incident_info_path
from utils.slack_api.days_since import Incident

__author__ = 'acushner'


class IncidentInfo(FrozenDatum):
    id: str
    user_name: str
    user_id: str
    channel_id: str
    incident: Incident

    @cluegen_deco
    def __getitem__(cls):
        return '\n'.join((
            'def __getitem__(self, item):',
            f'    return getattr(self, item)'
        ))

    def get(self, item):
        try:
            return self[item]
        except AttributeError:
            return None

    @property
    def cache_vals(self):
        for field in 'user_name', 'user_id', 'channel_id':
            yield self[field]


class IncidentStore:
    def __init__(self):
        self.incidents = defaultdict(set)
        self._id_gen = count()

    @property
    def next_id(self) -> str:
        return f'inc_id_{next(self._id_gen):05}'

    def add(self, user_name, user_id, channel_id, desc: str) -> IncidentInfo:
        ii = IncidentInfo(self.next_id, user_name, user_id, channel_id, Incident.from_desc(desc))
        for v in ii.cache_vals:
            self.incidents[v].add(ii)
        self.incidents[ii.id] = ii
        return ii

    def rm(self, ii_id):
        ii = self.incidents.pop(ii_id, None)
        if ii is None:
            raise ValueError(f'unable to find id {ii_id}')

        for v in ii.cache_vals:
            self.incidents[v].remove(ii)
        return ii


def init_incident_store(fname='') -> IncidentStore:
    key = '_incident_store'
    shelf = shelve.open(fname or incident_info_path)
    incident_store = shelf.get(key, IncidentStore())

    def _at_close():
        shelf[key] = incident_store
        shelf.close()

    atexit.register(_at_close)
    return incident_store


def __main():
    pass


if __name__ == '__main__':
    __main()
