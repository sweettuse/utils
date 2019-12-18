import logging

from utils.misty import Routine

__author__ = 'byi'

log = logging.getLogger(__name__)


class _BaseXmasText(Routine):
    def __init__(self):
        super().__init__('xmas')

        self.nice = [
            "You are getting a raise for Christmas!",
            "You've been very good this year",
            "You are a rockstar!",
            "You are the sweetest!",
        ]

        self.naughty = [
            "Someone's been naughty this year",
            "Someone is getting a lot of coal",
            "No presents for you",
            "Sorry, you're permanently on the naughty list",
            "You are so getting coal",
            "With this much coal you're getting, you might actually bring back mining jobs",
            "No presents for you, you drink too much",
        ]


bxt = _BaseXmasText()
