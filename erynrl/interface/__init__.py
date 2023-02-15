# Eryn Wells <eryn@erynwells.me>

'''
The game's graphical user interface
'''

from typing import List

from tcod.console import Console

from .color import HealthBar
from .percentage_bar import PercentageBar
from .window import Window, MapWindow
from ..geometry import Point, Rect, Size
from ..map import Map
from ..messages import MessageLog
from ..object import Entity, Hero


class Interface:
    '''The game's user interface'''

    # pylint: disable=redefined-builtin
    def __init__(self, size: Size, map: Map, message_log: MessageLog):
        self.map_window = MapWindow(Rect(Point(0, 0), Size(size.width, size.height - 5)), map)
        self.info_window = InfoWindow(Rect(Point(0, size.height - 5), Size(28, 5)))
        self.message_window = MessageLogWindow(Rect(Point(28, size.height - 5), Size(size.width - 28, 5)), message_log)

    def update(self, turn_count: int, hero: Hero, entities: List[Entity]):
        '''Update game state that the interface needs to render'''
        self.info_window.turn_count = turn_count
        self.info_window.update_hero(hero)

        self.map_window.update_drawable_map_bounds(hero)
        self.map_window.entities = entities

    def draw(self, console: Console):
        '''Draw the UI to the console'''
        self.map_window.draw(console)
        self.info_window.draw(console)
        self.message_window.draw(console)


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
