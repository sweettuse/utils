import asyncio
import random
from collections import defaultdict
from contextlib import asynccontextmanager
from typing import Set, Union, List, Optional

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
    default_eyes = 'e_DefaultContent.jpg'

    def __init__(self, mood: Mood):
        self.mood = mood
        self.is_good = mood in good_moods

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
        async with api.movement.reset_to_orig():
            await wait_for_group(
                self._set_eyes(),
                self._set_posture(),
                random_sound(self.mood)
            )
            yield

        await api.images.display(self.default_eyes)

    async def _set_posture(self):
        await (good_posture if self.is_good else bad_posture)()

    async def _set_eyes(self):
        await api.images.display(random.choice(eyes[self.mood]))

    @property
    def xmas_saying(self):
        return bxt.nice if self.is_good else bxt.naughty


class PersonalResponse:
    def __init__(self, phrase, mood: Optional[Union[Mood, List[Mood]]] = None):
        self.phrase = phrase

        if mood:
            self.moods = [mood] if isinstance(mood, Mood) else mood
        else:
            self.moods = list(Mood)

    async def respond(self):
        state = State(random.choice(self.moods))
        async with state.set():
            await say(self.phrase)
            await state.xmas_saying


people = dict(
    annika=PersonalResponse("oh annika oh annika come light the menorah", Mood.joy),
    lee=PersonalResponse("lee, you are the man now dog", Mood.love),
    ray=PersonalResponse('my man, mr ray of sunshine', Mood.amazement),
    ben_yi=PersonalResponse('yo ben "tupperware" yi!', Mood.ecstacy),
    rich_wong=PersonalResponse('hey rich, good to see you!', Mood.amazement),
    ben_ross=PersonalResponse("hey big ben, my friend is the VP of a startup that uses agile principals "
                              "to accelerate ROI and QSP against multi-metric PI-based employee incentive plans,"
                              "i think we should bring her in to help with Q1 BDD-based development operations",
                              Mood.rage),
    cush=PersonalResponse("the tuse is loose!", Mood.rage),
    curt=PersonalResponse('corn on the curt!', Mood.amazement),
    du=PersonalResponse("du. du hast. du hast mich!", [Mood.rage, Mood.anger, Mood.annoyance]),
    hemanth=PersonalResponse('I have the power! Mr. Heman himself!', Mood.ecstacy),
    ishiak=PersonalResponse('Hey hot stuff!', Mood.love),
    jason=PersonalResponse('jason, sing me giant steps!', Mood.awe),
    mel=PersonalResponse("mel, you're the best for bringing the pizza"),
    mukesh=PersonalResponse("hi mukesh, you always look so fresh"),
    olivia=PersonalResponse("hey Olivia, make sure you tag me on your instagram story"),
    pat=PersonalResponse("hey Pat, I'm so happy I can call you my friend"),
    rouzbeh=PersonalResponse("hey Rouzbeh, I'm the Data Science now."),
    sara=PersonalResponse("hey Sara, looks like you are a cat lover who has a great sense of style"),
    tom=PersonalResponse("hello thomas 'steve' wagner, hope you have a nice day"),
    victor=PersonalResponse("hey victor, we should hang out more, my number is 867.5309"),
    gerry=PersonalResponse("hey gerry, analyze this:", Mood.annoyance),
)


# ======================================================================================================================

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
        self._responding = False

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
            if not self._responding and self._last_acked.set(name):
                try:
                    self._responding = True
                    await self._respond(person)
                finally:
                    self._responding = False

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
            await asyncio.sleep(80)
        finally:
            api.ws.unsubscribe_all()


def __main():
    # print(eyes[Mood.amazement])
    asyncio.run(RecognizeAndRespond().run())
    pass


if __name__ == '__main__':
    __main()
