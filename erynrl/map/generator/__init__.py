import numpy as np

from ..tile import Empty
from .corridor import CorridorGenerator
from .room import RoomGenerator


class MapGenerator:
    '''Abstract base class defining an interface for generating a map and applying it to a set of tiles.'''

    def generate(self, tiles: np.ndarray):
        raise NotImplementedError()


class RoomsAndCorridorsGenerator(MapGenerator):
    '''
    Generates a classic "rooms and corridors" style map with the given room and corridor generators.
    '''

    def __init__(self, room_generator: RoomGenerator, corridor_generator: CorridorGenerator):
        self.room_generator = room_generator
        self.corridor_generator = corridor_generator

    def generate(self, tiles: np.ndarray):
        self.room_generator.generate()
        self.room_generator.apply(tiles)

        self.corridor_generator.generate(self.room_generator.rooms)
        self.corridor_generator.apply(tiles)
