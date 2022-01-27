from typing import Literal

import typer
from utils.lights.font_to_bitmap import Fonts
from utils.rich_utils.fun import *

app = typer.Typer()

font_names = Literal['typewriter', 'comic_sans', 'courier_new', 'futura', 'jet_brains_mono', 'menlo', 'papyrus']


@app.command()
def emojify(text: str,
            emoji: str = 'saxophone',
            font: str = 'courier_new',
            size: int = 11,
            invert: bool = False
            ):
    print(*emoji_text(text, emoji=emoji, font=Fonts[font], size=size, flip=invert))


if __name__ == '__main__':
    app()
