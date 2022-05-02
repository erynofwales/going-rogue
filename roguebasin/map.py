#!/usr/bin/env python3
# Eryn Wells <eryn@erynwells.me>

import logging
import numpy as np
import random
import tcod
from .geometry import Point, Rect, Size
from .tile import Floor, Wall
from typing import List, Optional

LOG = logging.getLogger('map')

class Map:
    def __init__(self, size: Size):
        self.size = size

        self.generator = RoomsAndCorridorsGenerator(size=size)
        self.tiles = self.generator.generate()

    def tile_is_in_bounds(self, point: Point) -> bool:
        return 0 <= point.x < self.size.width and 0 <= point.y < self.size.height

    def tile_is_walkable(self, point: Point) -> bool:
        return self.tiles[point.x, point.y]['walkable']

    def print_to_console(self, console: tcod.Console) -> None:
        size = self.size
        console.tiles_rgb[0:size.width, 0:size.height] = self.tiles["dark"]

class MapGenerator:
    def __init__(self, *, size: Size):
        self.size = size

    def generate(self) -> np.ndarray:
        '''
        Generate a tile grid

        Subclasses should implement this and fill in their specific map
        generation algorithm.
        '''
        raise NotImplementedError()

class RoomsAndCorridorsGenerator(MapGenerator):
    '''Generate a rooms-and-corridors style map with BSP.'''

    class Configuration:
        def __init__(self, min_room_size: Size):
            self.minimum_room_size = min_room_size

    DefaultConfiguration = Configuration(
        min_room_size=Size(8, 8)
    )

    def __init__(self, *, size: Size, config: Optional[Configuration] = None):
        super().__init__(size=size)
        self.configuration = config if config else RoomsAndCorridorsGenerator.DefaultConfiguration

        self.rng: tcod.random.Random = tcod.random.Random()

        self.rooms: List['RectanularRoom'] = []
        self.tiles: Optional[np.ndarray] = None

    def generate(self) -> np.ndarray:
        if self.tiles:
            return self.tiles

        minimum_room_size = self.configuration.minimum_room_size

        # Recursively divide the map into squares of various sizes to place rooms in.
        bsp = tcod.bsp.BSP(x=0, y=0, width=self.size.width, height=self.size.height)
        bsp.split_recursive(
            depth=4,
            min_width=minimum_room_size.width, min_height=minimum_room_size.height,
            max_horizontal_ratio=1.5, max_vertical_ratio=1.5)

        tiles = np.full(tuple(self.size), fill_value=Wall, order='F')

        # Generate the rooms
        rooms: List['RectangularRoom'] = []
        # For nicer debug logging
        indent = 0

        for node in bsp.post_order():
            node_bounds = self.__rect_from_bsp_node(node)

            if node.children:
                LOG.debug(f'{" " * indent}{node_bounds}')

                left_node_bounds = self.__rect_from_bsp_node(node.children[0])
                right_node_bounds = self.__rect_from_bsp_node(node.children[1])

                LOG.debug(f'{" " * indent} left:{node.children[0]}, {left_node_bounds}')
                LOG.debug(f'{" " * indent}right:{node.children[1]}, {right_node_bounds}')

                start_point = left_node_bounds.midpoint
                end_point = right_node_bounds.midpoint

                # Randomly choose whether to move horizontally then vertically or vice versa
                if random.random() < 0.5:
                    corner = Point(end_point.x, start_point.y)
                else:
                    corner = Point(start_point.x, end_point.y)

                LOG.debug(f'{" " * indent}Digging tunnel between {start_point} and {end_point} with corner {corner}')
                LOG.debug(f'{" " * indent}`-> start:{left_node_bounds}')
                LOG.debug(f'{" " * indent}`->   end:{right_node_bounds}')

                for x, y in tcod.los.bresenham(tuple(start_point), tuple(corner)).tolist():
                    tiles[x, y] = Floor
                for x, y in tcod.los.bresenham(tuple(corner), tuple(end_point)).tolist():
                    tiles[x, y] = Floor

                indent += 2
            else:
                LOG.debug(f'{" " * indent}{node_bounds} (room) {node}')

                size = Size(self.rng.randint(5, min(15, max(5, node.width - 2))),
                            self.rng.randint(5, min(15, max(5, node.height - 2))))
                origin = Point(node.x + self.rng.randint(1, max(1, node.width - size.width - 1)),
                               node.y + self.rng.randint(1, max(1, node.height - size.height - 1)))
                bounds = Rect(origin, size)

                LOG.debug(f'{" " * indent}`-> {bounds}')

                room = RectangularRoom(bounds)
                rooms.append(room)

                indent -= 2

        self.rooms = rooms

        for room in rooms:
            bounds = room.bounds
            tiles[bounds.min_x:bounds.max_x, bounds.min_y:bounds.max_y] = Floor

        self.tiles = tiles

        return tiles

    def generate_tunnel(self, start_room_bounds: Rect, end_room_bounds: Rect):
        pass

    def __rect_from_bsp_node(self, node: tcod.bsp.BSP) -> Rect:
        return Rect(Point(node.x, node.y), Size(node.width, node.height))


class RectangularRoom:
    def __init__(self, bounds: Rect):
        self.bounds = bounds

    @property
    def center(self) -> Point:
        return self.bounds.midpoint

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.bounds})'