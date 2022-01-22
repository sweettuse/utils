#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Needs freetype-py>=1.0

# For more info see:
# http://dbader.org/blog/monochrome-font-rendering-with-freetype-and-python

# The MIT License (MIT)
#
# Copyright (c) 2013 Daniel Bader (http://dbader.org)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
import string
from functools import lru_cache
from pathlib import Path
from typing import List, NamedTuple

import freetype
from PIL import Image
from lifxlan3 import Color, Colors, timer
from lifxlan3.routines.tile.core import set_cm
from lifxlan3.routines.tile.tile_utils import ColorMatrix, RC
from more_itertools import collapse
from utils.assets_path import ASSETS_PATH

from utils.core import chunk

ON = '\u2588'
ON = '#'
OFF = ' '


class Bitmap:
    """
    A 2D bitmap image represented as a list of byte values. Each byte indicates the state
    of a single pixel in the bitmap. A value of 0 indicates that the pixel is `off`
    and any other value indicates that it is `on`.
    """

    def __init__(self, width, height, pixels=None):
        self.width = width
        self.height = height
        self.pixels = pixels or bytearray(width * height)

    @property
    def bits(self) -> List[List[int]]:
        return list(chunk(self.pixels, self.width))

    def __repr__(self):
        """Return a string representation of the bitmap's pixels."""
        rows = ''
        for y in range(self.height):
            for x in range(self.width):
                rows += ON if self.pixels[y * self.width + x] else OFF
            rows += '\n'
        return rows

    def add_border(self, height_pct=10.) -> 'Bitmap':
        n_pixels = int(self.height * height_pct // 100) + 1
        bits = self.bits
        width = self.width + 2 * n_pixels
        height = self.height + 2 * n_pixels
        lr_zeros = n_pixels * [0]
        for r in bits:
            r[:0] = lr_zeros
            r.extend(lr_zeros)
        extra_zero_rows = n_pixels * [width * [0]]
        bits[:0] = extra_zero_rows
        bits.extend(extra_zero_rows)
        return Bitmap(width, height, bytearray(collapse(bits)))

    def bitblt(self, src, x, y):
        """Copy all pixels from `src` into this bitmap"""
        srcpixel = 0
        dstpixel = y * self.width + x
        row_offset = self.width - src.width

        for sy in range(src.height):
            for sx in range(src.width):
                # Perform an OR operation on the destination pixel and the source pixel
                # because glyph bitmaps may overlap if character kerning is applied, e.g.
                # in the string "AVA", the "A" and "V" glyphs must be rendered with
                # overlapping bounding boxes.
                self.pixels[dstpixel] = self.pixels[dstpixel] or src.pixels[srcpixel]
                srcpixel += 1
                dstpixel += 1
            dstpixel += row_offset


class Glyph:
    def __init__(self, pixels, width, height, top, advance_width):
        self.bitmap = Bitmap(width, height, pixels)

        # The glyph bitmap's top-side bearing, i.e. the vertical distance from the
        # baseline to the bitmap's top-most scanline.
        self.top = top

        # Ascent and descent determine how many pixels the glyph extends
        # above or below the baseline.
        self.descent = max(0, self.height - self.top)
        self.ascent = max(0, max(self.top, self.height) - self.descent)

        # The advance width determines where to place the next character horizontally,
        # that is, how many pixels we move to the right to draw the next glyph.
        self.advance_width = advance_width

    @property
    def width(self):
        return self.bitmap.width

    @property
    def height(self):
        return self.bitmap.height

    @staticmethod
    def from_glyphslot(slot):
        """Construct and return a Glyph object from a FreeType GlyphSlot."""
        pixels = Glyph.unpack_mono_bitmap(slot.bitmap)
        width, height = slot.bitmap.width, slot.bitmap.rows
        top = slot.bitmap_top

        # The advance width is given in FreeType's 26.6 fixed point format,
        # which means that the pixel values are multiples of 64.
        advance_width = slot.advance.x // 64

        return Glyph(pixels, width, height, top, advance_width)

    @staticmethod
    def unpack_mono_bitmap(bitmap):
        """
        Unpack a freetype FT_LOAD_TARGET_MONO glyph bitmap into a bytearray where each
        pixel is represented by a single byte.
        """
        # Allocate a bytearray of sufficient size to hold the glyph bitmap.
        data = bytearray(bitmap.rows * bitmap.width)

        # Iterate over every byte in the glyph bitmap. Note that we're not
        # iterating over every pixel in the resulting unpacked bitmap --
        # we're iterating over the packed bytes in the input bitmap.
        for y in range(bitmap.rows):
            for byte_index in range(bitmap.pitch):

                # Read the byte that contains the packed pixel data.
                byte_value = bitmap.buffer[y * bitmap.pitch + byte_index]

                # We've processed this many bits (=pixels) so far. This determines
                # where we'll read the next batch of pixels from.
                num_bits_done = byte_index * 8

                # Pre-compute where to write the pixels that we're going
                # to unpack from the current byte in the glyph bitmap.
                rowstart = y * bitmap.width + byte_index * 8

                # Iterate over every bit (=pixel) that's still a part of the
                # output bitmap. Sometimes we're only unpacking a fraction of a byte
                # because glyphs may not always fit on a byte boundary. So we make sure
                # to stop if we unpack past the current row of pixels.
                for bit_index in range(min(8, bitmap.width - num_bits_done)):
                    # Unpack the next pixel from the current glyph byte.
                    bit = byte_value & (1 << (7 - bit_index))

                    # Write the pixel to the output bytearray. We ensure that `off`
                    # pixels have a value of 0 and `on` pixels have a value of 1.
                    data[rowstart + bit_index] = 1 if bit else 0

        return data


class TextDims(NamedTuple):
    width: int
    height: int
    baseline: int


class Font:
    def __init__(self, filename, size):
        self.face = freetype.Face(filename)
        self.face.set_pixel_sizes(0, size)

    @lru_cache(128)
    def glyph_for_character(self, char):
        # Let FreeType load the glyph for the given character and tell it to render
        # a monochromatic bitmap representation.
        self.face.load_char(char, freetype.FT_LOAD_RENDER | freetype.FT_LOAD_TARGET_MONO)
        return Glyph.from_glyphslot(self.face.glyph)

    def render_character(self, char):
        glyph = self.glyph_for_character(char)
        return glyph.bitmap

    def kerning_offset(self, previous_char, char):
        """
        Return the horizontal kerning offset in pixels when rendering `char`
        after `previous_char`.
        Use the resulting offset to adjust the glyph's drawing position to
        reduces extra diagonal whitespace, for example in the string "AV" the
        bitmaps for "A" and "V" may overlap slightly with some fonts. In this
        case the glyph for "V" has a negative horizontal kerning offset as it is
        moved slightly towards the "A".
        """
        kerning = self.face.get_kerning(previous_char, char)

        # The kerning offset is given in FreeType's 26.6 fixed point format,
        # which means that the pixel values are multiples of 64.
        return kerning.x // 64

    def text_dimensions(self, text) -> TextDims:
        """Return (width, height, baseline) of `text` rendered in the current font."""
        width = 0
        max_ascent = 0
        max_descent = 0
        previous_char = None

        # For each character in the text string we get the glyph
        # and update the overall dimensions of the resulting bitmap.
        for char in text:
            glyph = self.glyph_for_character(char)
            max_ascent = max(max_ascent, glyph.ascent)
            max_descent = max(max_descent, glyph.descent)
            kerning_x = self.kerning_offset(previous_char, char)

            # With kerning, the advance width may be less than the width of the glyph's bitmap.
            # Make sure we compute the total width so that all of the glyph's pixels
            # fit into the returned dimensions.
            width += max(glyph.advance_width + kerning_x, glyph.width + kerning_x)

            previous_char = char

        height = max_ascent + max_descent
        return TextDims(width, height, max_descent)

    def render_text(self, text, width=None, height=None, baseline=None) -> Bitmap:
        """
        Render the given `text` into a Bitmap and return it.
        If `width`, `height`, and `baseline` are not specified they are computed using
        the `text_dimensions' method.
        """
        if None in (width, height, baseline):
            width, height, baseline = self.text_dimensions(text)

        x = 0
        previous_char = None
        outbuffer = Bitmap(width, height)

        for char in text:
            glyph = self.glyph_for_character(char)

            # Take kerning information into account before we render the
            # glyph to the output bitmap.
            x += self.kerning_offset(previous_char, char)

            # The vertical drawing position should place the glyph
            # on the baseline as intended.
            y = height - glyph.ascent - baseline

            outbuffer.bitblt(glyph.bitmap, x, y)

            x += glyph.advance_width
            previous_char = char

        return outbuffer

    @timer
    def to_image(self, text: str, color: Color = Colors.YELLOW) -> Image.Image:
        bm = self.render_text(text).add_border(10)
        color = color.rgb[:3]
        colors = bytearray(collapse(color if px else (0, 0, 0) for px in bm.pixels))
        return Image.frombytes('RGB', (bm.width, bm.height), bytes(colors))

    def to_color_matrix(self, text: str, color: Color = Colors.YELLOW, height=16) -> ColorMatrix:
        im = self.to_image(text, color)
        width = int(im.width * height / im.height)
        im = im.resize((width, height), Image.ANTIALIAS)
        return ColorMatrix.from_image(im.resize((width, height), Image.ANTIALIAS))


def load_font(font_name='Courier New.ttf', size=13):
    font_dir = ASSETS_PATH / 'fonts'
    return Font(f'{font_dir}/{font_name}', size)


def display_dimensions(font_name='Courier New.ttf', r=range(13, 50)):
    """print out dimensions for a particular font in a particular range"""
    print(font_name)
    for size in r:
        fnt = load_font(font_name, size)
        print(size, fnt.text_dimensions(string.printable))
    print(font_name)


def _play():
    # Single characters
    fnt = load_font('Courier New.ttf', 13)
    ch = fnt.render_character('e')
    # print(ch.width, ch.height)
    # print(ch.bits)
    # print(repr(ch))

    # ColorMatrix
    fnt = load_font('Courier New.ttf', 16)
    fnt = load_font('AmericanTypewriter.ttc', 100)
    fnt = load_font('Courier New.ttf', 100)
    cm = fnt.to_color_matrix('Niiiiiiiiice', height=8)
    # from lifxlan3.routines.tile.core import set_cm, translate, Dir
    # set_cm(cm, size=RC(8, 256), in_terminal=True, verbose=False)
    # return
    im = fnt.to_image('hello==' * 10)
    # return

    from lifxlan3.routines.tile.core import set_cm, translate, Dir
    fnt.to_image('hello').show()
    return
    translate(cm, in_terminal=True, n_iterations=2, split=False, dir=Dir.left, sleep_secs=.3, pixels_per_step=4)
    # set_cm(cm, size=RC(8, 256), in_terminal=True, verbose=False)
    return
    # Multiple characters
    txt = fnt.render_text('hello')
    print(repr(txt))

    # Kerning
    print(repr(fnt.render_text('AV Wa')))

    # Choosing the baseline correctly
    print(repr(fnt.render_text('hello, world.')))


if __name__ == '__main__':
    # Be sure to place 'helvetica.ttf' (or any other ttf / otf font file) in the working directory.
    # fnt = Font('helvetica.ttf', 24)
    _play()
