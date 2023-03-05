# Eryn Wells <eryn@erynwells.me>

'''Main module'''

import argparse
import sys
import tcod
from . import log
from .configuration import Configuration, FontConfiguration, FontConfigurationError, MAP_SIZE, CONSOLE_SIZE
from .engine import Engine


def parse_args(argv, *a, **kw):
    parser = argparse.ArgumentParser(*a, **kw)
    parser.add_argument('--debug', action='store_true', default=True)
    parser.add_argument('--font')
    parser.add_argument('--sandbox', action='store_true', default=False)
    args = parser.parse_args(argv)
    return args


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

    try:
        font = args.font
        if font:
            font_config = FontConfiguration.with_filename(font)
        else:
            font_config = FontConfiguration.default_configuration()
    except FontConfigurationError as error:
        log.ROOT.error('Unable to create a font configuration: %s', error)
        return -1

    configuration = Configuration(
        console_font_configuration=font_config,
        sandbox=args.sandbox)

    engine = Engine(configuration)

    tileset = configuration.console_font_configuration.tileset
    console = tcod.Console(*configuration.console_size.numpy_shape, order='F')
    with tcod.context.new(columns=console.width, rows=console.height, tileset=tileset) as context:
        engine.run_event_loop(context, console)

    return 0


def run_until_exit():
    '''
    Run main() and call sys.exit when it finishes. In practice, this function will never return. The game engine has
    other mechanisms for exiting.
    '''
    result = main(sys.argv)
    sys.exit(0 if not result else result)


run_until_exit()
