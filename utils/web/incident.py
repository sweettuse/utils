import shelve

from pathlib import Path
from typing import NamedTuple

from utils.slack_api.days_since import Incident

__author__ = 'acushner'


class IncidentInfo(NamedTuple):
    username: str
    user_id: str
    channel_id: str
    incident: Incident


class IncidentHandler:
    def __init__(self, fname):
        self._shelf = shelve.open(Path(fname).parent / '.incident_store')

    def __del__(self):
        self._shelf.close()

    def register_incident(self, username, user_id, channel_id, date_str, desc):
        ii = IncidentInfo(username, user_id, channel_id, Incident(date_str, desc))
        self._shelf[ii] = ii


def __main():
    pass


if __name__ == '__main__':
    __main()
