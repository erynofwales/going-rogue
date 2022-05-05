#!/usr/bin/env python3
# Eryn Wells <eryn@erynwells.me>

import logging
import numpy as np
import random
import tcod
from .geometry import Direction, Point, Rect, Size
from .tile import Empty, Floor, Shroud, Wall
from dataclasses import dataclass
from typing import Iterator, List, Optional

LOG = logging.getLogger('map')

class Map:
    def __init__(self, size: Size):
        self.size = size

        self.generator = RoomsAndCorridorsGenerator(size=size)
        self.tiles = self.generator.generate()

        # Map tiles that are currently visible to the player
        self.visible = np.full(tuple(self.size), fill_value=False, order='F')
        # Map tiles that the player has explored
        self.explored = np.full(tuple(self.size), fill_value=False, order='F')

    def random_walkable_position(self) -> Point:
        # TODO: Include hallways
        random_room: RectangularRoom = random.choice(self.generator.rooms)
        floor = random_room.floor_bounds
        random_position_in_room = Point(random.randint(floor.min_x, floor.max_x),
                                        random.randint(floor.min_y, floor.max_y))
        return random_position_in_room

    def tile_is_in_bounds(self, point: Point) -> bool:
        return 0 <= point.x < self.size.width and 0 <= point.y < self.size.height

    def tile_is_walkable(self, point: Point) -> bool:
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

    @dataclass
    class Configuration:
        minimum_room_size: Size
        maximum_room_size: Size

    DefaultConfiguration = Configuration(
        minimum_room_size=Size(5, 5),
        maximum_room_size=Size(15, 15),
    )

    def __init__(self, *, size: Size, config: Optional[Configuration] = None):
        super().__init__(size=size)
        self.configuration = config if config else RoomsAndCorridorsGenerator.DefaultConfiguration

        self.rng: tcod.random.Random = tcod.random.Random()

        self.rooms: List['RectangularRoom'] = []
        self.tiles: Optional[np.ndarray] = None

    def generate(self) -> np.ndarray:
        if self.tiles:
            return self.tiles

        minimum_room_size = self.configuration.minimum_room_size
        maximum_room_size = self.configuration.maximum_room_size

        # Recursively divide the map into squares of various sizes to place rooms in.
        bsp = tcod.bsp.BSP(x=0, y=0, width=self.size.width, height=self.size.height)
        bsp.split_recursive(
            depth=4,
            # Add 2 to the minimum width and height to account for walls
            min_width=minimum_room_size.width + 2, min_height=minimum_room_size.height + 2,
            max_horizontal_ratio=1.5, max_vertical_ratio=1.5)

        tiles = np.full(tuple(self.size), fill_value=Empty, order='F')

        # Generate the rooms
        rooms: List['RectangularRoom'] = []
        # For nicer debug logging
        indent = 0

        room_attrname = f'{__class__.__name__}.room'

        for node in bsp.post_order():
            node_bounds = self.__rect_from_bsp_node(node)

            if node.children:
                LOG.debug(f'{" " * indent}{node_bounds}')

                left_room: RectangularRoom = getattr(node.children[0], room_attrname)
                right_room: RectangularRoom = getattr(node.children[1], room_attrname)

                left_room_bounds = left_room.bounds
                right_room_bounds = right_room.bounds

                LOG.debug(f'{" " * indent} left:{node.children[0]}, {left_room_bounds}')
                LOG.debug(f'{" " * indent}right:{node.children[1]}, {right_room_bounds}')

                start_point = left_room_bounds.midpoint
                end_point = right_room_bounds.midpoint

                # Randomly choose whether to move horizontally then vertically or vice versa
                if random.random() < 0.5:
                    corner = Point(end_point.x, start_point.y)
                else:
                    corner = Point(start_point.x, end_point.y)

                LOG.debug(f'{" " * indent}Digging tunnel between {start_point} and {end_point} with corner {corner}')
                LOG.debug(f'{" " * indent}`-> start:{left_room_bounds}')
                LOG.debug(f'{" " * indent}`->   end:{right_room_bounds}')

                for x, y in tcod.los.bresenham(tuple(start_point), tuple(corner)).tolist():
                    tiles[x, y] = Floor
                for x, y in tcod.los.bresenham(tuple(corner), tuple(end_point)).tolist():
                    tiles[x, y] = Floor

                indent += 2
            else:
                LOG.debug(f'{" " * indent}{node_bounds} (room) {node}')

                # Generate a room size between minimum_room_size and maximum_room_size. The minimum value is
                # straight-forward, but the maximum value needs to be clamped between minimum_room_size and the size of
                # the node.
                width_range = (minimum_room_size.width, min(maximum_room_size.width, max(minimum_room_size.width, node.width - 2)))
                height_range = (minimum_room_size.height, min(maximum_room_size.height, max(minimum_room_size.height, node.height - 2)))

                size = Size(self.rng.randint(*width_range), self.rng.randint(*height_range))
                origin = Point(node.x + self.rng.randint(1, max(1, node.width - size.width - 1)),
                               node.y + self.rng.randint(1, max(1, node.height - size.height - 1)))
                bounds = Rect(origin, size)

                LOG.debug(f'{" " * indent}`-> {bounds}')

                room = RectangularRoom(bounds)
                setattr(node, room_attrname, room)
                rooms.append(room)

                if not hasattr(node.parent, room_attrname):
                    setattr(node.parent, room_attrname, room)
                elif random.random() < 0.5:
                    setattr(node.parent, room_attrname, room)

                indent -= 2

            # Pass up a random child room so that parent nodes can connect subtrees to each other.
            parent = node.parent
            if parent:
                node_room = getattr(node, room_attrname)
                if not hasattr(node.parent, room_attrname):
                    setattr(node.parent, room_attrname, node_room)
                elif random.random() < 0.5:
                    setattr(node.parent, room_attrname, node_room)

        self.rooms = rooms

        for room in rooms:
            for wall_position in room.walls:
                if tiles[wall_position.x, wall_position.y] != Floor:
                    tiles[wall_position.x, wall_position.y] = Wall

            bounds = room.bounds
            # The range of a numpy array slice is [a, b).
            floor_rect = bounds.inset_rect(top=1, right=1, bottom=1, left=1)
            tiles[floor_rect.min_x:floor_rect.max_x + 1, floor_rect.min_y:floor_rect.max_y + 1] = Floor

        for y in range(self.size.height):
            for x in range(self.size.width):
                pos = Point(x, y)
                if tiles[x, y] != Floor:
                    continue

                neighbors = (pos + direction for direction in Direction.all())
                for neighbor in neighbors:
                    if tiles[neighbor.x, neighbor.y] != Empty:
                        continue
                    tiles[neighbor.x, neighbor.y] = Wall

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

    @property
    def floor_bounds(self) -> Rect:
        return self.bounds.inset_rect(top=1, right=1, bottom=1, left=1)

    @property
    def walls(self) -> Iterator[Point]:
        bounds = self.bounds
        min_y = bounds.min_y
        max_y = bounds.max_y
        min_x = bounds.min_x
        max_x = bounds.max_x
        for y in range(min_y, max_y + 1):
            for x in range(min_x, max_x + 1):
                if y == min_y or y == max_y or x == min_x or x == max_x:
                    yield Point(x, y)

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.bounds})'