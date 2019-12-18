import asyncio
import random
from collections import defaultdict
from contextlib import asynccontextmanager
from typing import Set, Union, List

from utils.misty import Routine, arrow, search, api, SubPayload, SubType, wait_for_group, random_sound, say, Mood
from utils.misty.hackathon.xmas_text import bxt

__author__ = 'acushner'

from utils.misty.hackathon.mood_mapper import good_posture, good_moods, bad_posture, eyes


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
        self.moods = [mood] if isinstance(mood, Mood) else mood
        self.xmas_response = random.choice(bxt.nice) if mood in good_moods else random.choice(bxt.naughty)

    def say(self, text):
        """use google tts to say something on misty"""

    @asynccontextmanager
    async def set(self):
        """
        have misty respond to person
        - set posture
        - set eyes
        - move a bit?
        - play a sound

        - address person by name and funny xmas phrase
        """
        mood = random.choice(self.moods)

        async with api.movement.reset_to_orig():
            await wait_for_group(
                self._set_posture(mood),
                self._set_eyes(mood),
                random_sound(mood)
            )
            yield

    @staticmethod
    async def _set_posture(mood):
        f = good_posture if mood in good_moods else bad_posture
        await f()

    @staticmethod
    async def _set_eyes(mood):
        await api.images.display(random.choice(eyes[mood]))


class PersonalResponse:
    default_eyes = 'e_DefaultContent.jpg'

    def __init__(self, name, misty_state: State):
        self.name = name
        self.misty_state = misty_state
        self.xmas_response = misty_state.xmas_response

    async def respond(self):
        async with self.misty_state.set():
            await say(f'hey there {self.name}')
            await asyncio.sleep(3)
            await say(f'{self.xmas_response}')


people = dict(ray=PersonalResponse('mr worldwide', State(Mood.amazement)))


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
                await self._respond(person)

    async def _respond(self, person: PersonalResponse):
        if self._search_task:
            self._search_task.cancel()
        await asyncio.sleep(.2)
        await api.movement.halt()
        await person.respond()
        await self._init_search()

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
    # print(eyes[Mood.amazement])
    asyncio.run(RecognizeAndRespond().run())
    pass


if __name__ == '__main__':
    __main()
