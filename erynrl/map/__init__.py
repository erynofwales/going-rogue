# Eryn Wells <eryn@erynwells.me>

'''
This module defines the level map, a number of basic building blocks (Rooms, etc), and objects that generate various
parts of a map.
'''

import random
from typing import Iterable, List

import numpy as np
import tcod

from ..configuration import Configuration
from ..geometry import Point, Rect, Size
from .generator import MapGenerator
from .room import Corridor, Room
from .tile import Empty, Shroud


class Map:
    '''A level map'''

    def __init__(self, config: Configuration, generator: MapGenerator):
        self.configuration = config

        map_size = config.map_size
        self._bounds = Rect(Point(), map_size)

        shape = map_size.numpy_shape
        self.tiles = np.full(shape, fill_value=Empty, order='F')

        self.highlighted = np.full(shape, fill_value=False, order='F')

        # Map tiles that are currently visible to the player
        self.visible = np.full(shape, fill_value=False, order='F')
        # Map tiles that the player has explored
        should_mark_all_tiles_explored = config.sandbox
        self.explored = np.full(shape, fill_value=should_mark_all_tiles_explored, order='F')

        self.__walkable_points = None

        generator.generate(self)

        # Map Features
        self.rooms: List[Room] = []
        self.corridors: List[Corridor] = []
        self.up_stairs = generator.up_stairs
        self.down_stairs = generator.down_stairs

    @property
    def bounds(self) -> Rect:
        '''The bounds of the map'''
        return self._bounds

    @property
    def size(self) -> Size:
        '''The size of the map'''
        return self.configuration.map_size

    @property
    def composited_tiles(self) -> np.ndarray:
        # TODO: Hold onto the result here so that this doen't have to be done every time this property is called.
        return np.select(
            condlist=[
                self.highlighted,
                self.visible,
                self.explored],
            choicelist=[
                self.tiles['highlighted'],
                self.tiles['light'],
                self.tiles['dark']],
            default=Shroud)

    def update_visible_tiles(self, point: Point, radius: int):
        field_of_view = tcod.map.compute_fov(self.tiles['transparent'], tuple(point), radius=radius)

        # The player's computed field of view
        self.visible[:] = field_of_view

    def random_walkable_position(self) -> Point:
        '''Return a random walkable point on the map.'''
        if not self.__walkable_points:
            self.__walkable_points = [Point(x, y) for x, y in np.ndindex(
                self.tiles.shape) if self.tiles[x, y]['walkable']]
        return random.choice(self.__walkable_points)

    def point_is_in_bounds(self, point: Point) -> bool:
        '''Return True if the given point is inside the bounds of the map'''
        return 0 <= point.x < self.size.width and 0 <= point.y < self.size.height

    def point_is_walkable(self, point: Point) -> bool:
        '''Return True if the tile at the given point is walkable'''
        if not self.point_is_in_bounds(point):
            raise ValueError(f'Point {point!s} is not in bounds')
        return self.tiles[point.numpy_index]['walkable']

    def point_is_visible(self, point: Point) -> bool:
        '''Return True if the point is visible to the player'''
        if not self.point_is_in_bounds(point):
            raise ValueError(f'Point {point!s} is not in bounds')
        return self.visible[point.numpy_index]

    def point_is_explored(self, point: Point) -> bool:
        '''Return True if the tile at the given point has been explored by the player'''
        if not self.point_is_in_bounds(point):
            raise ValueError(f'Point {point!s} is not in bounds')
        return self.explored[point.numpy_index]

    def highlight_points(self, points: Iterable[Point]):
        '''Update the highlight graph with the list of points to highlight.'''
        self.highlighted.fill(False)

        for pt in points:
            self.highlighted[pt.numpy_index] = True

    def find_walkable_path_from_point_to_point(self, point_a: Point, point_b: Point) -> Iterable[Point]:
        '''
        Find a path between point A and point B using tcod's A* implementation.
        '''
        a_star = tcod.path.AStar(self.tiles['walkable'])
        path = a_star.get_path(point_a.x, point_a.y, point_b.x, point_b.y)
        return map(lambda t: Point(t[0], t[1]), path)

    def __str__(self):
        string = ''

        tiles = self.tiles['light']['ch']
        for row in tiles:
            string += ''.join(chr(n) for n in row) + '\n'

        return string
