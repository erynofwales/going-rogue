# Eryn Wells <eryn@erynwells.me>

'''
Declares the Window class.
'''

from typing import Generic, Optional, TypeVar

from tcod import event as tev
from tcod.console import Console

from ...geometry import Point, Rect, Vector

WindowT = TypeVar('WindowT', bound='Window')


class Window:
    '''A user interface window. It can be framed and it can handle events.'''

    class EventHandler(tev.EventDispatch[bool], Generic[WindowT]):
        '''
        Handles events for a Window. Event dispatch methods return True if the event
        was handled and no further action is needed.
        '''

        def __init__(self, window: WindowT):
            super().__init__()
            self.window = window

        def mouse_point_for_event(self, event: tev.MouseState) -> Point:
            '''
            Return the mouse point in tiles for a window event. Raises a ValueError
            if the event is not a mouse event.
            '''
            if not isinstance(event, tev.MouseState):
                raise ValueError("Can't get mouse point for non-mouse event")

            return Point(event.tile.x, event.tile.y)

        def ev_keydown(self, event: tev.KeyDown) -> bool:
            return False

        def ev_keyup(self, event: tev.KeyUp) -> bool:
            return False

        def ev_mousemotion(self, event: tev.MouseMotion) -> bool:
            mouse_point = self.mouse_point_for_event(event)

            if mouse_point not in self.window.bounds:
                return False

            return False

    def __init__(self, bounds: Rect, *, framed: bool = True, event_handler: Optional['EventHandler'] = None):
        self.bounds = bounds
        '''The window's bounds in console coordinates'''

        self.is_framed = framed
        '''A `bool` indicating whether the window has a frame'''

        self.event_handler = event_handler or self.__class__.EventHandler(self)
        '''The window's event handler'''

    @property
    def drawable_bounds(self) -> Rect:
        '''
        A rectangle in console coordinates defining the area of the window that
        is drawable, inset by the window's frame if it has one.
        '''
        if self.is_framed:
            return self.bounds.inset_rect(1, 1, 1, 1)
        return self.bounds

    def convert_console_point_to_window(self, point: Point, *, use_drawable_bounds: bool = False) -> Optional[Point]:
        '''
        Converts a point in console coordinates to window coordinates. If the
        point is out of bounds of the window, return None.
        '''
        bounds = self.drawable_bounds if use_drawable_bounds else self.bounds
        if point in bounds:
            return point - Vector.from_point(bounds.origin)

        return None

    def draw(self, console: Console):
        '''Draw the window to the conole'''
        if self.is_framed:
            console.draw_frame(
                self.bounds.origin.x,
                self.bounds.origin.y,
                self.bounds.size.width,
                self.bounds.size.height)

        drawable_bounds = self.drawable_bounds
        console.draw_rect(drawable_bounds.min_x, drawable_bounds.min_y,
                          drawable_bounds.width, drawable_bounds.height,
                          ord(' '), (255, 255, 255), (0, 0, 0))
