from typing import Iterator

from ..geometry import Point, Rect


class Room:
    '''An abstract room. It can be any size or shape.'''

    def __init__(self, bounds):
        self.bounds = bounds

    @property
    def center(self) -> Point:
        '''The center of the room, truncated according to integer math rules'''
        return self.bounds.midpoint

    @property
    def walls(self) -> Iterator[Point]:
        '''An iterator over all the wall tiles of this room.'''
        raise NotImplementedError()

    @property
    def walkable_tiles(self) -> Iterator[Point]:
        '''An iterator over all the walkable tiles in this room.'''
        raise NotImplementedError()


class RectangularRoom(Room):
    '''A rectangular room defined by a Rect.

    Attributes
    ----------
    bounds : Rect
        A rectangle that defines the room. This rectangle includes the tiles used for the walls, so the floor is 1 tile
        inset from the bounds.
    '''

    @property
    def walkable_tiles(self) -> Iterator[Point]:
        floor_rect = self.bounds.inset_rect(top=1, right=1, bottom=1, left=1)
        for y in range(floor_rect.min_y, floor_rect.max_y + 1):
            for x in range(floor_rect.min_x, floor_rect.max_x + 1):
                yield Point(x, y)

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
