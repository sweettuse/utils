from lifxlan3 import LifxLAN, Device, Color as LColor
from rich import print
from rich.color import Color

from utils.core import take


def _from_hsv(cls, color: LColor):
    cls: Color
    return cls.from_rgb(*take(3, color.rgb))


Color.from_hsv = classmethod(_from_hsv)

t = LifxLAN()['guest']
l = t[0]

vals = {attr: val for attr in dir(l) if
        not attr.startswith('_') and not callable(val := getattr(l, attr))}
print(vals)


class LightDisp:
    def __init__(self, device: Device):
        self._device = device

    def __getattr__(self, item):
        return getattr(self._device, item)

    def __rich_repr__(self):
        c = Color.from_hsv(self.color)
        yield 'name', self.label
        yield 'color', c.name


print(LightDisp(l))
