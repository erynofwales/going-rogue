# Eryn Wells <eryn@erynwells.me>

import math
import random
from dataclasses import dataclass
from typing import Iterable, Iterator, List, Optional, Tuple, TYPE_CHECKING

import tcod

from ... import log
from ...geometry import Point, Rect, Size
from ..room import RectangularRoom, Room
from ..tile import Empty, Floor, StairsDown, StairsUp, Wall

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


class RoomMethod:
    '''An abstract class defining a method for generating rooms.'''

    def room_in_rect(self, rect: Rect) -> Optional[Room]:
        '''Create a Room inside the given Rect.'''
        raise NotImplementedError()


class RectangularRoomMethod(RoomMethod):
    def room_in_rect(self, rect: Rect) -> Optional[Room]:
        return RectangularRoom(rect)


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


class RandomRectRoomGenerator(RoomGenerator):
    '''Generate rooms by repeatedly attempting to place rects of random size across the map.'''

    NUMBER_OF_ATTEMPTS_PER_ROOM = 30

    def _generate(self) -> bool:
        number_of_attempts = 0

        minimum_room_size = self.configuration.minimum_room_size
        maximum_room_size = self.configuration.maximum_room_size

        width_range = (minimum_room_size.width, maximum_room_size.width)
        height_range = (minimum_room_size.height, maximum_room_size.height)

        while len(self.rooms) < self.configuration.number_of_rooms:
            size = Size(random.randint(*width_range), random.randint(*height_range))
            origin = Point(random.randint(0, self.size.width - size.width),
                           random.randint(0, self.size.height - size.height))
            candidate_room_rect = Rect(origin, size)

            overlaps_any_existing_room = any(candidate_room_rect.intersects(room.bounds) for room in self.rooms)
            if not overlaps_any_existing_room:
                self.rooms.append(RectangularRoom(candidate_room_rect))
                number_of_attempts = 0
                continue

            number_of_attempts += 1
            if number_of_attempts > RandomRectRoomGenerator.NUMBER_OF_ATTEMPTS_PER_ROOM:
                break

        return True


class BSPRoomGenerator(RoomGenerator):
    '''Generate a rooms-and-corridors style map with BSP.'''

    def __init__(self, *, size: Size, config: Optional[RoomGenerator.Configuration] = None):
        super().__init__(size=size, config=config)
        self.rng: tcod.random.Random = tcod.random.Random()

    def _generate(self) -> bool:
        if self.rooms:
            return True

        minimum_room_size = self.configuration.minimum_room_size
        maximum_room_size = self.configuration.maximum_room_size

        # Recursively divide the map into squares of various sizes to place rooms in.
        bsp = tcod.bsp.BSP(x=0, y=0, width=self.size.width, height=self.size.height)

        # Add 2 to the minimum width and height to account for walls
        bsp.split_recursive(
            depth=4,
            min_width=minimum_room_size.width,
            min_height=minimum_room_size.height,
            max_horizontal_ratio=1.1,
            max_vertical_ratio=1.1)

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

            log.MAP.debug('|-> min room size %s', minimum_room_size)
            log.MAP.debug('|-> max room size %s', maximum_room_size)
            log.MAP.debug('|-> node size %s x %s', node.width, node.height)
            log.MAP.debug('|-> width range %s', width_range)
            log.MAP.debug('|-> height range %s', width_range)

            size = Size(self.rng.randint(*width_range),
                        self.rng.randint(*height_range))
            origin = Point(node.x + self.rng.randint(1, max(1, node.width - size.width - 2)),
                           node.y + self.rng.randint(1, max(1, node.height - size.height - 2)))
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
