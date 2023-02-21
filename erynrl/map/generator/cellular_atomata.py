# Eryn Wells <eryn@erynwells.me>

import random
from dataclasses import dataclass
from typing import Optional

import numpy as np

from ... import log
from ...geometry import Point, Rect
from ..grid import make_grid
from ..tile import Floor, Wall


class CellularAtomataMapGenerator:
    '''
    A map generator that utilizes a cellular atomaton to place floors and walls.
    '''

    @dataclass
    class Configuration:
        '''
        Configuration of a cellular atomaton map generator.

        ### Attributes
        `fill_percentage` : `float`
            The percentage of tiles to fill with Floor when the map is seeded.
        `number_of_rounds` : `int`
            The number of rounds to run the atomaton. 5 is a good default. More
            rounds results in smoother output; fewer rounds results in more
            jagged, random output.
        '''
        fill_percentage: float = 0.5
        number_of_rounds: int = 5

    def __init__(self, bounds: Rect, config: Optional[Configuration] = None):
        '''
        Initializer

        ### Parameters
        `bounds` : `Rect`
            A rectangle representing the bounds of the cellular atomaton
        `config` : `Optional[Configuration]`
            A configuration object specifying parameters for the atomaton. If
            None, the instance will use a default configuration.
        '''
        self.bounds = bounds
        self.configuration = config if config else CellularAtomataMapGenerator.Configuration()
        self.tiles = make_grid(bounds.size)

    def generate(self):
        '''
        Run the cellular atomaton on a grid of `self.bounds.size` shape.

        First fill the grid with random Floor and Wall tiles according to
        `self.configuration.fill_percentage`, then run the simulation for
        `self.configuration.number_of_rounds` rounds.
        '''
        self._fill()
        self._run_atomaton()

    def _fill(self):
        fill_percentage = self.configuration.fill_percentage

        for y, x in np.ndindex(self.tiles.shape):
            self.tiles[x, y] = Floor if random.random() < fill_percentage else Wall

    def _run_atomaton(self):
        alternate_tiles = make_grid(self.bounds.size)

        number_of_rounds = self.configuration.number_of_rounds
        if number_of_rounds < 1:
            raise ValueError('Refusing to run cellular atomaton for less than 1 round')

        log.MAP_CELL_ATOM.info(
            'Running cellular atomaton over %s for %d round%s',
            self.bounds,
            number_of_rounds,
            '' if number_of_rounds == 1 else 's')

        for i in range(number_of_rounds):
            if i % 2 == 0:
                from_tiles = self.tiles
                to_tiles = alternate_tiles
            else:
                from_tiles = alternate_tiles
                to_tiles = self.tiles

            self._do_round(from_tiles, to_tiles)

        # If we ended on a round where alternate_tiles was the "to" tile grid
        # above, save it back to self.tiles.
        if number_of_rounds % 2 == 0:
            self.tiles = alternate_tiles

    def _do_round(self, from_tiles: np.ndarray, to_tiles: np.ndarray):
        for y, x in np.ndindex(from_tiles.shape):
            pt = Point(x, y)

            # Start with 1 because the point is its own neighbor
            number_of_neighbors = 1
            for neighbor in pt.neighbors:
                if neighbor not in self.bounds:
                    continue

                if from_tiles[neighbor.x, neighbor.y] == Floor:
                    number_of_neighbors += 1

            tile_is_alive = from_tiles[pt.x, pt.y] == Floor
            if tile_is_alive and number_of_neighbors >= 5:
                # Survival
                to_tiles[pt.x, pt.y] = Floor
            elif not tile_is_alive and number_of_neighbors >= 5:
                # Birth
                to_tiles[pt.x, pt.y] = Floor
            else:
                to_tiles[pt.x, pt.y] = Wall

    def __str__(self):
        return '\n'.join(''.join(chr(i['light']['ch']) for i in row) for row in self.tiles)
