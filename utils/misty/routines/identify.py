import asyncio
from typing import NamedTuple, Dict

import arrow
from misty_py.api import MistyAPI
from misty_py.misty_ws import EventCallback, UnchangedValue
from misty_py.subscriptions import SubPayload, Actuator, SubType

from utils.misty import api


class Person(NamedTuple):
    name: str
    target_acquired_phrase: str
    theme_song: str

    async def on_find(self, api: MistyAPI):
        await api.movement.halt()
        print('first', arrow.utcnow())
        await api.audio.play(self.target_acquired_phrase, blocking=True)
        print('first done', arrow.utcnow())

        print('second', arrow.utcnow())
        await api.audio.play(self.theme_song, how_long_secs=10, blocking=True)
        print('second done', arrow.utcnow())


people: Dict[str, Person] = {}


def add_person(person: Person):
    people[person.name] = person


add_person(Person('sweettuse', 'sweettuse_recognized.mp3', 'price_is_right.mp3'))
add_person(Person('ftuid_86971680', 'sweettuse_recognized.mp3', 'price_is_right.mp3'))


# ======================================================================================================================


async def wait_one(sp: SubPayload):
    print('wait_one', sp)
    return True


async def _handle_head_movement(yaw):
    ecb = EventCallback(UnchangedValue())
    await api.movement.move_head(yaw=yaw)
    async with api.ws.sub_unsub(Actuator.yaw.sub, ecb, 400):
        await ecb


async def _handle_face_recognition(sp: SubPayload):
    print('face_rec', sp)
    person = people.pop(sp.data.message.personName, None)
    if person:
        print('found', person)
        await sp.sub_id.unsubscribe()
        await person.on_find(api)
        return True


async def _init_face_recognition() -> EventCallback:
    print('starting face recognition')
    await api.faces.start_recognition()
    eh = EventCallback(_handle_face_recognition)
    await api.ws.subscribe(SubType.face_recognition, eh)
    return eh


async def run():
    print('started')
    await asyncio.sleep(3)
    face_handler = await _init_face_recognition()
    await _handle_head_movement(200)
    await face_handler
    await api.faces.stop_recognition()
    print('done')


def __main():
    asyncio.run(run())
    print('we did something')
    pass


if __name__ == '__main__':
    __main()
