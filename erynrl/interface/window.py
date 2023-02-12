# Eryn Wells <eryn@erynwells.me>

from typing import List

import numpy as np
from tcod.console import Console

from ..object import Entity
from ..geometry import Rect, Vector
from ..map import Map


class Window:
    '''A user interface window. It can be framed.'''

    def __init__(self, bounds: Rect, *, framed: bool = True):
        self.bounds = bounds
        self.is_framed = framed

    @property
    def drawable_bounds(self) -> Rect:
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


class MapWindow(Window):
    '''A Window that displays a game map'''

    def __init__(self, bounds: Rect, map_: Map, **kwargs):
        super().__init__(bounds, **kwargs)
        self.map = map_

        self.entities: List[Entity] = []

    def draw(self, console: Console):
        super().draw(console)
        self._draw_map(console)
        self._draw_entities(console)

    def _draw_map(self, console: Console):
        map_ = self.map
        map_size = map_.size

        drawable_bounds = self.drawable_bounds

        width = min(map_size.width, drawable_bounds.width)
        height = min(map_size.height, drawable_bounds.height)

        # TODO: Adjust the slice according to where the hero is.
        map_slice = np.s_[0:width, 0:height]

        min_x = drawable_bounds.min_x
        max_x = min_x + width
        min_y = drawable_bounds.min_y
        max_y = min_y + height

        console.tiles_rgb[min_x:max_x, min_y:max_y] = self.map.composited_tiles[map_slice]

    def _draw_entities(self, console):
        drawable_bounds_vector = Vector.from_point(self.drawable_bounds.origin)

        for ent in self.entities:
            # Only process entities that are in the field of view
            if not self.map.visible[tuple(ent.position)]:
                continue

            # Entity positions are 0-based relative to the (0, 0) point of the Map. In order to render them in the
            # correct position in the console, we need to offset the position.
            entity_position = ent.position
            map_tile_at_entity_position = self.map.composited_tiles[entity_position.x, entity_position.y]

            position = ent.position + drawable_bounds_vector
            console.print(
                x=position.x,
                y=position.y,
                string=ent.symbol,
                fg=ent.foreground,
                bg=tuple(map_tile_at_entity_position['bg'][:3]))

            # if ent.position == self.__current_mouse_point:
            #     entities_at_mouse_position.append(ent)

        # if len(entities_at_mouse_position) > 0:
        #     console.print(x=1, y=43, string=', '.join(e.name for e in entities_at_mouse_position))
