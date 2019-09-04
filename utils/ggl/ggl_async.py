from utils.ggl.google_clients import text_to_speech, speech_to_text, translate
from utils.aio.core import make_async

__author__ = 'acushner'

atext_to_speech = make_async(text_to_speech)
aspeech_to_text = make_async(speech_to_text)
atranslate = make_async(translate)


def __main():
    pass


if __name__ == '__main__':
    __main()
