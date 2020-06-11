__author__ = 'acushner'

from utils.font_to_bitmap import load_font, Font
from utils.slack_app import UserType, async_run
from utils.slack_app.app import SlackAPI


def text_to_emoji(s: str, emoji='blob-turtle', font: Font = load_font()) -> str:
    num_spaces = 6
    res = font.render_text(s)
    emoji = f':{emoji.replace(":", "")}:'
    res = [[emoji if c else num_spaces * ' ' for c in row] for row in res.bits]
    res[0][0] = '.' + (num_spaces - 1) * ' '
    res = '\n'.join(map(''.join, res))
    with open('/tmp/etest', 'w') as f:
        f.write(res)
    return res


async def run(sa: SlackAPI, channel: str, text: str):
    await sa.client.chat_postMessage(channel=channel, text=text)


def __main():
    sa = SlackAPI.from_user_type(UserType.bot)
    s = text_to_emoji('cp!', 'copilot')
    async_run(run(sa, 'oasis', s))


if __name__ == '__main__':
    __main()
