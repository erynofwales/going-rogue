# Eryn Wells <eryn@erynwels.me>

'''
Implements an abstract Room class, and subclasses that implement it. Rooms are basic components of maps.
'''



class Room:
    '''An abstract room. It can be any size or shape.'''

    def __init__(self, bounds: Rect):
        self.bounds: Rect = bounds

    @property
    def center(self) -> Point:
        '''The center of the room, truncated according to integer math rules'''
        return self.bounds.midpoint

    @property
    def wall_points(self) -> Iterator[Point]:
        '''An iterator over all the points that make up the walls of this room.'''
        raise NotImplementedError()

    @property
    def floor_points(self) -> Iterator[Point]:
        '''An iterator over all the points that make of the floor of this room'''
        raise NotImplementedError()

    @property
    def walkable_tiles(self) -> Iterator[Point]:
        '''An iterator over all the points that are walkable in this room.'''
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
    def wall_points(self) -> Iterator[Point]:
        bounds = self.bounds

        min_y = bounds.min_y
        max_y = bounds.max_y
        min_x = bounds.min_x
        max_x = bounds.max_x

        for x in range(min_x, max_x + 1):
            yield Point(x, min_y)
            yield Point(x, max_y)

        for y in range(min_y + 1, max_y):
            yield Point(min_x, y)
            yield Point(max_x, y)

    @property
    def floor_points(self) -> Iterator[Point]:
        inset_bounds = self.bounds.inset_rect(1, 1, 1, 1)

        min_y = inset_bounds.min_y
        max_y = inset_bounds.max_y
        min_x = inset_bounds.min_x
        max_x = inset_bounds.max_x

        for x in range(min_x, max_x + 1):
            for y in range(min_y, max_y + 1):
                yield Point(x, y)

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.bounds})'
