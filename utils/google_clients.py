import random
from contextlib import suppress
from io import BytesIO
from itertools import chain
from typing import Union, List, NamedTuple, Optional
from more_itertools import interleave

from google.cloud import speech, texttospeech as tts, translate
from utils.core import play_sound

__author__ = 'acushner'

_tts_client = tts.TextToSpeechClient()
_stt_client = speech.SpeechClient()
_translate_client = translate.Client()


def ssmlify_text(text):
    if text.startswith('<speak>'):
        return text
    return f'<speak>{text}</speak>'


def text_to_speech(text: str, encoding=_tts_client.enums.AudioEncoding.MP3, language_code='en-US',
                   voice_name='en-US-Wavenet-E', pitch=2, speaking_rate=1) -> bytes:
    """hit google's text-to-speech API"""
    si = tts.types.SynthesisInput(ssml=ssmlify_text(text))
    audio_conf = tts.types.AudioConfig(audio_encoding=encoding, pitch=pitch, speaking_rate=speaking_rate)
    voice = tts.types.VoiceSelectionParams(language_code=language_code, name=voice_name, ssml_gender='FEMALE')
    return _tts_client.synthesize_speech(si, voice, audio_conf).audio_content


def speech_to_text(file_or_path: Union[bytes, BytesIO, str]):
    """hit google's speech-to-text API"""
    if isinstance(file_or_path, BytesIO):
        file_or_path = file_or_path.read()
    elif isinstance(file_or_path, str):
        with open(file_or_path, 'rb') as f:
            file_or_path = f.read()

    audio = speech.types.RecognitionAudio(content=file_or_path)
    recog_conf = speech.types.RecognitionConfig(encoding=speech.enums.RecognitionConfig.AudioEncoding.LINEAR16,
                                                language_code='en-US')

    res = _stt_client.recognize(recog_conf, audio)
    return _parse_stt_res(res)


def _parse_stt_res(res):
    """parse result from a request to speech-to-text"""
    res = str(res.results[0].alternatives[0])
    transcript, confidence, *_ = res.rsplit('\n', -1)
    with suppress(Exception):
        transcript = transcript.split(maxsplit=1)[1]
    with suppress(Exception):
        confidence = float(confidence.split(maxsplit=1)[1])
    return transcript, confidence


class TranslationRes(NamedTuple):
    translation: str
    target_language: str
    source: str
    source_language: str


class LangInfo(NamedTuple):
    lang: str
    name: str

    @classmethod
    def from_google(cls, data):
        return cls(data['language'], data['name'])


def _translate(data: Union[str, List[str]], target_language: str, source_language: str = 'en') -> TranslationRes:
    res = _translate_client.translate(data, target_language=target_language, source_language=source_language)
    return TranslationRes(res['translatedText'], target_language, data, source_language)


def the_google_shuffle(data, n_translations: Optional[int] = 6, source_language='en', *,
                       show_intermediate_results: bool = False):
    """
    mutate a sentence by passing it through n_translations languages
    it's like the game of "telephone"

    if `n_translations` is `None`, will go through all languages, which is perhaps not the best move
    """
    langs = [d['language'] for d in _translate_client.get_languages()]
    random.shuffle(langs)
    langs = [source_language] + langs[:n_translations] + [source_language]
    for source, target in zip(langs, langs[1:]):
        if source == target:
            continue
        print(source, '-->', target, end=': ')
        trans = _translate(data, target, source)
        if show_intermediate_results:
            if target != source_language:
                # translate intermediate steps back to source
                to_source = _translate(trans.translation, target_language=source_language, source_language=target)
                print(to_source.translation)
            else:
                print(trans.translation)
        else:
            print()
        data = trans.translation
    return trans


def _translate_simpsons_quote(s: str):
    num, rest = s.split(maxsplit=1)
    r = text_to_speech(rest)
    with open(f'/tmp/simpsons/simpsons_{num}mp3', 'wb') as f:
        f.write(r)


def translate_simpsons_quotes():
    with open('/tmp/simpsons_quotes.txt') as f:
        for line in f:
            _translate_simpsons_quote(line)


suffix_type_dict = dict(mp3=_tts_client.enums.AudioEncoding.MP3,
                        wav=_tts_client.enums.AudioEncoding.LINEAR16)


def _stt():
    res = speech_to_text('/tmp/ftuid_be4724e4.wav')
    print(res)


def __main():
    return _stt()
    # t = _translate_client.get_languages()
    # translate_simpsons_quotes()
    t = '<speak>to help you remain tranquil in the face of almost-certain death, smooth jazz will be deployed in ' \
        '3<break time="850ms"/>2<break time="850ms"/>1<break time="850ms"/></speak>'
    # t = 'ready to have your face trained? look at me and smile. keep looking at me until the music stops playing'
    # t = '<speak>starting in 3<break time="850ms"/>2<break time="850ms"/>1<break time="850ms"/></speak>'
    t = "now that i recognize you, i'll be seeing you around!"
    suffix = 'wav'
    r = text_to_speech(t, suffix_type_dict[suffix])
    play_sound(r)
    with open(f'/tmp/see_you_around.{suffix}', 'wb') as f:
        f.write(r)
    # print([l for l in t if 'span' in l['name'].lower()])
    # t = t
    # print(_translate('my god, tatiana you are such a beauty!', 'es'))

    # res = _translate('i am the very model of the modern major general', 'fr')
    # source = "a pet fanatic who lives like there’s no tomorrow"
    # res = the_google_shuffle(source, n_translations=6)
    # res = speech_to_text('/tmp/ggl_test_mono.wav')
    # print(_parse_stt_res(res))
    # sound = text_to_speech('sweettuse: recognized!  playing theme song')
    # play_sound(sound)
    # with open('/tmp/sweettuse_recognized.mp3', 'wb') as f:
    #     f.write(sound)


if __name__ == '__main__':
    __main()
