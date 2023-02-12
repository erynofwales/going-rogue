# Eryn Wells <eryn@erynwells.me>

'''
Game configuration parameters.
'''

import os.path as osp
import re
from dataclasses import dataclass
from enum import Enum
from os import PathLike
from typing import Iterable

import tcod.tileset

from . import log
from .geometry import Size


CONSOLE_SIZE = Size(80, 50)
MAP_SIZE = Size(80, 45)
FONT_CP437 = 'terminal16x16_gs_ro.png'
FONT_BDF = 'ter-u32n.bdf'


class FontConfigurationError(Exception):
    '''Invalid font configration based on available parameters'''


@dataclass
class FontConfiguration:
    '''Configuration of the font to use for rendering the game'''

    filename: str | PathLike[str]

    @staticmethod
    def __find_fonts_directory():
        '''Walk up the filesystem tree from this file to find a `fonts` directory.'''

        def walk_up_directories_of_path(path):
            while path and path != '/':
                path = osp.dirname(path)
                yield path

        for parent_dir in walk_up_directories_of_path(__file__):
            possible_fonts_dir = osp.join(parent_dir, 'fonts')
            if osp.isdir(possible_fonts_dir):
                log.ROOT.info('Found fonts dir %s', possible_fonts_dir)
                break
        else:
            return None

        return possible_fonts_dir

    @staticmethod
    def default_configuration():
        '''Return a default configuration: a tilesheet font configuration using `fonts/terminal16x16_gs_ro.png`.'''

        fonts_directory = FontConfiguration.__find_fonts_directory()
        if not fonts_directory:
            message = "Couldn't find a fonts directory"
            log.ROOT.error('%s', message)
            raise FontConfigurationError(message)

        font = osp.join(fonts_directory, 'terminal16x16_gs_ro.png')
        if not osp.isfile(font):
            message = f"Font file {font} doesn't exist"
            log.ROOT.error("%s", message)
            raise FontConfigurationError(message)

        return FontConfiguration.with_filename(font)

    @staticmethod
    def with_filename(filename: str | PathLike[str]) -> 'FontConfiguration':
        '''Return a FontConfig subclass based on the path to the filename'''
        _, extension = osp.splitext(filename)

        match extension:
            case ".bdf":
                return BDFFontConfiguration(filename)
            case ".ttf":
                return TTFFontConfiguration(filename)
            case ".png":
                # Attempt to find the tilesheet dimensions in the filename.
                try:
                    match = re.match(r'^.*\(\d+\)x\(\d+\).*$', extension)
                    if not match:
                        return TilesheetFontConfiguration(filename)

                    rows, columns = int(match.group(1)), int(match.group(2))
                    return TilesheetFontConfiguration(
                        filename=filename,
                        dimensions=Size(columns, rows))
                except ValueError:
                    return TilesheetFontConfiguration(filename)
            case _:
                raise FontConfigurationError(f'Unable to determine font configuration from {filename}')

    @property
    def tileset(self) -> tcod.tileset.Tileset:
        '''Returns a tcod tileset based on the parameters of this font config'''
        raise NotImplementedError()


@dataclass
class BDFFontConfiguration(FontConfiguration):
    '''A font configuration based on a BDF file.'''

    @property
    def tileset(self) -> tcod.tileset.Tileset:
        return tcod.tileset.load_bdf(self.filename)


@dataclass
class TTFFontConfiguration(FontConfiguration):
    '''
    A font configuration based on a TTF file. Since TTFs are variable width, a fixed tile size needs to be specified.
    '''

    tile_size: Size = Size(16, 16)

    @property
    def tileset(self) -> tcod.tileset.Tileset:
        return tcod.tileset.load_truetype_font(self.filename, *self.tile_size)


@dataclass
class TilesheetFontConfiguration(FontConfiguration):
    '''
    Configuration for tilesheets. Unlike other font configurations, tilesheets must have their dimensions specified as
    the number of sprites per row and number of rows.
    '''

    class Layout(Enum):
        '''The layout of the tilesheet'''
        CP437 = 1
        TCOD = 2

    dimensions: Size = Size(16, 16)
    layout: Layout | Iterable[int] = Layout.CP437

    @property
    def tilesheet(self) -> Iterable[int]:
        '''A tilesheet mapping for the given layout'''
        if not self.layout:
            return tcod.tileset.CHARMAP_CP437

        if isinstance(self.layout, Iterable):
            return self.layout

        match self.layout:
            case TilesheetFontConfiguration.Layout.CP437:
                return tcod.tileset.CHARMAP_CP437
            case TilesheetFontConfiguration.Layout.TCOD:
                return tcod.tileset.CHARMAP_TCOD

    @property
    def tileset(self) -> tcod.tileset.Tileset:
        '''A tcod tileset with the given parameters'''
        return tcod.tileset.load_tilesheet(
            self.filename,
            self.dimensions.width,
            self.dimensions.height,
            self.tilesheet)


@dataclass
class Configuration:
    '''Configuration of the game engine'''
    console_size: Size
    console_font_config: FontConfiguration

    map_size: Size

    sandbox: bool = False
