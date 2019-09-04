from contextlib import suppress
from typing import NamedTuple

import bs4
import pandas as pd
from bs4 import BeautifulSoup

__author__ = 'acushner'


def get_table_rows():
    with open('/tmp/wit', 'rb') as f:
        data = f.read()
    soup = BeautifulSoup(data, features='html.parser')
    table = soup.find('table')
    return table.find_all('tr')


def is_header(fields):
    with suppress(IndexError):
        return fields[0] in '01'


def is_body(fields):
    return fields[0].startswith('primary')


def _fields(r):
    t = ' '.join(r.get_text('|').split())
    return [s.strip().lower() for s in t.split('|')]


class Header(NamedTuple):
    fave: bool
    name: str
    email: str
    phone: str

    title: str
    employer: str
    location: str
    years_exp: int

    college: str
    degree: str

    @classmethod
    def from_soup(cls, fields):
        if '@' not in fields[3]:
            fields.insert(3, '')
        fields[-4] = float(fields[-4])
        fave = fields[0] == '0'
        return cls(fave, *fields[2:-1])


class Body(NamedTuple):
    languages: str
    relo: str
    i9: str
    skills: str
    enjoyment: str
    impact: str

    @classmethod
    def from_soup(cls, fields):
        starts = 'skills:', 'what do you enjoy about engineering?', 'how do you want to impact tech?'
        for s in starts:
            fields[fields.index(s)] = '|'
        answers = ' '.join(fields[6:]).split('|')
        final = [*fields[1:6:2], *answers[1:]]
        return cls(*final)


class Both(NamedTuple):
    header: Header
    body: Body

    @property
    def dict(self):
        return {**self.header._asdict(), **self.body._asdict()}


def __main():
    res = []
    rows = get_table_rows()
    for r in rows[5:]:
        fields = _fields(r)
        if is_header(fields):
            cur_header = Header.from_soup(fields)
        elif is_body(fields):
            res.append(Both(cur_header, Body.from_soup(fields)))
    df = pd.DataFrame([b.dict for b in res])
    df.to_csv('/tmp/andiamo', index=False)


if __name__ == '__main__':
    __main()
