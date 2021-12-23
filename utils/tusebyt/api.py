from functools import partial
from tempfile import NamedTemporaryFile

import requests
import keyring
from misty_py.utils import json_obj
from utils.core import exhaust, mapt
from PIL import Image
from io import BytesIO

key = keyring.get_password('tidbyt', 'key')
device_id = keyring.get_password('tidbyt', 'device_id')
BASE_URL = 'https://api.tidbyt.com/v0'
headers = {'Authorization': f'Bearer {key}',
           'Content-Type': 'application/json'}


class TusebytAPI:
    @property
    def device_info(self):
        res = requests.get(f'{BASE_URL}/devices/{device_id}', headers=headers)
        return res.json()

    @property
    def installations(self):
        """application info of installed apps"""
        res = requests.get(f'{BASE_URL}/devices/{device_id}/installations', headers=headers)
        return mapt(json_obj, res.json()['installations'])

    @property
    def available_apps(self):
        """application info of installed apps"""
        res = requests.get(f'{BASE_URL}/apps', headers=headers)
        return res.json()['apps']

    def installations_by_app_id(self, app_id: str):
        return [i for i in self.installations if i.appID == app_id]

    def get_image(self, install_id) -> bytes:
        print(install_id)
        res = requests.get(f'{BASE_URL}/devices/{device_id}/installations/{install_id}/preview')
        return res.content

    def display_photos(self):
        for i in self.installations_by_app_id('photo'):
            im = Image.open(BytesIO(self.get_image(i.id)))
            im.show()


ep = partial(exhaust, print)

api = TusebytAPI()
# print(api.device_info)
# ep(api.installations)
print(api.display_photos())
# exhaust(print, api.available_apps)
