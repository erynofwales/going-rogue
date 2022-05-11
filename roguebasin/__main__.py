# Eryn Wells <eryn@erynwells.me>

import argparse
import json
import logging
import logging.config
import os.path
import sys
import tcod
from .engine import Configuration, Engine
from .events import EventHandler
from .geometry import Size

LOG = logging.getLogger('main')

CONSOLE_WIDTH, CONSOLE_HEIGHT = 80, 50
MAP_WIDTH, MAP_HEIGHT = 80, 45

FONT = 'terminal16x16_gs_ro.png'

def parse_args(argv, *a, **kw):
    parser = argparse.ArgumentParser(*a, **kw)
    parser.add_argument('--debug', action='store_true', default=True)
    args = parser.parse_args(argv)
    return args

def init_logging(args):
    '''Set up the logging system by (preferrably) reading a logging configuration file.'''
    logging_config_path = find_logging_config()
    if logging_config_path:
        with open(logging_config_path, encoding='utf-8') as logging_config_file:
            logging_config = json.load(logging_config_file)
            logging.config.dictConfig(logging_config)
        LOG.info('Found logging configuration at %s', logging_config_path)
    else:
        root_logger = logging.getLogger('')
        root_logger.setLevel(logging.DEBUG if args.debug else logging.INFO)

        stderr_handler = logging.StreamHandler()
        stderr_handler.setFormatter(logging.Formatter("%(asctime)s %(name)s: %(message)s"))

        root_logger.addHandler(stderr_handler)

def walk_up_directories_of_path(path):
    while path and path != '/':
        path = os.path.dirname(path)
        yield path

def find_fonts_directory():
    '''Walk up the filesystem tree from this script to find a fonts/ directory.'''
    for parent_dir in walk_up_directories_of_path(__file__):
        possible_fonts_dir = os.path.join(parent_dir, 'fonts')
        if os.path.isdir(possible_fonts_dir):
            LOG.info('Found fonts dir %s', possible_fonts_dir)
            break
    else:
        return None

    return possible_fonts_dir

def find_logging_config():
    '''Walk up the filesystem from this script to find a logging_config.json'''
    for parent_dir in walk_up_directories_of_path(__file__):
        possible_logging_config_file = os.path.join(parent_dir, 'logging_config.json')
        if os.path.isfile(possible_logging_config_file):
            LOG.info('Found logging config file %s', possible_logging_config_file)
            break
    else:
        return None

    return possible_logging_config_file

def main(argv):
    args = parse_args(argv[1:], prog=argv[0])

    init_logging(args)

    fonts_directory = find_fonts_directory()
    if not fonts_directory:
        LOG.error("Couldn't find a fonts/ directory")
        return -1

    font = os.path.join(fonts_directory, FONT)
    if not os.path.isfile(font):
        LOG.error("Font file %s doesn't exist", font)
        return -1

    tileset = tcod.tileset.load_tilesheet(font, 16, 16, tcod.tileset.CHARMAP_CP437)
    console = tcod.Console(CONSOLE_WIDTH, CONSOLE_HEIGHT, order='F')

    configuration = Configuration(map_size=Size(MAP_WIDTH, MAP_HEIGHT))
    engine = Engine(configuration)
    event_handler = EventHandler(engine)

    with tcod.context.new(columns=console.width, rows=console.height, tileset=tileset) as context:
        while True:
            console.clear()
            engine.print_to_console(console)
            context.present(console)

            event_handler.wait_for_events()

def run_until_exit():
    '''
    Run main() and call sys.exit when it finishes. In practice, this function will never return. The game engine has
    other mechanisms for exiting.
    '''
    result = main(sys.argv)
    sys.exit(0 if not result else result)

run_until_exit()
