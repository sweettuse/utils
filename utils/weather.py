from functools import lru_cache
from pathlib import Path
from typing import NamedTuple, Union, Dict

import requests

__author__ = 'acushner'


class LatLon(NamedTuple):
    lat: float
    lon: float

    @property
    def joined(self) -> str:
        return f'{self.lat},{self.lon}'


class _ZC:
    @property
    @lru_cache(1)
    def _zip_codes(self):
        def to_zc_ll(s: str):
            zc, lat, lon = s.split(',')
            return zc, LatLon(float(lat), float(lon))

        with open(Path(__file__).parent / 'assets/zip/zipcodes.txt') as f:
            next(f)
            return dict(map(to_zc_ll, f))

    def __getitem__(self, key):
        key = str(key)
        return self._zip_codes[(5 - len(key)) * '0' + key]


zip_codes: Dict[str, LatLon] = _ZC()


class NWS:
    """interface for weather.gov"""

    def __init__(self, lat_lon: LatLon):
        self.lat_lon = lat_lon

    @property
    def info(self):
        """get general info based on lat lon"""
        return requests.get(f'https://api.weather.gov/points/{self.lat_lon.joined}').json()


def weather(zip_code_5: Union[str, int]):
    nws = NWS(zip_codes[zip_code_5])
    forecast_url = nws.info['properties']['forecast']
    forecast = requests.get(forecast_url).json()
    return forecast['properties']['periods'][0]['detailedForecast']


def __main():
    pass


if __name__ == '__main__':
    __main()
