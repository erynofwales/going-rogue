# Eryn Wells <eryn@erynwells.me>

import random

import numpy as np
import numpy.typing as npt
import tcod

from ..geometry import Point, Size
from .generator import MapGenerator
from .tile import Empty, Shroud


class Map:
    def __init__(self, size: Size, generator: MapGenerator):
        self.size = size

        self.generator = generator
        self.tiles = np.full(tuple(size), fill_value=Empty, order='F')
        generator.generate(self.tiles)

        self.up_stairs = generator.up_stairs
        self.down_stairs = generator.down_stairs

        # Map tiles that are currently visible to the player
        self.visible = np.full(tuple(self.size), fill_value=True, order='F')
        # Map tiles that the player has explored
        self.explored = np.full(tuple(self.size), fill_value=True, order='F')

        self.__walkable_points = None

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
        return self.tiles[point.x, point.y]['walkable']

    def print_to_console(self, console: tcod.Console) -> None:
        '''Render the map to the console.'''
        size = self.size

        # If a tile is in the visible array, draw it with the "light" color. If it's not, but it's in the explored
        # array, draw it with the "dark" color. Otherwise, draw it as Empty.
        console.tiles_rgb[0:size.width, 0:size.height] = np.select(
            condlist=[self.visible, self.explored],
            choicelist=[self.tiles['light'], self.tiles['dark']],
            default=Shroud)
