import asyncio
import shelve
from contextlib import suppress, contextmanager
from pathlib import Path
from uuid import uuid4

import uvloop
from misty_py.api import MistyAPI

from utils.aio.core import run_in_executor

uvloop.install()

api = MistyAPI()
__author__ = 'acushner'


class UID:
    """UID used for interacting with misty"""

    def __init__(self, prefix=''):
        self.uid = self._init_uid(prefix)

    @classmethod
    def from_name(cls, uid):
        res = cls()
        res.uid = uid
        return res

    @staticmethod
    def _init_uid(prefix):
        _base = hex(uuid4().fields[0])[2:]
        return ('' if not prefix else f'{prefix}_') + _base

    @property
    def image(self):
        return self.uid

    @property
    def audio(self):
        return f'{self.uid}.wav'

    @property
    def audio_misty(self):
        return f'{self.uid}_misty.wav'

    async def prompt_name(self):
        async def _prompt():
            with suppress(asyncio.TimeoutError):
                name = await asyncio.wait_for(run_in_executor(input, "type in name: "), 20)
                if name:
                    await asyncio.gather(
                        run_in_executor(self._store, name),
                        self._name_to_misty(name),
                    )

        print()
        return asyncio.create_task(_prompt())

    async def _name_to_misty(self, name):
        from utils.ggl.ggl_async import atext_to_speech
        misty_audio = await atext_to_speech(name)
        await api.audio.upload(self.audio_misty, data=misty_audio)

    @classmethod
    @contextmanager
    def _open_store(cls):
        with shelve.open(str(Path('~/.misty_store').expanduser())) as db:
            yield db

    def _store(self, name):
        with self._open_store() as db:
            db[self.uid] = name

    def _from_store(self):
        with self._open_store() as db:
            return db.get(self.uid)

    @classmethod
    def dump_store(cls):
        with cls._open_store() as db:
            for pair in db.items():
                print(pair)

    def __str__(self):
        return self.uid


def __main():
    pass
    # print(asyncio.run(get_actuator_positions()))
    # asyncio.run(say("hey philip, how's it going?"))


if __name__ == '__main__':
    __main()
