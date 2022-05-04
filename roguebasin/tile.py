#!/usr/bin/env python3
# Eryn Wells <eryn@erynwells.me>

import numpy as np
from typing import Tuple

graphic_datatype = np.dtype([
    # Character, a Unicode codepoint represented as an int32
    ('ch', np.int32),
    # Foreground color, three bytes
    ('fg', '3B'),
    # Background color, three bytes
    ('bg', '3B'),
])

tile_datatype = np.dtype([
    # Bool indicating whether this tile can be traversed
    ('walkable', np.bool),
    # Bool indicating whether this tile is transparent
    ('transparent', np.bool),
    # A graphic struct (as above) defining the look of this tile when it's not visible
    ('dark', graphic_datatype),
    # A graphic struct (as above) defining the look of this tile when it's visible
    ('light', graphic_datatype),
])

def tile(*,
         walkable: int,
         transparent: int,
         dark: Tuple[int, Tuple[int, int, int], Tuple[int, int ,int]],
         light: Tuple[int, Tuple[int, int, int], Tuple[int, int ,int]]) -> np.ndarray:
    return np.array((walkable, transparent, dark, light), dtype=tile_datatype)

# An overlay color for tiles that are not visible and have not been explored
Shroud = np.array((ord(' '), (255, 255, 255), (0, 0, 0)), dtype=graphic_datatype)

Empty = tile(walkable=False, transparent=False,
             dark=(ord(' '), (255, 255, 255), (0, 0, 0)),
             light=(ord(' '), (255, 255, 255), (0, 0, 0)))
Floor = tile(walkable=True, transparent=True,
             dark=(ord('·'), (80, 80, 100), (50, 50, 50)),
             light=(ord('·'), (100, 100, 120), (80, 80, 100)))
Wall = tile(walkable=False, transparent=False,
            dark=(ord(' '), (255, 255, 255), (0, 0, 150)),
            light=(ord(' '), (255, 255, 255), (50, 50, 200)))