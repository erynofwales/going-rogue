# Eryn Wells <eryn@erynwells.me>

'''
Initializes and sets up
'''

import json
import logging
import logging.config
import os.path

# These are re-imports so clients of this module don't have to also import logging
# pylint: disable=unused-import
from logging import CRITICAL, DEBUG, ERROR, FATAL, INFO, NOTSET, WARN, WARNING


def _log_name(*components):
    return '.'.join(['erynrl'] + list(components))


ROOT = logging.getLogger(_log_name())
AI = logging.getLogger(_log_name('ai'))
ACTIONS = logging.getLogger(_log_name('actions'))
ACTIONS_TREE = logging.getLogger(_log_name('actions', 'tree'))
ENGINE = logging.getLogger(_log_name('engine'))
EVENTS = logging.getLogger(_log_name('events'))
MAP = logging.getLogger(_log_name('map'))
UI = logging.getLogger(_log_name('ui'))


def walk_up_directories_of_path(path):
    '''Walk up a path, yielding each directory, until the root of the filesystem is found'''
    while path and path != '/':
        if os.path.isdir(path):
            yield path
        path = os.path.dirname(path)


def find_logging_config():
    '''Walk up the filesystem from this script to find a logging_config.json'''
    for parent_dir in walk_up_directories_of_path(__file__):
        possible_logging_config_file = os.path.join(parent_dir, 'logging_config.json')
        if os.path.isfile(possible_logging_config_file):
            ROOT.info('Found logging config file %s', possible_logging_config_file)
            break
    else:
        return None

    return possible_logging_config_file


def init(config_file=None):
    '''
    Set up the logging system by (preferrably) reading a logging configuration file.

    Parameters
    ----------
    config_file : str
        Path to a file containing a Python logging configuration in JSON
    '''
    logging_config_path = config_file if config_file else find_logging_config()

    if os.path.isfile(logging_config_path):
        with open(logging_config_path, encoding='utf-8') as logging_config_file:
            logging_config = json.load(logging_config_file)
            logging.config.dictConfig(logging_config)
        ROOT.info('Found logging configuration at %s', logging_config_path)
    else:
        root_logger = logging.getLogger('')
        root_logger.setLevel(logging.DEBUG)

        stderr_handler = logging.StreamHandler()
        stderr_handler.setFormatter(logging.Formatter("%(asctime)s %(name)s: %(message)s"))

        root_logger.addHandler(stderr_handler)
