# Eryn Wells <eryn@erynwells.me>

from typing import List, TYPE_CHECKING

import numpy as np

from .corridor import CorridorGenerator
from .room import RoomGenerator
from ...geometry import Point

if TYPE_CHECKING:
    from .. import Map


class MapGenerator:
    '''Abstract base class defining an interface for generating a map and applying it to a set of tiles.'''

    @property
    def up_stairs(self) -> List[Point]:
        '''The location of any routes to a higher floor of the dungeon.'''
        raise NotImplementedError()

    @property
    def down_stairs(self) -> List[Point]:
        '''The location of any routes to a lower floor of the dungeon.'''
        raise NotImplementedError()

    # pylint: disable=redefined-builtin
    def generate(self, map: 'Map'):
        '''Generate a map and place it in `tiles`'''
        raise NotImplementedError()


class RoomsAndCorridorsGenerator(MapGenerator):
    '''
    Generates a classic "rooms and corridors" style map with the given room and corridor generators.
    '''

    def __init__(self, room_generator: RoomGenerator, corridor_generator: CorridorGenerator):
        self.room_generator = room_generator
        self.corridor_generator = corridor_generator

    @property
    def up_stairs(self) -> List[Point]:
        return self.room_generator.up_stairs

    @property
    def down_stairs(self) -> List[Point]:
        return self.room_generator.down_stairs

    # pylint: disable=redefined-builtin
    def generate(self, map: 'Map'):
        self.room_generator.generate()
        self.room_generator.apply(map)

        self.corridor_generator.generate(self.room_generator.rooms)
        self.corridor_generator.apply(map.tiles)
