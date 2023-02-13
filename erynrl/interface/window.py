# Eryn Wells <eryn@erynwells.me>

from typing import List

import numpy as np
from tcod.console import Console

from .. import log
from ..geometry import Point, Rect, Vector
from ..map import Map
from ..object import Entity, Hero


class Window:
    '''A user interface window. It can be framed.'''

    def __init__(self, bounds: Rect, *, framed: bool = True):
        self.bounds = bounds
        self.is_framed = framed

    @property
    def drawable_bounds(self) -> Rect:
        '''The bounds of the window that is drawable, inset by any frame'''
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


class MapWindow(Window):
    '''A Window that displays a game map'''

    # pylint: disable=redefined-builtin
    def __init__(self, bounds: Rect, map: Map, **kwargs):
        super().__init__(bounds, **kwargs)
        self.map = map

        self.drawable_map_bounds = map.bounds
        self.offset = Vector()
        self.entities: List[Entity] = []

    def update_drawable_map_bounds(self, hero: Hero):
        bounds = self.drawable_bounds
        map_bounds = self.map.bounds

        if map_bounds.width < bounds.width and map_bounds.height < bounds.height:
            # We can draw the whole map in the drawable bounds
            self.drawable_map_bounds = map_bounds

        # Attempt to keep the player centered in the viewport.

        hero_point = hero.position

        x = min(max(0, hero_point.x - bounds.mid_x), map_bounds.max_x - bounds.width)
        y = min(max(0, hero_point.y - bounds.mid_y), map_bounds.max_y - bounds.height)
        origin = Point(x, y)

        self.drawable_map_bounds = Rect(origin, bounds.size)

    def draw(self, console: Console):
        super().draw(console)
        self._draw_map(console)
        self._draw_entities(console)

    def _draw_map(self, console: Console):
        drawable_map_bounds = self.drawable_map_bounds
        drawable_bounds = self.drawable_bounds

        log.UI.info('Drawing map')
        log.UI.info('|- map bounds: %s', drawable_map_bounds)
        log.UI.info('|- window bounds: %s', drawable_bounds)

        map_slice = np.s_[
            drawable_map_bounds.min_x:drawable_map_bounds.max_x + 1,
            drawable_map_bounds.min_y:drawable_map_bounds.max_y + 1]

        console_slice = np.s_[
            drawable_bounds.min_x:drawable_bounds.max_x + 1,
            drawable_bounds.min_y:drawable_bounds.max_y + 1]

        log.UI.info('|- map slice: %s', map_slice)
        log.UI.info('`- console slice: %s', console_slice)

        console.tiles_rgb[console_slice] = self.map.composited_tiles[map_slice]

    def _draw_entities(self, console):
        map_bounds_vector = Vector.from_point(self.drawable_map_bounds.origin)
        drawable_bounds_vector = Vector.from_point(self.drawable_bounds.origin)

        log.UI.info('Drawing entities')

        for ent in self.entities:
            # Only draw entities that are in the field of view
            if not self.map.visible[tuple(ent.position)]:
                continue

            # Entity positions are 0-based relative to the (0, 0) point of the Map. In order to render them in the
            # correct position in the console, we need to offset the position.
            entity_position = ent.position
            map_tile_at_entity_position = self.map.composited_tiles[entity_position.x, entity_position.y]

            position = ent.position - map_bounds_vector + drawable_bounds_vector

            if isinstance(ent, Hero):
                log.UI.info('|- hero position on map %s', entity_position)
                log.UI.info('`- position in window %s', position)

            console.print(
                x=position.x,
                y=position.y,
                string=ent.symbol,
                fg=ent.foreground,
                bg=tuple(map_tile_at_entity_position['bg'][:3]))
