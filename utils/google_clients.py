from contextlib import suppress
from io import BytesIO
from typing import Union

from google.cloud import speech, texttospeech as tts
from utils.core import play_sound

__author__ = 'acushner'

_tts_client = tts.TextToSpeechClient()
_stt_client = speech.SpeechClient()


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


def __main():
    res = speech_to_text('/tmp/ggl_test_mono.wav')
    print(_parse_stt_res(res))
    res = res
    return
    sound = text_to_speech('jebtuse my main man! i am co-pi-lette')
    play_sound(sound)
    with open('/tmp/ggl.raw', 'wb') as f:
        f.write(sound)


if __name__ == '__main__':
    __main()
