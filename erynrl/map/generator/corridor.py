# Eryn Wells <eryn@erynwells.me>

'''
Defines an abstract CorridorGenerator and several concrete subclasses. These classes generate corridors between rooms.
'''

import random
from itertools import pairwise
from typing import List

import tcod
import numpy as np

from ... import log
from ...geometry import Point
from ..room import Room
from ..tile import Empty, Floor, Wall


class CorridorGenerator:
    '''
    Corridor generators produce corridors between rooms.
    '''

    def generate(self, rooms: List[Room]) -> bool:
        '''Generate corridors given a list of rooms.'''
        raise NotImplementedError()

    def apply(self, tiles: np.ndarray):
        '''Apply corridors to a tile grid.'''
        raise NotImplementedError()


class ElbowCorridorGenerator(CorridorGenerator):
    '''
    Generators corridors using a simple "elbow" algorithm:

    ```
    For each pair of rooms:
        1. Find the midpoint of the bounding rect of each room
        2. Calculate an elbow point
        3. Draw a path from the midpoint of the first room to the elbow point
        4. Draw a path from the elbow point to the midpoint of the second room
    ```
    '''

    def __init__(self):
        self.corridors: List[List[Point]] = []

    def generate(self, rooms: List[Room]) -> bool:
        if len(rooms) < 2:
            return True

        for (left_room, right_room) in pairwise(rooms):
            corridor = self._generate_corridor_between(left_room, right_room)
            self.corridors.append(corridor)

        for i in range(len(rooms) - 2):
            corridor = self._generate_corridor_between(rooms[i], rooms[i + 2])
            self.corridors.append(corridor)

        return True

    def _generate_corridor_between(self, left_room, right_room):
        left_room_bounds = left_room.bounds
        right_room_bounds = right_room.bounds

        log.MAP.debug(' left: %s, %s', left_room, left_room_bounds)
        log.MAP.debug('right: %s, %s', right_room, right_room_bounds)

        start_point = left_room_bounds.midpoint
        end_point = right_room_bounds.midpoint

        # Randomly choose whether to move horizontally then vertically or vice versa
        if random.random() < 0.5:
            corner = Point(end_point.x, start_point.y)
        else:
            corner = Point(start_point.x, end_point.y)

        log.MAP.debug('Digging a tunnel between %s and %s with corner %s', start_point, end_point, corner)
        log.MAP.debug('|-> start: %s', left_room_bounds)
        log.MAP.debug('`->   end: %s', right_room_bounds)

        corridor: List[Point] = []

        for x, y in tcod.los.bresenham(tuple(start_point), tuple(corner)).tolist():
            corridor.append(Point(x, y))

        for x, y in tcod.los.bresenham(tuple(corner), tuple(end_point)).tolist():
            corridor.append(Point(x, y))

        return corridor

    def apply(self, tiles):
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
