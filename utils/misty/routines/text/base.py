from utils.misty.routine import Routine

__author__ = 'acushner'


class _BaseText(Routine):
    def __init__(self):
        super().__init__('base')

        self.alright = [
            "alright",
            "alrighty then",
            "ok",
            "ok then",
            "cool",
            "neato",
        ]

        self.greeting = [
            "hello!",
            "hi there",
            "greetings",
            "how's it going?",
            "hi!",
            "good to see you",
            "howdy",
            "good afternoon",
        ]

        self.thanks = [
            "thanks",
            "thank you",
            "great",
        ]

        self.emphatic = [
            "so much",
            "a lot",
            "very much",
        ]

        self.swears = [
            "shit",
            "fuck",
            "ass",
            "damn",
            "cunt",
            "motherfucker",
            "dick",
            "dickface",
            "bitch",
            "fuck me in the ass",
            "anus",
            "douche",
            "son of a bitch",
            "butthole",
            "assface",
        ]
        self.party_time = [
            "it's party time!",
            "time to get our party on!",
            "who wants to rock out?",
            "i'm such a dork, but let's party anyway!"
        ]


bt = _BaseText()


async def to_misty():
    for _ in range(10):
        await bt.swears


def __main():
    bt.generate('party_time')
    # print(bt.get_filenames())
    # print(bt.swears)
    # asyncio.run(to_misty())
    # pass


if __name__ == '__main__':
    __main()
