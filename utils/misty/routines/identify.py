import asyncio
from typing import NamedTuple, Dict

import arrow
from misty_py.api import MistyAPI
from misty_py.misty_ws import EventCallback, UnchangedValue
from misty_py.subscriptions import SubPayload, Actuator, SubType

from utils.misty import api, play, say, search


class Person(NamedTuple):
    name: str
    target_acquired_phrase: str
    theme_song: str

    async def on_find(self, api: MistyAPI):
        await api.movement.halt()
        print('first', arrow.utcnow())
        await say(self.target_acquired_phrase)
        print('first done', arrow.utcnow())

        print('second', arrow.utcnow())
        await play(self.theme_song, how_long_secs=15)
        print('second done', arrow.utcnow())


people: Dict[str, Person] = {}


def add_person(person: Person):
    people[person.name] = person


# add_person(Person('sweettuse', 'hi there, nice to see you!', 'vgm--best--2-36 Password.mp3'))
add_person(Person('ftuid_4e4509c9', "hi there, adam, nice to see you! here's a tune a know you like",
                  'vgm--best--2-36 Password.mp3'))


# add_person(Person('ftuid_d55fadec', 'hi there, adam, nice to see you!', 'vgm--best--2-36 Password.mp3'))


# add_person(Person('ftuid_86971680', 'sweettuse_recognized.mp3', 'price_is_right.mp3'))


# ======================================================================================================================


class HandleFaceRecognition:
    def __init__(self, t: asyncio.Task):
        self._t = t
        self._people = people.copy()

    async def __call__(self, sp: SubPayload):
        print('face_rec', sp)
        person = self._people.pop(sp.data.message.personName, None)
        if person:
            print('found', person)
            self._t.cancel()
            await sp.sub_id.unsubscribe()
            await person.on_find(api)
            return True


async def run():
    print('started')
    await asyncio.sleep(1)
    print('starting face recognition')
    await api.faces.start_recognition()
    t = asyncio.create_task(search(do_reset=False))
    try:
        ec = EventCallback(HandleFaceRecognition(t))
        await api.ws.subscribe(SubType.face_recognition, ec)
        await ec
        await api.faces.stop_recognition()
    except asyncio.CancelledError:
        t.cancel()
    print('done')


def __main():
    asyncio.run(run())
    print('we did something')
    pass


if __name__ == '__main__':
    __main()
