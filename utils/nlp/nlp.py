from collections import defaultdict
from pathlib import Path
from pprint import pprint

import spacy
from spacy.tokens import Token

__author__ = 'acushner'

nlp = spacy.load('en_core_web_sm')


def _parse_simpsons():
    with open(Path(__file__).parent / 'simpsons.txt') as f:
        doc = nlp(f.read())

    def valid(w: Token):
        return w.text.isalnum() and len(w.text) > 1

    res = defaultdict(lambda: defaultdict(set))
    for t in doc:
        if valid(t):
            res[t.pos_][t.tag_].add(t.text.lower())

    for pos, tags in res.items():
        for t, vals in tags.items():
            for _, v in zip(range(20), vals):
                print(f'{pos}|{t}|{v}')

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

    pprint(dict(zip(res, map(spacy.explain, res))))
    print()
    pprint(dict(zip(tags, map(spacy.explain, tags))))


if __name__ == '__main__':
    __main()
