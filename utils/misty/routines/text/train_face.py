from utils.misty.routine import Routine

__author__ = 'acushner'


class _FTR(Routine):
    def __init__(self):
        super().__init__('ft')

        self.intro = [
            "hi, my name's misty! how are you?! if it's ok, i'd like to learn to recognize you",
            "hi there, misty here! how are you doing today? if you're ok with it, i'd like to train your face",
            "hi there, you can call me misty, but one of my nicknames is co-pi-lette. "
            "would you like for me to recognize you in the future?"
        ]

        self.like_to_train = "i'd like to train your face"

        self.prompt_name = [
            "would you mind telling me your name?",
            "could you please tell me your name?",
            "why don't you tell me your name?"
        ]

        self.prompt_picture = [
            "i'd like to take your picture. could you please smile for the camera?",
            "it's picture time! look at me and smile, or make a funny face, or anything, and i'll take your picture!"
        ]

        self.take_a_look = "take a look!"

        self.prompt_training = [
            "the part you've been waiting for: face training!"
        ]

        self.instructions = [
            "to successfully get your face trained, please look at me, don't move too much, and enjoy the music. ",
            "please stare into my beautiful eyes, relax, and enjoy the music!"
        ]

        self.goodbye = [
            "looking forward to seeing you around!",
            "now that i recognize you, i'm looking forward to seeing you around!",
            "woohoo! face training successful! see you around",
            "pretty easy, right? thanks for your help. see you around!"
        ]


ftr = _FTR()


def __main():
    ftr.generate('take_a_look')


if __name__ == '__main__':
    __main()
