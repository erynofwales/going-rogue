#!/usr/bin/env python3
# Eryn Wells <eryn@erynwells.me>

import tcod
from typing import Optional

class Tile:
    class Color:
        WALL = tcod.Color(255, 255, 255)
        GROUND = tcod.Color(33, 33, 33)

    def __init__(self, blocks_movement: bool, blocks_sight: Optional[bool] = None):
        self.blocks_movement = blocks_movement

        # If blocks_sight isn't explicitly given, tiles that block movement also block sight.
        if blocks_sight is None:
            self.blocks_sight = blocks_movement
        else:
            self.blocks_sight = blocks_sight