from io import BytesIO

from PIL import Image
import requests

__author__ = 'acushner'


def _calc_resize(im, mult):
    return int(im.size[0] * mult), int(im.size[1] * mult)


def _resize_gif(path, save_as=None, resize_mult=None):
    """
    Resizes the GIF to a given length:

    Args:
        path: the path to the GIF file
        save_as (optional): Path of the resized gif. If not set, the original gif will be overwritten.
        resize_to (optional): new size of the gif. Format: (int, int). If not set, the original GIF will be resized to
                              half of its size.
    """
    all_frames = extract_and_resize_frames(path, resize_mult)

    if not save_as:
        save_as = path

    if len(all_frames) == 1:
        print("Warning: only 1 frame found")
        all_frames[0].save(save_as, format='gif', optimize=True)
    else:
        all_frames[0].save(save_as, format='gif', optimize=True, save_all=True, append_images=all_frames[1::2],
                           loop=1000)


def analyze_image(path):
    """
    Pre-process pass over the image to determine the mode (full or additive).
    Necessary as assessing single frames isn't reliable. Need to know the mode
    before processing all frames.
    """
    im = Image.open(path)
    results = {
        'size': im.size,
        'mode': 'full',
    }
    try:
        while True:
            if im.tile:
                tile = im.tile[0]
                update_region = tile[1]
                update_region_dimensions = update_region[2:]
                if update_region_dimensions != im.size:
                    results['mode'] = 'partial'
                    break
            im.seek(im.tell() + 1)
    except EOFError:
        pass
    return results


def extract_and_resize_frames(path, resize_mult=None):
    """
    Iterate the GIF, extracting each frame and resizing them

    Returns:
        An array of all frames
    """
    mode = analyze_image(path)['mode']

    im = Image.open(path)

    if not resize_mult:
        resize_mult = .5
    resize_to = _calc_resize(im, resize_mult)

    i = 0
    p = im.getpalette()
    last_frame = im.convert('RGBA')

    all_frames = []

    try:
        while True:
            # If the GIF uses local colour tables, each frame will have its own palette.
            # If not, we need to apply the global palette to the new frame.
            if not im.getpalette():
                im.putpalette(p)

            new_frame = Image.new('RGBA', im.size)

            # Is this file a "partial"-mode GIF where frames update a region of a different size to the entire image?
            # If so, we need to construct the new frame by pasting it on top of the preceding frames.
            if mode == 'partial':
                new_frame.paste(last_frame)

            new_frame.paste(im, (0, 0), im.convert('RGBA'))

            all_frames.append(new_frame.resize(resize_to, Image.NEAREST))

            i += 1
            last_frame = new_frame
            im.seek(im.tell() + 1)
    except EOFError:
        pass

    return all_frames


def resize_image(data: BytesIO, mult: int) -> BytesIO:
    im = Image.open(data)
    res = BytesIO()
    im = im.resize(_calc_resize(im, mult)).convert('RGB')
    im.save(res, format='jpeg', optimize=True)
    res.seek(0)
    return res


def resize_gif(data: BytesIO, mult: int) -> BytesIO:
    res = BytesIO()
    _resize_gif(data, res, mult)
    res.seek(0)
    return res


def __main():
    # t = requests.get('https://assets.bwbx.io/images/users/iqjWHBFdfxIU/i6NtsdFrY8KU/v0/-1x-1.png')
    t = requests.get('https://emoji.slack-edge.com/T03UGBWK0/lee/fdf586306d4275ab.png')
    # t = requests.get('https://emoji.slack-edge.com/T03UGBWK0/cushparrot/c2bdb7c9afff077e.gif')

    res = resize_image(BytesIO(t.content), 10)
    with open('/tmp/lee.jpg', 'wb') as f:
        f.write(res.read())
    breakpoint()
    pass


if __name__ == '__main__':
    __main()
