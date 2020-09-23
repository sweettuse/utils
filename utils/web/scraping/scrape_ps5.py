import time
from abc import abstractmethod
from concurrent.futures.thread import ThreadPoolExecutor
from concurrent.futures import wait
from typing import NamedTuple, Dict, Callable, Optional

import arrow
import keyring
import requests

__author__ = 'acushner'

from misty_py.utils import classproperty

from requests import Response

from utils.core import Pickle, sms

_base_headers = {}

registry = {}



class Site:
    def __init_subclass__(cls, **kwargs):
        registry[cls.__name__] = cls()

    def __init__(self):
        self._last_success = arrow.Arrow.min
        self._consecutive_hits = 0
        self.num_consec_for_success = 2

    def get(self):
        return requests.get(self.site, headers=self.headers)

    def run(self) -> bool:
        if (self._consecutive_hits >= self.num_consec_for_success
                and (arrow.now() - self._last_success).total_seconds() < 3600):
            return False

        resp = self.get()
        if resp.status_code != 200:
            self._on_error(resp)
            return False

        return self._parse(resp)

    @abstractmethod
    @classproperty
    def site(self) -> str:
        """the url to hit"""

    @classproperty
    def display_site(self) -> str:
        """the url to go to as the consumer"""
        return self.site

    @abstractmethod
    def _parse(self, resp: Response) -> bool:
        """return True if item is in stock"""

    @property
    def name(self):
        return type(self).__name__

    @classproperty
    def _specific_headers(self):
        return {}

    @property
    def headers(self):
        return {**_base_headers, **self._specific_headers}

    def _on_error(self, resp):
        print(f'{self.name}: {resp.status_code}: {resp.text}')

    def mark_success(self):
        self._last_success = arrow.now()
        self._consecutive_hits += 1
        return self._consecutive_hits

    def mark_failure(self):
        self._consecutive_hits = 0


class Amazon(Site):
    @classproperty
    def _specific_headers(self):
        return {
            'authority': 'www.amazon.com',
            'pragma': 'no-cache',
            'cache-control': 'no-cache',
            'dnt': '1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'cookie': 'skin=noskin; session-id=142-5175355-7393049; ubid-main=135-5649029-0755957; lc-main=en_US; aws-priv=eyJ2IjoxLCJldSI6MCwic3QiOjB9; aws_lang=en; s_cc=true; aws-mkto-trk=id%3A112-TZM-766%26token%3A_mch-aws.amazon.com-1574372768850-43600; aws-account-alias=952256534162; regStatus=registered; aws-ubid-main=456-1538584-1542487; lwa-context=4a8b9c8f6f6a804f8e5e91e305d5954c; appstore-devportal-locale=en_US; aws-userInfo=%7B%22arn%22%3A%22arn%3Aaws%3Aiam%3A%3A952256534162%3Auser%2Fadam.cushner%40xaxis.com%22%2C%22alias%22%3A%22952256534162%22%2C%22username%22%3A%22adam.cushner%2540xaxis.com%22%2C%22keybase%22%3A%22BbVLVtQj7lxDATtuBpms9AgzmXw9VXzUqmtAeD%2Ft%2Fto%5Cu003d%22%2C%22issuer%22%3A%22http%3A%2F%2Fsignin.aws.amazon.com%2Fsignin%22%2C%22signinType%22%3A%22PUBLIC%22%7D; x-main=M0idOlIDPHAomgfylFM3FtrN6XGvlx0b; at-main=Atza|IwEBIFdvI3wKJALGfQ6sRvk9_sc8chvtaTl2e-LpmwvDWiKSmeBqHHwuBe_jPVe89GS6pZzr5SpdPvZrsxo6Wh25zwIlab2lLyrTv5z_SjjhdRco2x84IaQosPDw8cfJ_1hg9bhaiADWKVGoZEZTGhXryOA7FFcPA-Rt8GUpuG92GQRMOyq15GgqinbjQacW1JA-c3E6jho7bIsguGjOl6bykr--; sess-at-main="GUOtDmhAZMLqy/YccevLO/Mm9Cl9Ps1JpVVhl675rw0="; sst-main=Sst1|PQHNXUHpJFAMfVXRc1gyonIOCQZXMzYirlXVGLi5KK1cvLdSvihTlNuA5AvjERT03WkwcF78byZ1yiiWrkja8J2dM8y6kw6mY4o5vNN7ZkF-r24KXVgdGIbGPA-eae_1lv8PDWlD-cp_JXPHjxwXp5lQvP-L-zs9eTnAgATihJ4wS11HYI81639vKdU417vRd99PhqMCaI2ToBrf-8fYXwMEHVkzSheoOJG27yvHTvYacW8JeYEdwNSuroPCTl6eJNGc-cts6WvNKFlJJk5fNWsW4nn1mRhEo6MFWgq2yGHzVEE; session-id-time=2082787201l; i18n-prefs=USD; csrf=-1054820603; session-token="gGfr02R3FJuycXzV110KzSRxq7GC4j/1o7KhHJ2XINYgwdeKtB+SPwGowmKd2u1Dn+8127yVhZVY8VlRmhYBzpVQ/nqfARAkCIOtutL2AOJyZN6/2EVyrKS0d0u2B7CxK4M1hOnWTqrM0z/FYHZdBBCYP4w32lKGae1iOrnrpymleoULWHgIwnG250uE/jgbXDggRcc3Q8lIMw+iA2oQYg=="; csm-hit=tb:XGKKNANNEEWRESRG9HZW+s-MBTZ4RBQ8RSBPYDFN2WA|1600618985320&t:1600618985321&adb:adblk_yes',
            'sec-fetch-site': 'none',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-dest': 'document',
            'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        }

    @classproperty
    def site(self) -> str:
        return 'https://www.amazon.com/gp/product/B08FC5L3RG?pf_rd_r=DXM1T6PXA6YV34513R3K&th=1'

    def _parse(self, resp: Response) -> bool:
        if "you're not a robot." in resp.text:
            raise Exception("amazon thinks you're a robot")
        return 'currently unavailable' not in resp.content.decode().lower()


class BestBuy(Site):
    @classproperty
    def display_site(cls) -> str:
        return 'https://www.bestbuy.com/site/sony-playstation-5-console/6426149.p?skuId=6426149'

    @classproperty
    def site(cls) -> str:
        return f'https://api.bestbuy.com/v1/products/6426149.json?apiKey={keyring.get_password("scraping", "bestbuy")}'

    def _parse(self, resp: Response) -> bool:
        return resp.json()['orderable'] != 'ComingSoon'


class Walmart(Site):
    def __init__(self):
        super().__init__()
        self.num_consec_for_success = 4

    @classproperty
    def site(cls) -> str:
        return 'https://www.walmart.com/ip/PlayStation5-Console/363472942'

    def _parse(self, resp: Response) -> bool:
        return '>Out of stock<' not in resp.text


# class GameStop(Site):
#     @classproperty
#     def site(cls) -> str:
#         return 'https://www.gamestop.com/video-games/playstation-5/consoles/products/playstation-5/11108140.html'
#
#     @classproperty
#     def _specific_headers(self):
#         return {
#             'pragma': 'no-cache',
#             'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
#             'accept-encoding': 'gzip, deflate, br',
#             'accept-language': 'en-US,en;q=0.9',
#             'cache-control': 'max-age=0',
#             'cookie': '__cfduid=d7296bdc794e9ab2fccdd745efcf211151600347545; cqcid=abNQ6oBvDN11Cq2jI8Mbz7PJ3t; dwanonymous_420142ceefb9f0c103b3815e84e9fcef=abNQ6oBvDN11Cq2jI8Mbz7PJ3t; lastVisitedCgid=ps5-consoles; __cq_dnt=0; dw_dnt=0; akaas_CartThrottling=2147483647~rv=1~id=ea097916eaba5ebb9baa80bfdbc577d3~rn=; ai_user=A2Ucz|2020-09-17T12:59:06.036Z; __cfruid=bafee3d609b1b450c1316179c8bc6c7e8c8ea340-1600347546; _caid=511a06b3-d67d-4ebd-b796-b266efcb049a; BVImplsfcc=9014_3_0; akavpau_Prioritization=1600348272~id=1d4ce68d18ecd3ebf7fe44d2bee597ff; dwac_a78eb5a11975e4c9cbc84f55ad=3ipIyzF0U-_ffSj2AAlg6CfhSu7AFbenKKg%3D|dw-only|||USD|false|US%2FCentral|true; sid=3ipIyzF0U-_ffSj2AAlg6CfhSu7AFbenKKg; dwsid=qpde7vASvNCW5ez3WTAzFVNcXMsBc1iYYTBbEzeXkZg2CxP92djuzDFwTGiXPwX1FvDxwJIJWPFGC4EoDDqPXw==; ak_bmsc=D2294E07A0AFABCAD3CC95F43362DF4517240147F36D000094D3665F70394056~plgi5DERKL5sPtwXEb8mUAnbGx6qwyO2Zcw5ahG1aSmg+IbXb4k5ZzRWWQo5qY86v3XR5lnAv+2QeE80MHm0tHUdqb2bj5RFihTPVcBn33hstXkA2yiSPt3HLsV0OEVJyCc30d55NhcduTu7Vcnd+COZ73UvnDgYlNDO9b00xq6LLA6UPaSQjbzXe/3yzRYjE2HmeCmOfgibW89CS2mwzLstGEv5tNF8c57q3QFdwKSvI=; bm_sz=630A2297D6CA1AFADA75694D53474516~YAAQRwEkF/iCeJ90AQAAMHyqqQlFmKw62FnZEw4gpvwgI4Ij0/d1GEdOQ5kx96pbeDvZnbTwyAklWZAn5LP8S4UdSdirUfibLQy1oyhgqD13ypidDZ64plIE8QKTiIRB4AjLZoGp0G67lIsdEtFNoMSmemVokQab7XFcXDYGMxKHQh34KbQtfCLRscUedFzd; _cavisit=174a9aa7e5b|; bm_mi=5E994E0F178765A1BC534690C0C9313E~qwBkCFzng5/90UGersUn5/Mq61fwmEiN0X/uiRX4rkC3f7V3gRTQH574sroyWVKAPx38j50o+eZvEb7cXU9yz5iQ4kdomEfsL/vDagJazSUon5XT/OPJOnjjl6kibktcQgPr8rEKpkmFyj1e+vv17Jmkg7c02dz3nV2BUj65cNDx+rSW7/3MW71t16Pu5kGKcJpWClWLTsw1lm9g/qu9TFq1WdFnCryS0uSQLByhbV/UXLLe+BMf3tbvYikupgEcqi+x1/WbIIt+LHyiut2c4YdqLY0hIRNEHI2u/w2q+ZhC7b9O+QofiD5LjOxXGgIjSUz2lmYvCtWON+2L7XeWMg==; ai_session=u6kYv|1600574363690.385|1600574363690.385; bm_sv=1C8EFFE96392877FB2444809CD9F3C7C~NXC+OnRBkB10CPA+xq2ojTBsD5ATvvkvitzHjPOZ0ej+YTqf7STPWQQ+AwopBbhD7D+U2fV0x7Qz4Rv6SMt8XLF1VuQVeJyiEvwOYJHc1iQWMWFwjYalan4NEtQFikCmlP2Act9ktEXOa+XMqspgRrgJi0fmrx1VaQuf22j0JOg=; _abck=C546B9A94217EA6274E693598BCF0DE0~-1~YAAQTwEkFxULen90AQAApdCsqQQb5ozlD56AVJcYV8SUPYeudLw4TjvWfmmpXWMrRPMkTD/4tHbiegppJAsU88shz8se2xGSXsG5C1fO/F0ZyRvnr50qx8iNt/2vZ/ab8axl/HzipE5xM9lIGCop26GGB1v0QMMotW+om78IZXOmpXx9UDoNenJoKYWUFtsBhV143XrXZ8oEduVpUZloUj0brcueJJ2fjpotuZWuz6mqsWUZqTS2uaQxHyY5uT1sZWPMxsho7kXoihxi+4lW2pQ+AaGVileiQAoyRlSicMi3UIK+czVVoK7mKF2+fXeNYMYhY/STt1jQb4CtAnmpRM8k6G41Dg==~-1~-1~-1',
#             # 'referer': 'https://www.gamestop.com/',
#             'sec-fetch-dest': 'document',
#             'sec-fetch-mode': 'navigate',
#             'sec-fetch-site': 'same-origin',
#             'sec-fetch-user': '?1',
#             'upgrade-insecure-requests': '1',
#             'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Mobile Safari/537.36',
#         }
#
#     def _parse(self, resp: Response) -> bool:
#         return '>Out of stock<' in resp.text


# class Test(Site):
#     @classproperty
#     def site(cls) -> str:
#         return 'https://example.com'
#
#     def _parse(self, resp: Response) -> bool:
#         return True
#
#     def run(self):
#         return True
#

pool: ThreadPoolExecutor = None


def query(*, debug=True):
    global pool
    if not pool:
        pool = ThreadPoolExecutor(len(registry))

    futures = [(inst, pool.submit(inst.run)) for inst in registry.values()]

    res = []
    for inst, f in futures:
        if f.exception():
            print(inst.site, f.exception())
            continue

        if f.result():
            if inst.mark_success() >= inst.num_consec_for_success:
                res.append(inst.display_site[8:])
        else:
            inst.mark_failure()
    if res:
        msg = '\n'.join(res) + '\nps5!'
        if not debug:
            sms(f'{keyring.get_password("phone", "number")}@msg.fi.google.com', msg)
        else:
            print(msg)


def test(cls):
    t = cls().get()
    with open('/tmp/wm', 'w') as f:
        f.write(t.text)
        return


def __main():
    while True:
        print('.', end='', flush=True)
        query(debug=False)
        time.sleep(30)
    # r = Pickle().read('resp')
    # query()


if __name__ == '__main__':
    __main()
