# Eryn Wells <eryn@erynwells.me>

'''
The game's graphical user interface
'''

from typing import NoReturn

from tcod import event as tev
from tcod.console import Console
from tcod.context import Context

from .color import HealthBar
from .events import InterfaceEventHandler
from .percentage_bar import PercentageBar
from .window import Window, MapWindow
from ..engine import Engine
from ..geometry import Point, Rect, Size
from ..messages import MessageLog
from ..object import Entity, Hero


class Interface:
    '''The game's user interface'''

    def __init__(self, size: Size, engine: Engine):
        self.engine = engine

        self.console = Console(*size.numpy_shape, order='F')

        self.map_window = MapWindow(
            Rect.from_raw_values(0, 0, size.width, size.height - 5),
            engine.map)
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
        self.map_window.update_drawable_map_bounds(hero)

        sorted_entities = sorted(self.engine.entities, key=lambda e: e.render_order.value)
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
                did_handle = self.event_handler.dispatch(event)
                if did_handle:
                    continue

                action = self.engine.event_handler.dispatch(event)
                if not action:
                    # The engine didn't handle the event, so just drop it.
                    continue

                self.engine.process_input_action(action)


class InfoWindow(Window):
    '''A window that displays information about the player'''

    def __init__(self, bounds: Rect):
        super().__init__(bounds, framed=True)

        self.turn_count: int = 0

        drawable_area = self.drawable_bounds
        self.hit_points_bar = PercentageBar(
            position=Point(drawable_area.min_x + 6, drawable_area.min_y),
            width=20,
            colors=list(HealthBar.bar_colors()))

    def update_hero(self, hero: Hero):
        '''Update internal state for the hero'''
        assert hero.fighter

        fighter = hero.fighter
        hp, max_hp = fighter.hit_points, fighter.maximum_hit_points

        self.hit_points_bar.percent_filled = hp / max_hp

    def draw(self, console):
        super().draw(console)

        drawable_bounds = self.drawable_bounds
        console.print(x=drawable_bounds.min_x + 2, y=drawable_bounds.min_y, string='HP:')
        self.hit_points_bar.render_to_console(console)

        if self.turn_count:
            console.print(x=drawable_bounds.min_x, y=drawable_bounds.min_y + 1, string=f'Turn: {self.turn_count}')


class MessageLogWindow(Window):
    '''A window that displays a list of messages'''

    def __init__(self, bounds: Rect, message_log: MessageLog):
        super().__init__(bounds, framed=True)
        self.message_log = message_log

    def draw(self, console):
        super().draw(console)
        self.message_log.render_to_console(console, self.drawable_bounds)
