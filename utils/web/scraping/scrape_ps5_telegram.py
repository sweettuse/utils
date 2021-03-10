import os

import arrow
import keyring
from more_itertools import first
from telethon import TelegramClient, events, sync

from utils.core import exhaust, sms

api_id = keyring.get_password('telegram', 'api_id')
api_hash = keyring.get_password('telegram', 'api_hash')

client = TelegramClient('session_name', api_id, api_hash)
client.start()


def _get_instock_channel_id():
    ds = client.get_dialogs()
    channel = first(d for d in ds if d.name.startswith('NowInStock.net'))
    # channel = first(d for d in ds if d.name.startswith('tuse'))
    return client.get_entity(channel).id


print(_get_instock_channel_id())


@client.on(events.NewMessage(chats=[_get_instock_channel_id()]))
async def handler(event):
    event_msg = event.message.message
    words = event_msg.split()
    now = arrow.now()
    for address in words:
        if address.startswith('https'):
            os.system(f'open {address}')
            print(f'{now}: {address}')
            sms(f'{keyring.get_password("phone", "number")}@msg.fi.google.com', address[8:])


def __main():
    with client:
        client.loop.run_forever()


if __name__ == '__main__':
    __main()
