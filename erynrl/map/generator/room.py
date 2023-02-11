import random
from dataclasses import dataclass
from typing import List, Optional

import numpy as np
import tcod

from ... import log
from ...geometry import Direction, Point, Rect, Size
from ..room import Room, RectangularRoom
from ..tile import Empty, Floor, StairsUp, StairsDown, Wall


class RoomGenerator:
    '''Abstract room generator class.'''

    def __init__(self, *, size: Size):
        self.size = size
        self.rooms: List[Room] = []
        self.up_stairs: List[Point] = []
        self.down_stairs: List[Point] = []

    def generate(self):
        '''Generate rooms and stairs'''
        did_generate_rooms = self._generate()

        if did_generate_rooms:
            self._generate_stairs()

    def _generate(self) -> bool:
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
        '''Apply the generated rooms to a tile array'''
        self._apply(tiles)
        self._apply_stairs(tiles)

    def _apply(self, tiles: np.ndarray):
        '''
        Apply the generated list of rooms to an array of tiles. Subclasses must implement this.

        Arguments
        ---------
        tiles: np.ndarray
            The array of tiles to update.
        '''
        for room in self.rooms:
            for pt in room.floor_points:
                tiles[pt.x, pt.y] = Floor

        for room in self.rooms:
            for pt in room.wall_points:
                if tiles[pt.x, pt.y] != Empty:
                    continue
                tiles[pt.x, pt.y] = Wall

    def _generate_stairs(self):
        up_stair_room = random.choice(self.rooms)
        down_stair_room = None
        if len(self.rooms) >= 2:
            while down_stair_room is None or down_stair_room == up_stair_room:
                down_stair_room = random.choice(self.rooms)
        else:
            down_stair_room = up_stair_room

        self.up_stairs.append(random.choice(list(up_stair_room.walkable_tiles)))
        self.down_stairs.append(random.choice(list(down_stair_room.walkable_tiles)))

    def _apply_stairs(self, tiles):
        for pt in self.up_stairs:
            tiles[pt.x, pt.y] = StairsUp
        for pt in self.down_stairs:
            tiles[pt.x, pt.y] = StairsDown


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

class BSPRoomGenerator(RoomGenerator):
    '''Generate a rooms-and-corridors style map with BSP.'''

        self.rng: tcod.random.Random = tcod.random.Random()

    def _generate(self) -> bool:
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
        rooms: List[Room] = []

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

    def __rect_from_bsp_node(self, node: tcod.bsp.BSP) -> Rect:
        '''Create a Rect from the given BSP node object'''
        return Rect(Point(node.x, node.y), Size(node.width, node.height))
