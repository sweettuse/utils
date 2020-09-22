import json
from typing import Optional

from fastapi import FastAPI
import requests

__author__ = 'acushner'

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Optional[str] = None):
    """holy shit this is pretty cool"""
    return {"item_id": item_id, "q": q}


def __main():
    pass


if __name__ == '__main__':
    __main()
