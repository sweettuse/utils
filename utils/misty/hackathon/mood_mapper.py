from enum import Enum

from utils.misty import Mood
from utils.misty.core import api


import logging

__author__ = 'byi'

log = logging.getLogger(__name__)


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

good_moods = {Mood[m] for m in 'acceptance amazement awe ecstacy joy love phrase sleepy'.split()}


async def good_posture():
    await api.movement.move_head(0, 40, 0, 90)


async def bad_posture():
    await api.movement.move_head(-80, 0, 0, 90)
