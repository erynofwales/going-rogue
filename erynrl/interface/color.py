# Eryn Wells <eryn@erynwells.me>
# pylint: disable=too-few-public-methods

'''
A bunch of colors.
'''

from typing import Iterator, Tuple

Color = Tuple[int, int, int]

# Grayscale
BLACK = (0x00, 0x00, 0x00)
GREY12 = (0x20, 0x20, 0x20)
GREY25 = (0x40, 0x40, 0x40)
GREY50 = (0x80, 0x80, 0x80)
GREY75 = (0xC0, 0xC0, 0xC0)
WHITE = (0xFF, 0xFF, 0xFF)

# Primaries
BLUE = (0x00, 0x00, 0xFF)
CYAN = (0x00, 0xFF, 0xFF)
GREEN = (0x00, 0xFF, 0x00)
MAGENTA = (0xFF, 0x00, 0xFF)
RED = (0xFF, 0x00, 0x00)
YELLOW = (0xFF, 0xFF, 0x00)
ORANGE = (0xFF, 0x77, 0x00)

# Semantic
class HealthBar:
    '''Semantic colors for the health bar'''
    FULL = GREEN
    GOOD = GREEN
    OKAY = YELLOW
    LOW = ORANGE
    CRITICAL = RED

    @staticmethod
    def bar_colors() -> Iterator[Tuple[float, Color]]:
        '''Return an iterator of colors that a Bar class can use'''
        yield (0.1, HealthBar.CRITICAL)
        yield (0.25, HealthBar.LOW)
        yield (0.75, HealthBar.OKAY)
        yield (0.9, HealthBar.GOOD)
        yield (1.0, HealthBar.FULL)
