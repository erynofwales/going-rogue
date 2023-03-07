# Eryn Wells <eryn@erynwells.me>

import math
import random
from dataclasses import dataclass
from typing import Iterable, Iterator, List, Optional, Tuple, TYPE_CHECKING

import numpy as np
import tcod

from ... import log
from ...geometry import Point, Rect, Size
from ..room import FreeformRoom, RectangularRoom, Room
from ..tile import Empty, Floor, StairsDown, StairsUp, Wall, tile_datatype
from .cellular_atomata import CellularAtomataMapGenerator

if TYPE_CHECKING:
    from .. import Map


class RoomGenerator:
    '''Abstract room generator class.'''

    @dataclass
    class Configuration:
        rect_method: 'RectMethod'
        room_method: 'RoomMethod'

    def __init__(self, *, size: Size, config: Configuration):
        self.size = size
        self.configuration = config

        self.rooms: List[Room] = []

        self.up_stairs: List[Point] = []
        self.down_stairs: List[Point] = []

    def generate(self):
        '''Generate rooms and stairs'''
        rect_method = self.configuration.rect_method
        room_method = self.configuration.room_method

        for rect in rect_method.generate():
            room = room_method.room_in_rect(rect)
            if not room:
                break
            self.rooms.append(room)

        if len(self.rooms) == 0:
            return

        self._generate_stairs()

    # pylint: disable=redefined-builtin
    def apply(self, map: 'Map'):
        '''Apply the generated rooms to a tile array'''
        self._apply(map)
        self._apply_stairs(map.tiles)

    def _apply(self, map: 'Map'):
        '''
        Apply the generated list of rooms to an array of tiles. Subclasses must implement this.

        Arguments
        ---------
        map: Map
            The game map to apply the generated room to
        '''
        tiles = map.tiles

        for room in self.rooms:
            for pt in room.floor_points:
                tiles[pt.numpy_index] = Floor

        for room in self.rooms:
            for pt in room.wall_points:
                idx = pt.numpy_index

                if tiles[idx] != Empty:
                    continue

                tiles[idx] = Wall

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
            tiles[pt.numpy_index] = StairsUp
        for pt in self.down_stairs:
            tiles[pt.numpy_index] = StairsDown


class RectMethod:
    '''An abstract class defining a method for generating rooms.'''

    def __init__(self, *, size: Size):
        self.size = size

    def generate(self) -> Iterator[Rect]:
        '''Generate rects to place rooms in until there are no more.'''
        raise NotImplementedError()


class OneBigRoomRectMethod(RectMethod):
    '''
    A room generator method that yields one large rectangle centered in the
    bounds defined by the zero origin and `self.size`.
    '''

    @dataclass
    class Configuration:
        '''
        Configuration for a OneBigRoom room generator method.

        ### Attributes

        width_percentage : float
            The percentage of overall width to make the room
        height_percentage : float
            The percentage of overall height to make the room
        '''
        width_percentage: float = 0.5
        height_percentage: float = 0.5

    def __init__(self, *, size: Size, config: Optional[Configuration] = None):
        super().__init__(size=size)
        self.configuration = config or self.__class__.Configuration()

    def generate(self) -> Iterator[Rect]:
        width = self.size.width
        height = self.size.height

        size = Size(math.floor(width * self.configuration.width_percentage),
                    math.floor(height * self.configuration.height_percentage))
        origin = Point((width - size.width) // 2, (height - size.height) // 2)

        yield Rect(origin, size)


class RandomRectMethod(RectMethod):
    NUMBER_OF_ATTEMPTS_PER_RECT = 30

    @dataclass
    class Configuration:
        number_of_rooms: int = 30
        minimum_room_size: Size = Size(7, 7)
        maximum_room_size: Size = Size(20, 20)

    def __init__(self, *, size: Size, config: Optional[Configuration] = None):
        super().__init__(size=size)
        self.configuration = config or self.__class__.Configuration()
        self._rects: List[Rect] = []

    def generate(self) -> Iterator[Rect]:
        minimum_room_size = self.configuration.minimum_room_size
        maximum_room_size = self.configuration.maximum_room_size

        width_range = (minimum_room_size.width, maximum_room_size.width)
        height_range = (minimum_room_size.height, maximum_room_size.height)

        while len(self._rects) < self.configuration.number_of_rooms:
            for _ in range(self.__class__.NUMBER_OF_ATTEMPTS_PER_RECT):
                size = Size(random.randint(*width_range), random.randint(*height_range))
                origin = Point(random.randint(0, self.size.width - size.width),
                               random.randint(0, self.size.height - size.height))
                candidate_rect = Rect(origin, size)

                overlaps_any_existing_room = any(candidate_rect.intersects(r) for r in self._rects)
                if not overlaps_any_existing_room:
                    break
            else:
                return

            self._rects.append(candidate_rect)
            yield candidate_rect


class BSPRectMethod(RectMethod):
    @dataclass
    class Configuration:
        '''
        Configuration for the binary space partitioning (BSP) Rect method.

        ### Attributes

        number_of_rooms : int
            The maximum number of rooms to produce
        maximum_room_size : Size
            The maximum size of any room
        minimum_room_size : Size
            The minimum size of any room
        room_size_ratio : Tuple[float, float]
            A pair of floats indicating the maximum proportion the sides of a
            BSP node can have to each other.

            The first value is the horizontal ratio. BSP nodes will never have a
            horizontal size (width) bigger than `room_size_ratio[0]` times the
            vertical size.

            The second value is the vertical ratio. BSP nodes will never have a
            vertical size (height) larger than `room_size_ratio[1]` times the
            horizontal size.

            The closer these values are to 1.0, the more square the BSP nodes
            will be.
        '''
        number_of_rooms: int = 30
        minimum_room_size: Size = Size(7, 7)
        maximum_room_size: Size = Size(20, 20)
        room_size_ratio: Tuple[float, float] = (1.1, 1.1)

    def __init__(self, *, size: Size, config: Optional[Configuration] = None):
        super().__init__(size=size)
        self.configuration = config or self.__class__.Configuration()

    def generate(self) -> Iterator[Rect]:
        nodes_with_rooms = set()

        minimum_room_size = self.configuration.minimum_room_size
        maximum_room_size = self.configuration.maximum_room_size

        # Recursively divide the map into squares of various sizes to place rooms in.
        bsp = tcod.bsp.BSP(x=0, y=0, width=self.size.width, height=self.size.height)

        # Add 2 to the minimum width and height to account for walls
        bsp.split_recursive(
            depth=6,
            min_width=minimum_room_size.width,
            min_height=minimum_room_size.height,
            max_horizontal_ratio=self.configuration.room_size_ratio[0],
            max_vertical_ratio=self.configuration.room_size_ratio[1])

        log.MAP_BSP.info('Generating room rects via BSP')

        # Visit all nodes in a level before visiting any of their children
        for bsp_node in bsp.level_order():
            node_width = bsp_node.w
            node_height = bsp_node.h

            if node_width > maximum_room_size.width or node_height > maximum_room_size.height:
                log.MAP_BSP.debug('Node with size (%s, %s) exceeds maximum size %s',
                                  node_width, node_height, maximum_room_size)
                continue

            if len(nodes_with_rooms) >= self.configuration.number_of_rooms:
                # Made as many rooms as we're allowed. We're done.
                log.MAP_BSP.debug("Generated enough rooms (more than %d); we're done",
                                  self.configuration.number_of_rooms)
                return

            if any(node in nodes_with_rooms for node in self.__all_parents_of_node(bsp_node)):
                # Already made a room for one of this node's parents
                log.MAP_BSP.debug('Already made a room for parent of %s', bsp_node)
                continue

            try:
                probability_of_room = max(
                    1.0 / (node_width - minimum_room_size.width),
                    1.0 / (node_height - minimum_room_size.height))
            except ZeroDivisionError:
                probability_of_room = 1.0

            log.MAP_BSP.info('Probability of generating room for %s: %f', bsp_node, probability_of_room)

            if random.random() <= probability_of_room:
                log.MAP_BSP.info('Yielding room for node %s', bsp_node)
                nodes_with_rooms.add(bsp_node)
                yield self.__rect_from_bsp_node(bsp_node)

        log.MAP_BSP.info('Finished BSP room rect generation, yielded %d rooms', len(nodes_with_rooms))

    def __rect_from_bsp_node(self, bsp_node: tcod.bsp.BSP) -> Rect:
        return Rect.from_raw_values(bsp_node.x, bsp_node.y, bsp_node.w, bsp_node.h)

    def __all_parents_of_node(self, node: tcod.bsp.BSP | None) -> Iterable[tcod.bsp.BSP]:
        while node:
            yield node
            node = node.parent


class RoomMethod:
    '''An abstract class defining a method for generating rooms.'''

    def room_in_rect(self, rect: Rect) -> Optional[Room]:
        '''Create a Room inside the given Rect.'''
        raise NotImplementedError()


class RectangularRoomMethod(RoomMethod):
    def room_in_rect(self, rect: Rect) -> Optional[Room]:
        return RectangularRoom(rect)


class CellularAtomatonRoomMethod(RoomMethod):

    def __init__(self, cellular_atomaton_config: CellularAtomataMapGenerator.Configuration):
        self.cellular_atomaton_configuration = cellular_atomaton_config

    def room_in_rect(self, rect: Rect) -> Optional[Room]:
        # The cellular atomaton doesn't generate any walls, just floors and
        # emptiness. Inset it by 1 all the way around so that we can draw walls
        # around it.

        atomaton_rect = rect.inset_rect(1, 1, 1, 1)
        room_generator = CellularAtomataMapGenerator(atomaton_rect, self.cellular_atomaton_configuration)
        room_generator.generate()

        # Create a new tile array and copy the result of the atomaton into it,
        # then draw walls everywhere that neighbors a floor tile.

        width = rect.width
        height = rect.height

        room_tiles = np.full((height, width), fill_value=Empty, dtype=tile_datatype, order='C')
        room_tiles[1:height - 1, 1:width - 1] = room_generator.tiles

        for y, x in np.ndindex(room_tiles.shape):
            if room_tiles[y, x] == Floor:
                continue

            for neighbor in Point(x, y).neighbors:
                try:
                    if room_tiles[neighbor.y, neighbor.x] != Floor:
                        continue
                    room_tiles[y, x] = Wall
                    break
                except IndexError:
                    pass

        return FreeformRoom(rect, room_tiles)


class OrRoomMethod(RoomMethod):
    '''
    A room generator method that picks between several RoomMethods at random
    based on a set of probabilities.
    '''

    def __init__(self, methods: Iterable[Tuple[float, RoomMethod]]):
        assert sum(m[0] for m in methods) == 1.0
        self.methods = methods

    def room_in_rect(self, rect: Rect) -> Optional[Room]:
        factor = random.random()

        threshold = 0
        for method in self.methods:
            threshold += method[0]
            if factor <= threshold:
                return method[1].room_in_rect(rect)

        return None
