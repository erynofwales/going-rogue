# Eryn Wells <eryn@erynwells.me>

import numpy as np

from .tile import Empty
from ..geometry import Size


def make_grid(size: Size):
    return np.full(size.numpy_shape, fill_value=Empty, order='F')
