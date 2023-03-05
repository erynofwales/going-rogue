# Eryn Wells <eryn@erynwells.me>

from typing import List

import numpy as np
from tcod.console import Console

from .. import log
from ..geometry import Point, Rect, Size, Vector
from ..map import Map
from ..object import Entity, Hero


class Window:
    '''A user interface window. It can be framed.'''

    def __init__(self, bounds: Rect, *, framed: bool = True):
        self.bounds = bounds
        self.is_framed = framed

    @property
    def drawable_bounds(self) -> Rect:
        '''
        The bounds of the window that is drawable, inset by its frame if
        `is_framed` is `True`.
        '''
        if self.is_framed:
            return self.bounds.inset_rect(1, 1, 1, 1)
        return self.bounds

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
