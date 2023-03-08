# Eryn Wells <eryn@erynwells.me>

from typing import List, Optional

import numpy as np
import tcod.event as tev
from tcod.console import Console

from . import Window
from ... import log
from ...geometry import Point, Rect, Size, Vector
from ...map import Map
from ...object import Entity, Hero


class MapWindow(Window):
    '''A Window that displays a game map'''

    class EventHandler(Window.EventHandler['MapWindow']):
        '''An event handler for the MapWindow.'''

        def ev_mousemotion(self, event: tev.MouseMotion) -> bool:
            mouse_point = self.window.convert_console_point(self.mouse_point_for_event(event))
            if not mouse_point:
                return False

            log.UI.info('Mouse point in window %s', mouse_point)

            hero = self.window.hero
            if not hero:
                return False

            map_point = self.window.convert_window_point_to_map(mouse_point)
            log.UI.info('Mouse point in map %s', map_point)

            map_ = self.window.map
            path = map_.find_walkable_path_from_point_to_point(hero.position, map_point)
            map_.highlight_points(path)

            return False

    # pylint: disable=redefined-builtin
    def __init__(self, bounds: Rect, map: Map, hero: Hero, **kwargs):
        super().__init__(bounds, event_handler=self.__class__.EventHandler(self), **kwargs)
        self.map = map

        self.drawable_map_bounds = map.bounds
        self.hero = hero
        self.entities: List[Entity] = []

        self._draw_bounds = self.drawable_bounds

    def convert_window_point_to_map(self, point: Point) -> Point:
        '''
        Convert a point in window coordinates to a point relative to the map's
        origin point.
        '''
        return point - Vector.from_point(self._draw_bounds.origin)

    def update_drawable_map_bounds(self):
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
        hero_point = self.hero.position

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

        map_slice = np.s_[
            drawable_map_bounds.min_x: drawable_map_bounds.max_x + 1,
            drawable_map_bounds.min_y: drawable_map_bounds.max_y + 1]

        console_draw_bounds = self._draw_bounds
        console_slice = np.s_[
            console_draw_bounds.min_x: console_draw_bounds.max_x + 1,
            console_draw_bounds.min_y: console_draw_bounds.max_y + 1]

        console.tiles_rgb[console_slice] = self.map.composited_tiles[map_slice]

    def _draw_entities(self, console):
        map_bounds_vector = Vector.from_point(self.drawable_map_bounds.origin)
        draw_bounds_vector = Vector.from_point(self._draw_bounds.origin)

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
