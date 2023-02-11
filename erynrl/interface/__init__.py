# Eryn Wells <eryn@erynwells.me>

from typing import Optional

from tcod.console import Console

from .color import HealthBar
from .percentage_bar import PercentageBar
from .window import Window
from ..geometry import Point, Rect, Size
from ..map import Map
from ..messages import MessageLog
from ..object import Hero


class Interface:
    def __init__(self, size: Size, map: Map, message_log: MessageLog):
        self.map_window = MapWindow(Rect(Point(0, 0), Size(size.width, size.height - 5)), map)
        self.info_window = InfoWindow(Rect(Point(0, size.height - 5), Size(28, 5)))
        self.message_window = MessageLogWindow(Rect(Point(28, size.height - 5), Size(size.width - 28, 5)), message_log)

    def update(self, hero: Hero, turn_count: int):
        self.info_window.turn_count = turn_count
        self.info_window.update_hero(hero)

    def draw(self, console: Console):
        self.map_window.draw(console)
        self.info_window.draw(console)
        self.message_window.draw(console)


class MapWindow(Window):
    def __init__(self, bounds: Rect, map: Map):
        super().__init__(bounds)
        self.map = map

    def draw(self, console):
        super().draw(console)

        # TODO: Get a 2D slice of tiles from the map given a rect based on the window's drawable area
        drawable_area = self.drawable_area
        self.map.print_to_console(console, drawable_area)


class InfoWindow(Window):
    def __init__(self, bounds: Rect):
        super().__init__(bounds, framed=True)

        self.turn_count: int = 0

        drawable_area = self.drawable_area
        self.hit_points_bar = PercentageBar(
            position=Point(drawable_area.min_x + 6, drawable_area.min_y),
            width=20,
            colors=list(HealthBar.bar_colors()))

    def update_hero(self, hero: Hero):
        hp, max_hp = hero.fighter.hit_points, hero.fighter.maximum_hit_points
        self.hit_points_bar.percent_filled = hp / max_hp

    def draw(self, console):
        super().draw(console)

        drawable_area = self.drawable_area
        console.print(x=drawable_area.min_x + 2, y=drawable_area.min_y, string='HP:')
        self.hit_points_bar.render_to_console(console)

        if self.turn_count:
            console.print(x=drawable_area.min_x, y=drawable_area.min_y + 1, string=f'Turn: {self.turn_count}')


class MessageLogWindow(Window):
    def __init__(self, bounds: Rect, message_log: MessageLog):
        super().__init__(bounds, framed=True)
        self.message_log = message_log

    def draw(self, console):
        super().draw(console)
        self.message_log.render_to_console(console, self.drawable_area)
