# Eryn Wells <eryn@erynwells.me>

'''
Utilities for maps.
'''

import numpy as np

from .tile import Empty
from ..geometry import Size


def make_grid(size: Size, fill: np.ndarray = Empty) -> np.ndarray:
    '''Make a numpy array of the given size filled with `fill` tiles.'''
    return np.full(size.numpy_shape, fill_value=fill, order='F')
