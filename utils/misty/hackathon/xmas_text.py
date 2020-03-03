import logging

from utils.misty import Routine

__author__ = 'byi'

log = logging.getLogger(__name__)


class _BaseXmasText(Routine):
    def __init__(self):
        super().__init__('xmas')

        self.nice = [
            "You are getting a raise for Christmas! i kid, i kid, i have no money",
            "You've been very good this year. (i swear, i haven't been stalking you)",
            "merry xmas from me to you!",
            "santa told me you had a pretty good year, congrats!",
            "i saw you when you were both sleeping and awake, and i have to say you were pretty good this year",
            "happy holiday season!",
        ]

        self.naughty = [
            "Someone's been naughty this year",
            "Someone is getting a lot of coal",
            "No presents for you, one year!",
            "Sorry, you're permanently on the naughty list",
            "You are so getting coal",
            "With this much coal you're getting, you might actually bring back mining jobs",
            "No presents for you, you drink too much",
            "santa hates you and i agree",
            "kwanzaa time is near and you're getting absolutely nothing",

        ]


bxt = _BaseXmasText()

if __name__ == '__main__':
    bxt.generate()
