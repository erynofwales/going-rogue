# Eryn Wells <eryn@erynwells.me>

from typing import List, Optional

import numpy as np
from tcod import event as tev
from tcod.console import Console

from .. import log
from ..geometry import Point, Rect, Size, Vector
from ..map import Map
from ..object import Entity, Hero


class Window:
    '''A user interface window. It can be framed and it can handle events.'''

    class EventHandler(tev.EventDispatch[bool]):
        '''
        Handles events for a Window. Event dispatch methods return True if the event
        was handled and no further action is needed.
        '''

        def __init__(self, window: 'Window'):
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
        self.is_framed = framed
        self.event_handler = event_handler or self.__class__.EventHandler(self)

    @property
    def drawable_bounds(self) -> Rect:
        '''
        The bounds of the window that is drawable, inset by its frame if
        `is_framed` is `True`.
        '''
        if self.is_framed:
            return self.bounds.inset_rect(1, 1, 1, 1)
        return self.bounds

    def convert_console_point(self, point: Point) -> Optional[Point]:
        '''
        Converts a point in console coordinates to window-relative coordinates.
        If the point is out of bounds of the window, return None.
        '''
        converted_point = point - Vector.from_point(self.bounds.origin)
        return converted_point if converted_point in self.bounds else None

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


class MapWindow(Window):
    '''A Window that displays a game map'''

    class EventHandler(Window.EventHandler):
        '''An event handler for the MapWindow.'''

        def ev_mousemotion(self, event: tev.MouseMotion) -> bool:
            mouse_point = self.window.convert_console_point(self.mouse_point_for_event(event))
            if not mouse_point:
                return False

            # TODO: Convert window point to map point
            # TODO: Perform a path finding operation from the hero to the mouse point
            # TODO: Highlight those points on the map

            return False

    # pylint: disable=redefined-builtin
    def __init__(self, bounds: Rect, map: Map, **kwargs):
        super().__init__(bounds, **kwargs)
        self.map = map

        self.drawable_map_bounds = map.bounds
        self.entities: List[Entity] = []

        self._draw_bounds = self.drawable_bounds

    def update_drawable_map_bounds(self, hero: Hero):
        '''
        Figure out what portion of the map is drawable and update
        `self.drawable_map_bounds`. This method attempts to keep the hero
        centered in the map viewport, while not overscrolling the map in either
        direction.
        '''
        bounds = self.drawable_bounds
        map_bounds = self.map.bounds

        viewport_is_wider_than_map = bounds.width > map_bounds.width
        viewport_is_taller_than_map = bounds.height > map_bounds.height

        if viewport_is_wider_than_map and viewport_is_taller_than_map:
            # The whole map fits within the window's drawable bounds
            self.drawable_map_bounds = map_bounds
            return

        # Attempt to keep the player centered in the viewport.
        hero_point = hero.position

        if viewport_is_wider_than_map:
            x = 0
        else:
            x = min(max(0, hero_point.x - bounds.mid_x), map_bounds.max_x - bounds.width)

        if viewport_is_taller_than_map:
            y = 0
        else:
            y = min(max(0, hero_point.y - bounds.mid_y), map_bounds.max_y - bounds.height)

        origin = Point(x, y)
        size = Size(min(bounds.width, map_bounds.width), min(bounds.height, map_bounds.height))

        self.drawable_map_bounds = Rect(origin, size)

    def _update_draw_bounds(self):
        '''
        The area where the map should actually be drawn, accounting for the size
        of the viewport (`drawable_bounds`)and the size of the map (`self.map.bounds`).
        '''
        drawable_map_bounds = self.drawable_map_bounds
        drawable_bounds = self.drawable_bounds

        viewport_is_wider_than_map = drawable_bounds.width >= drawable_map_bounds.width
        viewport_is_taller_than_map = drawable_bounds.height >= drawable_map_bounds.height

        if viewport_is_wider_than_map:
            # Center the map horizontally in the viewport
            origin_x = drawable_bounds.min_x + (drawable_bounds.width - drawable_map_bounds.width) // 2
            width = drawable_map_bounds.width
        else:
            origin_x = drawable_bounds.min_x
            width = drawable_bounds.width

        if viewport_is_taller_than_map:
            # Center the map vertically in the viewport
            origin_y = drawable_bounds.min_y + (drawable_bounds.height - drawable_map_bounds.height) // 2
            height = drawable_map_bounds.height
        else:
            origin_y = drawable_bounds.min_y
            height = drawable_bounds.height

        self._draw_bounds = Rect(Point(origin_x, origin_y), Size(width, height))

    def draw(self, console: Console):
        super().draw(console)
        self._update_draw_bounds()
        self._draw_map(console)
        self._draw_entities(console)

    def _draw_map(self, console: Console):
        drawable_map_bounds = self.drawable_map_bounds
        drawable_bounds = self.drawable_bounds

        log.UI.info('Drawing map')

        map_slice = np.s_[
            drawable_map_bounds.min_x: drawable_map_bounds.max_x + 1,
            drawable_map_bounds.min_y: drawable_map_bounds.max_y + 1]

        console_draw_bounds = self._draw_bounds
        console_slice = np.s_[
            console_draw_bounds.min_x: console_draw_bounds.max_x + 1,
            console_draw_bounds.min_y: console_draw_bounds.max_y + 1]

        log.UI.debug('Map bounds=%s, slice=%s', drawable_map_bounds, map_slice)
        log.UI.debug('Console bounds=%s, slice=%s', drawable_bounds, console_slice)

        console.tiles_rgb[console_slice] = self.map.composited_tiles[map_slice]

        log.UI.info('Done drawing map')

    def _draw_entities(self, console):
        map_bounds_vector = Vector.from_point(self.drawable_map_bounds.origin)
        draw_bounds_vector = Vector.from_point(self._draw_bounds.origin)

        log.UI.info('Drawing entities')

        for ent in self.entities:
            # Only draw entities that are in the field of view
            if not self.map.point_is_visible(ent.position):
                continue

            # Entity positions are relative to the (0, 0) point of the Map. In
            # order to render them in the correct position in the console, we
            # need to transform them into viewport-relative coordinates.
            entity_position = ent.position
            map_tile_at_entity_position = self.map.composited_tiles[entity_position.numpy_index]

            position = ent.position - map_bounds_vector + draw_bounds_vector

            if isinstance(ent, Hero):
                log.UI.debug('Hero position: map=%s, window=%s', entity_position, position)

            console.print(
                x=position.x,
                y=position.y,
                string=ent.symbol,
                fg=ent.foreground,
                bg=tuple(map_tile_at_entity_position['bg'][:3]))

        log.UI.info('Done drawing entities')
