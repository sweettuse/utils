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


def text_to_speech(text: str, encoding=_tts_client.enums.AudioEncoding.LINEAR16, language_code='en-US',
                   voice_name='en-US-Wavenet-E', pitch=4, speaking_rate=1) -> bytes:
    """hit google's text-to-speech API"""
    si = tts.types.SynthesisInput(text=text)
    audio_conf = tts.types.AudioConfig(audio_encoding=encoding, pitch=pitch, speaking_rate=speaking_rate)
    voice = tts.types.VoiceSelectionParams(language_code=language_code, name=voice_name)
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

    if `n_translations` is `None`, will go through all languages
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


def __main():
    print(_translate_client.get_languages())
    res = _translate('i am the very model of the modern major general', 'fr')
    source = "a pet fanatic who lives like there’s no tomorrow"
    res = the_google_shuffle(source, n_translations=6)
    res = speech_to_text('/tmp/ggl_test_mono.wav')
    print(_parse_stt_res(res))
    sound = text_to_speech('jebtuse my main man! i am co-pi-lette')
    play_sound(sound)
    with open('/tmp/ggl.raw', 'wb') as f:
        f.write(sound)


if __name__ == '__main__':
    __main()
