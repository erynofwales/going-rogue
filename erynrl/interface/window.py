# Eryn Wells <eryn@erynwells.me>

from tcod.console import Console

from ..geometry import Rect


class Window:
    def __init__(self, bounds: Rect, *, framed: bool = True):
        self.bounds = bounds
        self.is_framed = framed

    @property
    def drawable_area(self) -> Rect:
        if self.is_framed:
            return self.bounds.inset_rect(1, 1, 1, 1)
        return self.bounds

    def draw(self, console: Console):
        if self.is_framed:
            console.draw_frame(
                self.bounds.origin.x,
                self.bounds.origin.y,
                self.bounds.size.width,
                self.bounds.size.height)
