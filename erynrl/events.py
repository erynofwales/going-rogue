# Eryn Wells <eryn@erynwells.me>

'''Defines event handling mechanisms.'''

from typing import Optional, TYPE_CHECKING

import tcod

from . import log
from .actions import Action, ExitAction, RegenerateRoomsAction, BumpAction, WaitAction
from .geometry import Direction

if TYPE_CHECKING:
    from .engine import Engine

class EventHandler(tcod.event.EventDispatch[Action]):
    '''Handler of `tcod` events'''

    def __init__(self, engine: 'Engine'):
        super().__init__()
        self.engine = engine

    def wait_for_events(self):
        '''Wait for events and handle them.'''
        for event in tcod.event.wait():
            self.handle_event(event)

    def handle_event(self, event: tcod.event.Event) -> None:
        '''Handle the given event. Transform that event into an Action via an EventHandler and perform it.'''
        action = self.dispatch(event)

        # Unhandled event. Ignore it.
        if not action:
            log.EVENTS.debug('Unhandled event: %s', event)
            return

        result = self.engine.process_hero_action(action)

        # Player's action failed, don't proceed with turn.
        if not result.success and result.done:
            return

        self.engine.process_entity_actions()
        self.engine.update_field_of_view()

    def ev_quit(self, event: tcod.event.Quit) -> Optional[Action]:
        return ExitAction(self.engine.hero)

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[Action]:
        action: Optional[Action] = None

        hero = self.engine.hero

        sym = event.sym
        match sym:
            case tcod.event.KeySym.b:
                action = BumpAction(hero, Direction.SouthWest)
            case tcod.event.KeySym.h:
                action = BumpAction(hero, Direction.West)
            case tcod.event.KeySym.j:
                action = BumpAction(hero, Direction.South)
            case tcod.event.KeySym.k:
                action = BumpAction(hero, Direction.North)
            case tcod.event.KeySym.l:
                action = BumpAction(hero, Direction.East)
            case tcod.event.KeySym.n:
                action = BumpAction(hero, Direction.SouthEast)
            case tcod.event.KeySym.u:
                action = BumpAction(hero, Direction.NorthEast)
            case tcod.event.KeySym.y:
                action = BumpAction(hero, Direction.NorthWest)
            case tcod.event.KeySym.ESCAPE:
                action = ExitAction(hero)
            case tcod.event.KeySym.SPACE:
                action = RegenerateRoomsAction(hero)
            case tcod.event.KeySym.PERIOD:
                action = WaitAction(hero)

        return action
