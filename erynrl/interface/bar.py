# Eryn Wells <eryn@erynwells.me>

from typing import List, Optional, Tuple

from . import color
from ..geometry import Point

class Bar:
    '''A bar that expresses a percentage.'''

    def __init__(self, *, position: Point, width: int, colors: Optional[List[Tuple[float, color.Color]]] = None):
        '''
        Instantiate a new Bar

        Arguments
        ---------
        position : Point
            The position within a console to render this bar
        width : int
            The length of the bar in tiles
        colors : List[Tuple[float, color.Color]]
            A list of two-tuples specifying a percentage and color to draw the bar. If the bar is less than or equal to
            the specified percentage, that color will be chosen. For example, if the bar is 45% filled, and this colors
            array is specified:

            ```
            [(0.25, RED), (0.5, ORANGE), (0.75, YELLOW), (1.0, GREEN)]
            ```

            The bar will be painted `ORANGE` because 45% is greater than 25% and less than 50%.
        '''
        self.position = position
        self.width = width
        self.colors = sorted(colors, key=lambda c: c[0]) if colors is not None else []

        self._percent_filled = 1.0

    @property
    def percent_filled(self) -> float:
        '''The percentage of this bar that should be filled, as a value between 0.0 and 1.0.'''
        return self._percent_filled

    @percent_filled.setter
    def percent_filled(self, value):
        self._percent_filled = min(1, max(0, value))

    def render_to_console(self, console):
        '''Draw this bar to the console'''
        # Draw the background first
        console.draw_rect(x=self.position.x, y=self.position.y, width=self.width, height=1, ch=1, bg=color.GREY12)

        percent_filled = self._percent_filled
        if percent_filled > 0:
            for color_spec in self.colors:
                if percent_filled <= color_spec[0]:
                    bar_color = color_spec[1]
                    break
            else:
                bar_color = color.GREY50

            filled_width = round(self._percent_filled * self.width)
            console.draw_rect(x=self.position.x, y=self.position.y, width=filled_width, height=1, ch=1, bg=bar_color)
