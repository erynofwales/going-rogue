# Eryn Wells <eryn@erynwells.me>

'''
This module defines a bunch of mechanisms for generating maps.
'''

from typing import List, TYPE_CHECKING

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

    def generate(self, map: 'Map'):
        self.room_generator.generate(map)
        self.room_generator.apply(map)
        self.corridor_generator.generate(map)
        self.corridor_generator.apply(map)
