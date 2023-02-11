# Eryn Wells <eryn@erynwells.me>

import argparse
import os.path
import sys
import tcod
from . import log
from .engine import Configuration, Engine
from .geometry import Size

CONSOLE_WIDTH, CONSOLE_HEIGHT = 80, 50
MAP_WIDTH, MAP_HEIGHT = 80, 45
FONT_CP437 = 'terminal16x16_gs_ro.png'
FONT_BDF = 'ter-u32n.bdf'


def parse_args(argv, *a, **kw):
    parser = argparse.ArgumentParser(*a, **kw)
    parser.add_argument('--debug', action='store_true', default=True)
    args = parser.parse_args(argv)
    return args


def walk_up_directories_of_path(path):
    while path and path != '/':
        path = os.path.dirname(path)
        yield path


def find_fonts_directory():
    '''Walk up the filesystem tree from this script to find a fonts/ directory.'''
    for parent_dir in walk_up_directories_of_path(__file__):
        possible_fonts_dir = os.path.join(parent_dir, 'fonts')
        if os.path.isdir(possible_fonts_dir):
            log.ROOT.info('Found fonts dir %s', possible_fonts_dir)
            break
    else:
        return None

    return possible_fonts_dir


def main(argv):
    '''
    Beginning of the game

    Parameters
    ----------
    argv : List[str]
        A standard argument list, most likely you'll get this from sys.argv
    '''
    args = parse_args(argv[1:], prog=argv[0])

    log.init()

    fonts_directory = find_fonts_directory()
    if not fonts_directory:
        log.ROOT.error("Couldn't find a fonts/ directory")
        return -1

    font = os.path.join(fonts_directory, FONT_BDF)
    if not os.path.isfile(font):
        log.ROOT.error("Font file %s doesn't exist", font)
        return -1

    tileset = tcod.tileset.load_bdf(font)
    console = tcod.Console(CONSOLE_WIDTH, CONSOLE_HEIGHT, order='F')

    configuration = Configuration(map_size=Size(MAP_WIDTH, MAP_HEIGHT))
    engine = Engine(configuration)

    with tcod.context.new(columns=console.width, rows=console.height, tileset=tileset) as context:
        engine.run_event_loop(context, console)


def run_until_exit():
    '''
    Run main() and call sys.exit when it finishes. In practice, this function will never return. The game engine has
    other mechanisms for exiting.
    '''
    result = main(sys.argv)
    sys.exit(0 if not result else result)


run_until_exit()
