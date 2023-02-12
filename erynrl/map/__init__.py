# Eryn Wells <eryn@erynwells.me>

'''
This module defines the level map, a number of basic building blocks (Rooms, etc), and objects that generate various
parts of a map.
'''

import random
from typing import Iterable

import numpy as np
import numpy.typing as npt
import tcod

from ..engine import Configuration
from ..geometry import Point, Rect, Size
from .generator import MapGenerator
from .tile import Empty, Shroud


class Map:
    '''A level map'''

    def __init__(self, config: Configuration, generator: MapGenerator):
        self.configuration = config

        map_size = config.map_size
        shape = map_size.numpy_shape

        self.tiles = np.full(shape, fill_value=Empty, order='F')
        generator.generate(self.tiles)

        self.up_stairs = generator.up_stairs
        self.down_stairs = generator.down_stairs

        self.highlighted = np.full(shape, fill_value=False, order='F')
        # Map tiles that are currently visible to the player
        self.visible = np.full(shape, fill_value=False, order='F')
        # Map tiles that the player has explored
        should_mark_all_tiles_explored = config.sandbox
        self.explored = np.full(shape, fill_value=should_mark_all_tiles_explored, order='F')

        self.__walkable_points = None

    @property
    def size(self) -> Size:
        '''The size of the map'''
        return self.configuration.map_size

    def random_walkable_position(self) -> Point:
        '''Return a random walkable point on the map.'''
        if not self.__walkable_points:
            self.__walkable_points = [Point(x, y) for x, y in np.ndindex(
                self.tiles.shape) if self.tiles[x, y]['walkable']]
        return random.choice(self.__walkable_points)

    def tile_is_in_bounds(self, point: Point) -> bool:
        '''Return True if the given point is inside the bounds of the map'''
        return 0 <= point.x < self.size.width and 0 <= point.y < self.size.height

    def tile_is_walkable(self, point: Point) -> bool:
        '''Return True if the tile at the given point is walkable'''
        return self.tile_is_in_bounds(point) and self.tiles[point.x, point.y]['walkable']

    def point_is_explored(self, point: Point) -> bool:
        return self.tile_is_in_bounds(point) and self.explored[point.x, point.y]

    def highlight_points(self, points: Iterable[Point]):
        '''Update the highlight graph with the list of points to highlight.'''
        self.highlighted.fill(False)

        for pt in points:
            self.highlighted[pt.x, pt.y] = True

    def print_to_console(self, console: tcod.Console, bounds: Rect) -> None:
        '''Render the map to the console.'''
        size = self.size

        # If a tile is in the visible array, draw it with the "light" color. If it's not, but it's in the explored
        # array, draw it with the "dark" color. Otherwise, draw it as Empty.
        console.tiles_rgb[0:size.width, 0:size.height] = np.select(
            condlist=[self.highlighted, self.visible, self.explored],
            choicelist=[self.tiles['highlighted'], self.tiles['light'], self.tiles['dark']],
            default=Shroud)
