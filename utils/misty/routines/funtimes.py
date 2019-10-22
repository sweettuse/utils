import asyncio
from utils.misty import search, api
from utils.misty.core import UID

__author__ = 'acushner'


async def investigate():
    while True:
        await asyncio.sleep(30)
        await api.images.take_picture(UID('wit'))


async def run():
    asyncio.create_task(search())
    await investigate()


def __main():
    asyncio.run(run())
    pass


if __name__ == '__main__':
    __main()
