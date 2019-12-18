from enum import Enum
from utils.misty.core import api

import logging

__author__ = 'byi'

log = logging.getLogger(__name__)


class Mood(Enum):
    acceptance = 'acceptance'
    amazement = 'amazement'
    anger = 'anger'
    annoyance = 'annoyance'
    awe = 'awe'
    boredom = 'boredom'
    disapproval = 'disapproval'
    disgust = 'disgust'
    disoriented_confused = 'disoriented_confused'
    distraction = 'distraction'
    ecstacy = 'ecstacy'
    fear = 'fear'
    grief = 'grief'
    joy = 'joy'
    loathing = 'loathing'
    love = 'love'
    phrase = 'phrase'
    rage = 'rage'
    sadness = 'sadness'
    sleepy = 'sleepy'
    sleepy_snore = 'sleepy_snore'
    system = 'system'


sounds = {
    Mood.acceptance: ['s_Acceptance.wav'],
    Mood.amazement: ['s_Amazement.wav', 's_Amazement2.wav'],
    Mood.anger: ['s_Anger.wav', 's_Anger2.wav', 's_Anger3.wav', 's_Anger4.wav'],
    Mood.annoyance: ['s_Annoyance.wav', 's_Annoyance2.wav', 's_Annoyance3.wav', 's_Annoyance4.wav'],
    Mood.awe: ['s_Awe.wav', 's_Awe2.wav', 's_Awe3.wav'],
    Mood.boredom: ['s_Boredom.wav'],
    Mood.disapproval: ['s_Disapproval.wav'],
    Mood.disgust: ['s_Disgust.wav', 's_Disgust2.wav', 's_Disgust3.wav'],
    Mood.disoriented_confused: ['s_DisorientedConfused.wav', 's_DisorientedConfused2.wav',
                                's_DisorientedConfused3.wav', 's_DisorientedConfused4.wav',
                                's_DisorientedConfused5.wav', 's_DisorientedConfused6.wav'],
    Mood.distraction: ['s_Distraction.wav'],
    Mood.ecstacy: ['s_Ecstacy.wav', 's_Ecstacy2.wav'],
    Mood.fear: ['s_Fear.wav'],
    Mood.grief: ['s_Grief.wav', 's_Grief2.wav', 's_Grief3.wav', 's_Grief4.wav'],
    Mood.joy: ['s_Joy.wav', 's_Joy2.wav', 's_Joy3.wav', 's_Joy4.wav'],
    Mood.loathing: ['s_Loathing.wav'],
    Mood.love: ['s_Love.wav'],
    Mood.phrase: ['s_PhraseByeBye.wav', 's_PhraseEvilAhHa.wav', 's_PhraseHello.wav', 's_PhraseNoNoNo.wav',
                  's_PhraseOopsy.wav', 's_PhraseOwOwOw.wav', 's_PhraseOwwww.wav', 's_PhraseUhOh.wav'],
    Mood.rage: ['s_Rage.wav'],
    Mood.sadness: ['s_Sadness.wav', 's_Sadness2.wav', 's_Sadness3.wav', 's_Sadness4.wav', 's_Sadness5.wav',
                   's_Sadness6.wav', 's_Sadness7.wav'],
    Mood.sleepy: ['s_Sleepy.wav', 's_Sleepy2.wav', 's_Sleepy3.wav', 's_Sleepy4.wav', 's_SleepySnore.wav'],
    Mood.system: ['s_SystemCameraShutter.wav', 's_SystemFailure.wav', 's_SystemSuccess.wav', 's_SystemWakeWord.wav']
}

eyes = {

    Mood.acceptance: ['e_Admiration.jpg'],
    Mood.amazement: ['e_Amazement.jpg'],
    Mood.anger: ['e_Rage.jpg'],
    Mood.annoyance: ['e_Disgust.jpg'],
    Mood.awe: ['e_Joy.jpg'],
    Mood.boredom: ['e_Sleepy2.jpg', 'e_Sleepy.jpg', 'e_Sleepy3.jpg', 'e_Sleepy4.jpg'],
    Mood.disapproval: ['e_Disgust.jpg'],
    Mood.disgust: ['e_Disgust.jpg'],
    Mood.disoriented_confused: ['e_Disoriented.jpg'],
    Mood.distraction: ['e_ContentRight.jpg', 'e_ContentLeft.jpg'],
    Mood.ecstacy: ['e_EcstacyHilarious.jpg', 'e_EcstacyStarryEyed.jpg'],
    Mood.fear: ['e_Fear.jpg', 'e_Terror.jpg', 'e_Terror2.jpg', 'e_TerrorLeft.jpg', 'e_TerrorRight.jpg'],
    Mood.grief: ['e_Grief.jpg'],
    Mood.joy: ['e_Joy.jpg', 'e_Joy2.jpg', 'e_JoyGoofy.jpg', 'e_JoyGoofy2.jpg', 'e_JoyGoofy3.jpg'],
    Mood.loathing: ['e_Contempt.jpg'],
    Mood.love: ['e_Love.jpg'],
    Mood.phrase: ['e_DefaultContent.jpg'],
    Mood.rage: ['e_Rage.jpg', 'e_Rage2.jpg', 'e_Rage3.jpg', 'e_Rage4.jpg'],
    Mood.sadness: ['e_Sadness.jpg'],
    Mood.sleepy: ['e_Sleeping.jpg', 'e_SleepingZZZ.jpg'],
    Mood.system: ['e_SystemBlackScreen.jpg', 'e_SystemCamera.jpg', 'e_SystemFlash.jpg', 'e_SystemGearPrompt.jpg',
                  'e_SystemLogoPrompt.jpg'],
}

posture = {

    # Mood.acceptance: dict(move_head= lambda)

    Mood.amazement: ['e_Amazement.jpg'],
    Mood.anger: ['e_Rage.jpg'],
    Mood.annoyance: ['e_Disgust.jpg'],
    Mood.awe: ['e_Joy.jpg'],
    Mood.boredom: ['e_Sleepy2.jpg', 'e_Sleepy.jpg', 'e_Sleepy3.jpg', 'e_Sleepy4.jpg'],
    Mood.disapproval: ['e_Disgust.jpg'],
    Mood.disgust: ['e_Disgust.jpg'],
    Mood.disoriented_confused: ['e_Disoriented.jpg'],
    Mood.distraction: ['e_ContentRight.jpg', 'e_ContentLeft.jpg'],
    Mood.ecstacy: ['e_EcstacyHilarious.jpg', 'e_EcstacyStarryEyed.jpg'],
    Mood.fear: ['e_Fear.jpg', 'e_Terror.jpg', 'e_Terror2.jpg', 'e_TerrorLeft.jpg', 'e_TerrorRight.jpg'],
    Mood.grief: ['e_Grief.jpg'],
    Mood.joy: ['e_Joy.jpg', 'e_Joy2.jpg', 'e_JoyGoofy.jpg', 'e_JoyGoofy2.jpg', 'e_JoyGoofy3.jpg'],
    Mood.loathing: ['e_Contempt.jpg'],
    Mood.love: ['e_Love.jpg'],
    Mood.phrase: ['e_DefaultContent.jpg'],
    Mood.rage: ['e_Rage.jpg', 'e_Rage2.jpg', 'e_Rage3.jpg', 'e_Rage4.jpg'],
    Mood.sadness: ['e_Sadness.jpg'],
    Mood.sleepy: ['e_Sleeping.jpg', 'e_SleepingZZZ.jpg'],
    Mood.system: ['e_SystemBlackScreen.jpg', 'e_SystemCamera.jpg', 'e_SystemFlash.jpg', 'e_SystemGearPrompt.jpg',
                  'e_SystemLogoPrompt.jpg'],

}


async def good_posture():
    await api.movement.move_head(0, 40, 0, 90)


async def bad_posture():
    await api.movement.move_head(-80, 0, 0, 90)
