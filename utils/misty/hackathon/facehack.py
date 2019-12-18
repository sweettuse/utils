import asyncio
from collections import defaultdict
from typing import Set, Union, List

from utils.misty import Routine, arrow, search, api, SubPayload, flash, play, Mood, SubType

__author__ = 'acushner'

from utils.misty.routines.recognize_face import colors
from utils.misty.routines.text import bt


class _RecogFaceRoutine(Routine):
    def __init__(self):
        super().__init__('rfr')
        self.forgot = [
            "ooh, i can't remember your name",
            "ooh, i'm sorry, i forgot your name!",
        ]

        self.response = [
            "come work for copilot!",
            "copilot at xaxis is a ton of fun",
            "good to see you again!",
        ]


rfr = _RecogFaceRoutine()


class State:
    def __init__(self, mood: Union[Mood, List[Mood]]):
        self.mood = [mood] if isinstance(mood, Mood) else mood

    def say(self, text):
        """use google tts to say something on misty"""

    def set_state(self):
        """apply mood to misty. reset when done"""


class Person:
    def __init__(self, name, misty_state: State):
        self.name = name
        self.misty_state = misty_state

    def respond(self):
        pass


people = dict(ray=Person('mr. worldwide', State(Mood.amazement)))


class _LastAcked:
    def __init__(self, ack_secs=60):
        self._last_acked = defaultdict(lambda: arrow.Arrow.min)
        self._ack_secs = ack_secs

    def set(self, name):
        now = arrow.utcnow()
        if (now - self._last_acked[name]).total_seconds() > self._ack_secs:
            self._last_acked[name] = now
            return True


class RecognizeAndRespond:
    def __init__(self):
        self._names: Set[str]
        self._search_task: asyncio.Task
        self._last_acked = _LastAcked()

    async def _init_search(self):
        self._search_task = asyncio.create_task(search(do_reset=False))

    async def _on_recognized(self, sp: SubPayload):
        """
        "eventName": "FaceRecognition-0001",
        "message": {
            "bearing": 0,
            "created": "2019-09-03T23:41:04.7853578Z",
            "distance": 165,
            "elevation": -9,
            "personName": "ftuid_e8d2fc5a",
            "sensorId": "cv",
            "trackId": 25
        """
        name = sp.data.message.personName
        person = people.get(name)
        if person:
            if self._last_acked.set(name):
                await self._respond(name)

    async def _respond(self, name):
        if self._search_task:
            self._search_task.cancel()
        await asyncio.sleep(.2)
        await api.movement.halt()
        await self._init_search()

    async def _greet(self, name):
        t = asyncio.create_task(flash(colors, images, on_time_secs=.4, off_time_secs=.05, flashlight=False))
        await bt.greeting
        if name in self._names:
            await play(UID.from_name(name).audio_misty)
        else:
            await rfr.forgot
        await rfr.response
        await bt.thanks
        t.cancel()

    async def _subscribe(self):
        await api.faces.start_recognition()
        await api.ws.subscribe(SubType.face_recognition, self._on_recognized, 1000)

    async def run(self):
        try:
            await self._init_search()
            await self._subscribe()
            await asyncio.sleep(50)
        finally:
            api.ws.unsubscribe_all()


def __main():
    asyncio.run(RecognizeAndRespond().run())
    pass


def __main():
    pass


if __name__ == '__main__':
    __main()
