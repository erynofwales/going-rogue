# Eryn Wells <eryn@erynwells.me>

'''
Defines an abstract CorridorGenerator and several concrete subclasses. These classes generate corridors between rooms.
'''

import random
from itertools import pairwise
from typing import List, TYPE_CHECKING

import tcod

from ... import log
from ...geometry import Point
from ..room import Corridor, Room
from ..tile import Empty, Floor, Wall

if TYPE_CHECKING:
    from .. import Map


class CorridorGenerator:
    '''
    Corridor generators produce corridors between rooms.
    '''

    def generate(self, map: 'Map') -> bool:
        '''Generate corridors given a list of rooms.'''
        raise NotImplementedError()

    def apply(self, map: 'Map'):
        '''Apply corridors to a tile grid.'''
        raise NotImplementedError()

    def _sorted_rooms(self, rooms: List[Room]) -> List[Room]:
        return sorted(rooms, key=lambda r: r.bounds.origin)


class ElbowCorridorGenerator(CorridorGenerator):
    '''
    Generators corridors using a simple "elbow" algorithm:

    ```
    For each pair of rooms:
        1. Find the midpoint of the bounding rect of each room
        2. For each pair of rooms:
            1. Calculate an elbow point by taking the x coordinate of one room
               and the y coordinate of the other room, choosing which x and which
               y at random.
            2. Draw a path from the midpoint of the first room to the elbow point
            3. Draw a path from the elbow point to the midpoint of the second room
    ```
    '''

    def __init__(self):
        self.corridors: List[Corridor] = []

    def generate(self, map: 'Map') -> bool:
        rooms = map.rooms

        if len(rooms) < 2:
            return True

        sorted_rooms = self._sorted_rooms(rooms)

        for left_room, right_room in pairwise(sorted_rooms):
            corridor = self._generate_corridor_between(left_room, right_room)
            self.corridors.append(corridor)

        return True

    def _generate_corridor_between(self, left_room, right_room) -> Corridor:
        left_room_bounds = left_room.bounds
        right_room_bounds = right_room.bounds

        log.MAP.debug(' left: %s, %s', left_room, left_room_bounds)
        log.MAP.debug('right: %s, %s', right_room, right_room_bounds)

        start_point = left_room_bounds.midpoint
        end_point = right_room_bounds.midpoint

        # Randomly choose whether to move horizontally then vertically or vice versa
        horizontal_first = random.random() < 0.5
        if horizontal_first:
            corner = Point(end_point.x, start_point.y)
        else:
            corner = Point(start_point.x, end_point.y)

        log.MAP.debug(
            'Digging a tunnel between %s and %s with corner %s (%s)',
            start_point,
            end_point,
            corner,
            'horizontal' if horizontal_first else 'vertical')
        log.MAP.debug('|-> start: %s', left_room_bounds)
        log.MAP.debug('`->   end: %s', right_room_bounds)

        corridor: List[Point] = []

        for x, y in tcod.los.bresenham(tuple(start_point), tuple(corner)).tolist():
            corridor.append(Point(x, y))

        for x, y in tcod.los.bresenham(tuple(corner), tuple(end_point)).tolist():
            corridor.append(Point(x, y))

        return Corridor(points=corridor)

    def apply(self, map: 'Map'):
        tiles = map.tiles

        map.corridors = self.corridors

        for corridor in self.corridors:
            for pt in corridor:
                tiles[pt.x, pt.y] = Floor
                for neighbor in pt.neighbors:
                    if not (0 <= neighbor.x < tiles.shape[0] and 0 <= neighbor.y < tiles.shape[1]):
                        continue
                    if tiles[neighbor.x, neighbor.y] == Empty:
                        tiles[neighbor.x, neighbor.y] = Wall


class NetHackCorridorGenerator(CorridorGenerator):
    '''A corridor generator that produces doors and corridors that look like Nethack's Dungeons of Doom levels.'''
