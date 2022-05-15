# Eryn Wells <eryn@erynwells.me>

from . import color
from ..geometry import Point

class Bar:
    def __init__(self, *, position: Point, width: int):
        self.position = position
        self.width = width

        self._percent_filled = 1.0

    @property
    def percent_filled(self) -> float:
        '''The percentage of this bar that should be filled, as a value between 0.0 and 1.0.'''
        return self._percent_filled

    @percent_filled.setter
    def percent_filled(self, value):
        self._percent_filled = min(1, max(0, value))

    def render_to_console(self, console):
        console.draw_rect(x=self.position.x, y=self.position.y, width=self.width, height=1, ch=1, bg=color.GREY10)

        if self._percent_filled > 0:
            filled_width = round(self._percent_filled * self.width)
            console.draw_rect(x=self.position.x, y=self.position.y, width=filled_width, height=1, ch=1, bg=color.GREY50)
