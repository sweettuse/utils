import asyncio
import os
from concurrent.futures.thread import ThreadPoolExecutor
from typing import Callable
from urllib.parse import urlparse, unquote
from pathlib import Path


from bs4 import BeautifulSoup
import requests

__author__ = 'acushner'

_pool = ThreadPoolExecutor(8)


async def get(url):
    return await asyncio.get_event_loop().run_in_executor(_pool, requests.get, url)


async def parse_content(resp, predicate: Callable[[str], bool] = None):
    predicate = predicate or (lambda _: True)
    soup = BeautifulSoup(resp.text, features='html.parser')
    links = (link.get('href') for link in soup.find_all('a'))
    return [l for l in links if predicate(l)]


async def download(url, outdir):
    res = await get(url)
    p = urlparse(url)
    n = f'{outdir}/{unquote(unquote(Path(p.path).name))}'
    print('downloading:', n)
    with open(n, 'wb') as f:
        f.write(res.content)


async def run(url, outdir, predicate=None):
    links = await parse_content(await get(url), predicate)
    print(links)
    full_links = {get_name(url, link) for link in links}
    coros = (download(url, outdir) for url in full_links)
    await asyncio.gather(*coros)
    # await download(get_name(url, next(full_links)), outdir)


def get_name(url, link):
    if not link.startswith('/'):
        return link

    p = urlparse(url)
    return f'{p.scheme}://{p.netloc}{link}'


def __main():
    # url = 'https://themushroomkingdom.net/media/smb/wav'
    url = 'https://downloads.khinsider.com/game-soundtracks/album/castlevania-iii-dracula-s-curse'
    # outdir = f'/tmp/{Path(url).name}'
    outdir = f'/tmp/castlevania3'
    os.system(f'mkdir -p {outdir}')
    res = asyncio.run(run(url, outdir, lambda l: l and l.endswith('.mp3')))
    pass


if __name__ == '__main__':
    __main()
