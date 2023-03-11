# Eryn Wells <eryn@erynwells.me>

'''
The game's graphical user interface
'''

from typing import NoReturn

from tcod import event as tev
from tcod.console import Console
from tcod.context import Context

from .events import InterfaceEventHandler
from .window.info import InfoWindow
from .window.map import MapWindow
from .window.message_log import MessageLogWindow
from ..engine import Engine
from ..geometry import Rect, Size


class Interface:
    '''The game's user interface'''

    def __init__(self, size: Size, engine: Engine):
        self.engine = engine

        self.console = Console(*size.numpy_shape, order='F')

        self.map_window = MapWindow(
            Rect.from_raw_values(0, 0, size.width, size.height - 5),
            engine.map,
            engine.hero)
        self.info_window = InfoWindow(
            Rect.from_raw_values(0, size.height - 5, 28, 5))
        self.message_window = MessageLogWindow(
            Rect.from_raw_values(28, size.height - 5, size.width - 28, 5),
            engine.message_log)

        self.event_handler = InterfaceEventHandler(self)

    def update(self):
        '''Update game state that the interface needs to render'''
        self.info_window.turn_count = self.engine.current_turn

        hero = self.engine.hero
        self.info_window.update_hero(hero)

        sorted_entities = sorted(filter(lambda e: e.renderable is not None, self.engine.entities),
                                 key=lambda e: e.renderable.order.value)
        self.map_window.entities = sorted_entities

    def draw(self):
        '''Draw the UI to the console'''
        self.map_window.draw(self.console)
        self.info_window.draw(self.console)
        self.message_window.draw(self.console)

    def run_event_loop(self, context: Context) -> NoReturn:
        '''Run the event loop forever. This method never returns.'''
        while True:
            self.update()

            self.console.clear()
            self.draw()
            context.present(self.console)

            for event in tev.wait():
                context.convert_event(event)
                did_handle = self.event_handler.dispatch(event)
                if did_handle:
                    continue

                action = self.engine.event_handler.dispatch(event)
                if not action:
                    # The engine didn't handle the event, so just drop it.
                    continue

                self.engine.process_input_action(action)
