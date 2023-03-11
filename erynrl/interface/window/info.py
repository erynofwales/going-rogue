# Eryn Wells <eryn@erynwells.me>

'''
Declares the InfoWindow.
'''

from tcod.console import Console

from . import Window
from ..color import HealthBar
from ..percentage_bar import PercentageBar
from ...geometry import Point, Rect
from ...object import Hero


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

    def draw(self, console: Console):
        super().draw(console)

        drawable_bounds = self.drawable_bounds
        console.print(x=drawable_bounds.min_x + 2, y=drawable_bounds.min_y, string='HP:')
        self.hit_points_bar.render_to_console(console)

        if self.turn_count:
            console.print(x=drawable_bounds.min_x, y=drawable_bounds.min_y + 1, string=f'Turn: {self.turn_count}')
