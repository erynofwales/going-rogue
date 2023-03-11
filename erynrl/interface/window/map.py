# Eryn Wells <eryn@erynwells.me>

'''
Declares the MapWindow class.
'''

from typing import List

import numpy as np
import tcod.event as tev
from tcod.console import Console

from . import Window
from ... import log
from ...geometry import Point, Rect, Vector
from ...map import Map
from ...object import Entity, Hero


class MapWindow(Window):
    '''A Window that displays a game map'''

    class EventHandler(Window.EventHandler['MapWindow']):
        '''An event handler for the MapWindow.'''

        def ev_mousemotion(self, event: tev.MouseMotion) -> bool:
            mouse_point = self.mouse_point_for_event(event)

            converted_point = self.window.convert_console_point_to_window(mouse_point, use_drawable_bounds=True)
            if not converted_point:
                return False

            hero = self.window.hero
            if not hero:
                return False

            map_point = self.window.convert_console_point_to_map(mouse_point)
            log.UI.info('Mouse moved; finding path from hero to %s', map_point)

            map_ = self.window.map
            path = map_.find_walkable_path_from_point_to_point(hero.position, map_point)
            map_.highlight_points(path)

            return False

        def ev_mousebuttondown(self, event: tev.MouseButtonDown) -> bool:
            mouse_point = self.mouse_point_for_event(event)

            converted_point = self.window.convert_console_point_to_window(mouse_point, use_drawable_bounds=True)
            if not converted_point:
                return False

            map_point = self.window.convert_console_point_to_map(mouse_point)
            log.UI.info('Mouse button down at %s', map_point)

            return False

    def __init__(self, bounds: Rect, map: Map, hero: Hero, **kwargs):
        super().__init__(bounds, event_handler=self.__class__.EventHandler(self), **kwargs)
        self.map = map
        '''The game map'''

        self.visible_map_bounds = map.bounds
        '''A rectangle in map coordinates defining the visible area of the map in the window'''

        self.hero = hero
        '''The hero entity'''

        self.entities: List[Entity] = []
        '''A list of all game entities to render on the map'''

        self._draw_bounds = self.drawable_bounds
        '''
        A rectangle in console coordinates where the map will actually be drawn.
        This area should always be entirely contained within the window's
        drawable bounds.
        '''

    def convert_console_point_to_map(self, point: Point) -> Point:
        '''
        Convert a point in console coordinates to a point relative to the map's
        origin point.
        '''
        return point - Vector.from_point(self._draw_bounds.origin) + Vector.from_point(self.visible_map_bounds.origin)

    def _update_visible_map_bounds(self) -> Rect:
        '''
        Figure out what portion of the map is visible. This method attempts to
        keep the hero centered in the map viewport, while not overscrolling the
        map in either direction.
        '''
        bounds = self.drawable_bounds
        map_bounds = self.map.bounds

        viewport_is_wider_than_map = bounds.width > map_bounds.width
        viewport_is_taller_than_map = bounds.height > map_bounds.height

        if viewport_is_wider_than_map and viewport_is_taller_than_map:
            # The whole map fits within the window's drawable bounds
            return map_bounds

        # Attempt to keep the player centered in the viewport.
        hero_point = self.hero.position

        if viewport_is_wider_than_map:
            x = 0
            width = map_bounds.width
        else:
            half_width = bounds.width // 2
            x = min(max(0, hero_point.x - half_width), map_bounds.end_x - bounds.width)
            width = bounds.width

        if viewport_is_taller_than_map:
            y = 0
            height = map_bounds.height
        else:
            half_height = bounds.height // 2
            y = min(max(0, hero_point.y - half_height), map_bounds.end_y - bounds.height)
            height = bounds.height

        return Rect.from_raw_values(x, y, width, height)

    def _update_draw_bounds(self):
        '''
        The area where the map should actually be drawn, accounting for the size
        of the viewport (`drawable_bounds`) and the size of the map (`self.map.bounds`).
        '''
        visible_map_bounds = self.visible_map_bounds
        drawable_bounds = self.drawable_bounds

        viewport_is_wider_than_map = drawable_bounds.width >= visible_map_bounds.width
        viewport_is_taller_than_map = drawable_bounds.height >= visible_map_bounds.height

        if viewport_is_wider_than_map:
            # Center the map horizontally in the viewport
            x = drawable_bounds.min_x + (drawable_bounds.width - visible_map_bounds.width) // 2
            width = visible_map_bounds.width
        else:
            x = drawable_bounds.min_x
            width = drawable_bounds.width

        if viewport_is_taller_than_map:
            # Center the map vertically in the viewport
            y = drawable_bounds.min_y + (drawable_bounds.height - visible_map_bounds.height) // 2
            height = visible_map_bounds.height
        else:
            y = drawable_bounds.min_y
            height = drawable_bounds.height

        draw_bounds = Rect.from_raw_values(x, y, width, height)
        assert draw_bounds in self.drawable_bounds

        return draw_bounds

    def draw(self, console: Console):
        super().draw(console)

        self.visible_map_bounds = self._update_visible_map_bounds()
        self._draw_bounds = self._update_draw_bounds()
        self._draw_map(console)
        self._draw_entities(console)

    def _draw_map(self, console: Console):
        drawable_map_bounds = self.visible_map_bounds

        map_slice = np.s_[
            drawable_map_bounds.min_x: drawable_map_bounds.max_x + 1,
            drawable_map_bounds.min_y: drawable_map_bounds.max_y + 1]

        console_draw_bounds = self._draw_bounds
        console_slice = np.s_[
            console_draw_bounds.min_x: console_draw_bounds.max_x + 1,
            console_draw_bounds.min_y: console_draw_bounds.max_y + 1]

        console.tiles_rgb[console_slice] = self.map.composited_tiles[map_slice]

    def _draw_entities(self, console: Console):
        visible_map_bounds = self.visible_map_bounds
        map_bounds_vector = Vector.from_point(self.visible_map_bounds.origin)
        draw_bounds_vector = Vector.from_point(self._draw_bounds.origin)

        for ent in self.entities:
            entity_position = ent.position

            # Only draw entities that are within the visible map bounds
            if entity_position not in visible_map_bounds:
                continue

            # Only draw entities that are in the field of view
            if not self.map.point_is_visible(entity_position):
                continue

            # Entity positions are relative to the (0, 0) point of the Map. In
            # order to render them in the correct position in the console, we
            # need to transform them into viewport-relative coordinates.
            map_tile_at_entity_position = self.map.composited_tiles[entity_position.numpy_index]

            position = ent.position - map_bounds_vector + draw_bounds_vector

            console.print(
                x=position.x,
                y=position.y,
                string=ent.symbol,
                fg=ent.foreground,
                bg=tuple(map_tile_at_entity_position['bg'][:3]))
