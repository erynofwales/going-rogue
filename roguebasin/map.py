#!/usr/bin/env python3
# Eryn Wells <eryn@erynwells.me>

import logging
import numpy as np
import tcod
from .geometry import Point, Rect, Size
from .tile import Floor, Wall
from typing import List

LOG = logging.getLogger('map')

class Map:
    def __init__(self, size: Size):
        self.size = size

        self.tiles = np.full(self.size.as_tuple, fill_value=Floor, order="F")

        self.rng = tcod.random.Random()

        # BSP partitions
        self.partitions = list(self.generate_partitions())
        # Rooms, which are always some small portion of the above partitions.
        self.rooms: List[Rect] = self.generate_rooms(self.partitions)

        self.update_tiles()

    def tile_is_in_bounds(self, point: Point) -> bool:
        return 0 <= point.x < self.size.width and 0 <= point.y < self.size.height

    def tile_is_walkable(self, point: Point) -> bool:
        return self.tiles[point.x, point.y]['walkable']

    def generate_partitions(self):
        bsp = tcod.bsp.BSP(x=0, y=0, width=self.size.width, height=self.size.height)
        # TODO: Parameterize this. Maybe a MapConfiguration class?
        bsp.split_recursive(
            depth=4,
            min_width=8, min_height=8,
            max_horizontal_ratio=1.5, max_vertical_ratio=1.5)
        return bsp.pre_order()

    def generate_rooms(self, partitions):
        rooms = []

        # For nicer debug logging
        indent = 0

        for node in partitions:
            if node.children:
                if LOG.getEffectiveLevel() == logging.DEBUG:
                    LOG.debug(f'{" " * indent}{Rect(node.x, node.y, node.width, node.height)}')
                    indent += 2
                # TODO: Connect the two child rooms
            else:
                LOG.debug(f'{" " * indent}{Rect(node.x, node.y, node.width, node.height)} (room)')
                size = Size(self.rng.randint(5, min(15, max(5, node.width - 2))),
                            self.rng.randint(5, min(15, max(5, node.height - 2))))
                origin = Point(node.x + self.rng.randint(1, max(1, node.width - size.width - 1)),
                            node.y + self.rng.randint(1, max(1, node.height - size.height - 1)))
                room = Rect(origin.x, origin.y, size.width, size.height)
                LOG.debug(f'{" " * indent}`-> {room}')

                rooms.append(room)

                if LOG.getEffectiveLevel() == logging.DEBUG:
                    indent -= 2

        return rooms

    def update_tiles(self):
        # Fill the whole map with walls
        width, height = self.size.as_tuple
        self.tiles[0:width, 0:height] = Wall

        # Dig out rooms
        for room in self.rooms:
            for y in range(room.min_y, room.max_y + 1):
                for x in range(room.min_x, room.max_x + 1):
                    self.tiles[x, y] = Floor

    def print_to_console(self, console: tcod.Console) -> None:
        # for part in self.partitions:
        #     console.draw_frame(part.x, part.y, part.width, part.height, bg=(40, 40, 80), clear=True, decoration="···· ····")

        # for room in self.rooms:
        #     console.draw_frame(room.origin.x, room.origin.y, room.size.width, room.size.height,
        #         fg=(255, 255, 255), bg=(80, 40, 40), clear=True)

        size = self.size
        console.tiles_rgb[0:size.width, 0:size.height] = self.tiles["dark"]