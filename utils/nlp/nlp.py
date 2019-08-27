import re
from collections import defaultdict
from itertools import groupby
from pathlib import Path
from pprint import pprint
from typing import NamedTuple

import spacy
from spacy.tokens import Token

__author__ = 'acushner'

nlp = spacy.load('en_core_web_sm')


class Tok(NamedTuple):
    pos: str
    tag: str

    @classmethod
    def from_token(cls, t: Token):
        return cls(t.pos_, t.tag_)

    @property
    def key(self):
        return f'__'.join(self)

    def is_valid(self, text):
        return text.isalnum() and not re.match('[0-9][fF]', text) and (self.pos == 'PRON' or len(text) > 1)


def _parse_simpsons():
    with open(Path(__file__).parent / 'simpsons.txt') as f:
        doc = nlp(f.read())

    res = defaultdict(set)
    for tok in doc:
        t = Tok.from_token(tok)
        if t.is_valid(tok.text):
            res[t].add(tok.text.lower())

    # for tok in sorted(res):
    #     for _, w in zip(range(20), res[tok]):
    #         print(f'{tok.key}:{w}')

    with open('/tmp/words', 'w') as f:
        for k in sorted(res):
            f.write(f'self.{k.key} = {sorted(res[k])}\n')
    #     print(f'self.{k.key} = {sorted(res[k])}')

    print('total words', sum(len(words) for words in res.values()))
    # for pos, tags in res.items():
    #     for t, vals in tags.items():
    #         for _, v in zip(range(20), vals):
    #             print(f'{pos}|{t}|{v}')

    return res


pos_map = {
    'ADJ': 'adjective',
    'ADP': 'adposition',
    'ADV': 'adverb',
    'AUX': 'auxiliary',
    'CCONJ': 'coordinating conjunction',
    'DET': 'determiner',
    'INTJ': 'interjection',
    'NOUN': 'noun',
    'NUM': 'numeral',
    'PART': 'particle',
    'PRON': 'pronoun',
    'PROPN': 'proper noun',
    'PUNCT': 'punctuation',
    'SCONJ': 'subordinating conjunction',
    'SYM': 'symbol',
    'VERB': 'verb',
    'X': 'other'
}


def __main():
    res = _parse_simpsons()
    tags = sorted({tag for pos, tags in res.items() for tag in tags})
    print()

    # pprint(dict(zip(res, map(spacy.explain, res))))
    # print()
    # pprint(dict(zip(tags, map(spacy.explain, tags))))


if __name__ == '__main__':
    __main()
