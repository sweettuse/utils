from utils.misty.core import Routine

__author__ = 'acushner'

r = Routine('ft')

r.intro = [
    "hi, my name's misty! how are you?! if it's ok, i'd like to train your face",
    "hi there, misty here! how are you doing today? if you're ok with it, i'd like to train your face",
    "hi there, you can call my misty, but one of my nicknames is co-pi-lette. "
    "would you like for me to recognize you in the future?"
]

r.like_to_train = "i'd like to train your face"

r.prompt_name = [
    "would you mind telling me your name?",
    "could you please tell me your name?",
    "why don't you tell me your name?"
]

r.prompt_picture = [
    "i'd like to take your picture. could you please smile for the camera?",
    "it's picture time! look at me and smile, or make a funny face, or anything, and i'll take your picture!"
]

r.prompt_training = [
    "the part you've been waiting for: face training!"
]

r.instructions = [
    "to successfully get your face trained, please look at me, don't move too much, and enjoy the music. you'll "\
    "know when it's done when you hear tada!",
    "please stare into my beautiful eyes, relax, and enjoy the music!"
]

r.goodbye = [
    "looking forward to seeing you around!",
    "now that i recognize you, i'm looking forward to seeing you around!",
    "woohoo! face training successful! see you around",
    "pretty easy, right? thanks for your help. see you around!"
]


def __main():
    print(r.get_filenames('prompt_picture').keys())
    import time
    start = time.perf_counter()
    r.generate()
    print(time.perf_counter() - start)


if __name__ == '__main__':
    __main()
