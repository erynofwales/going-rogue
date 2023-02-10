import random
from dataclasses import dataclass
from typing import List, Optional

import numpy as np
import tcod

from ... import log
from ...geometry import Direction, Point, Rect, Size
from ..room import Room, RectangularRoom
from ..tile import Empty, Floor, Wall


class RoomGenerator:
    '''Abstract room generator class.'''

    def __init__(self, *, size: Size):
        self.size = size
        self.rooms: List[Room] = []

    def generate(self) -> bool:
        '''
        Generate a list of rooms.

        Subclasses should implement this and fill in their specific map
        generation algorithm.

        Returns
        -------
        np.ndarray
            A two-dimensional array of tiles. Dimensions should match the given size.
        '''
        raise NotImplementedError()

    def apply(self, tiles: np.ndarray):
        '''
        Apply the generated list of rooms to an array of tiles. Subclasses must implement this.

        Arguments
        ---------
        tiles: np.ndarray
            The array of tiles to update.
        '''
        raise NotImplementedError()


class BSPRoomGenerator(RoomGenerator):
    '''Generate a rooms-and-corridors style map with BSP.'''

    @dataclass
    class Configuration:
        '''Configuration parameters for BSPRoomGenerator.'''

        minimum_room_size: Size
        maximum_room_size: Size

    DefaultConfiguration = Configuration(
        minimum_room_size=Size(7, 7),
        maximum_room_size=Size(20, 20),
    )

    def __init__(self, *, size: Size, config: Optional[Configuration] = None):
        super().__init__(size=size)
        self.configuration = config if config else BSPRoomGenerator.DefaultConfiguration

        self.rng: tcod.random.Random = tcod.random.Random()

        self.rooms: List[RectangularRoom] = []
        self.tiles: Optional[np.ndarray] = None

    def generate(self) -> bool:
        if self.rooms:
            return True

        minimum_room_size = self.configuration.minimum_room_size
        maximum_room_size = self.configuration.maximum_room_size

        # Recursively divide the map into squares of various sizes to place rooms in.
        bsp = tcod.bsp.BSP(x=0, y=0, width=self.size.width, height=self.size.height)

        # Add 2 to the minimum width and height to account for walls
        gap_for_walls = 2
        bsp.split_recursive(
            depth=4,
            min_width=minimum_room_size.width + gap_for_walls,
            min_height=minimum_room_size.height + gap_for_walls,
            max_horizontal_ratio=1.1,
            max_vertical_ratio=1.1
        )

        # Generate the rooms
        rooms: List['RectangularRoom'] = []

        room_attrname = f'{__class__.__name__}.room'

        for node in bsp.post_order():
            node_bounds = self.__rect_from_bsp_node(node)

            if node.children:
                continue

            log.MAP.debug('%s (room) %s', node_bounds, node)

            # Generate a room size between minimum_room_size and maximum_room_size. The minimum value is
            # straight-forward, but the maximum value needs to be clamped between minimum_room_size and the size of
            # the node.
            width_range = (
                minimum_room_size.width,
                min(maximum_room_size.width, max(
                    minimum_room_size.width, node.width - 2))
            )
            height_range = (
                minimum_room_size.height,
                min(maximum_room_size.height, max(
                    minimum_room_size.height, node.height - 2))
            )

            size = Size(self.rng.randint(*width_range),
                        self.rng.randint(*height_range))
            origin = Point(node.x + self.rng.randint(1, max(1, node.width - size.width - 1)),
                           node.y + self.rng.randint(1, max(1, node.height - size.height - 1)))
            bounds = Rect(origin, size)

            log.MAP.debug('`-> %s', bounds)

            room = RectangularRoom(bounds)
            setattr(node, room_attrname, room)
            rooms.append(room)

            if not hasattr(node.parent, room_attrname):
                setattr(node.parent, room_attrname, room)
            elif random.random() < 0.5:
                setattr(node.parent, room_attrname, room)

            # Pass up a random child room so that parent nodes can connect subtrees to each other.
            parent = node.parent
            if parent:
                node_room = getattr(node, room_attrname)
                if not hasattr(node.parent, room_attrname):
                    setattr(node.parent, room_attrname, node_room)
                elif random.random() < 0.5:
                    setattr(node.parent, room_attrname, node_room)

        self.rooms = rooms

        return True

    def apply(self, tiles: np.ndarray):
        for room in self.rooms:
            for wall_position in room.walls:
                if tiles[wall_position.x, wall_position.y] != Floor:
                    tiles[wall_position.x, wall_position.y] = Wall

            bounds = room.bounds
            # The range of a numpy array slice is [a, b).
            floor_rect = bounds.inset_rect(top=1, right=1, bottom=1, left=1)
            tiles[floor_rect.min_x:floor_rect.max_x + 1,
                  floor_rect.min_y:floor_rect.max_y + 1] = Floor

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

    def __rect_from_bsp_node(self, node: tcod.bsp.BSP) -> Rect:
        '''Create a Rect from the given BSP node object'''
        return Rect(Point(node.x, node.y), Size(node.width, node.height))
