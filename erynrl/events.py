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
    '''Abstract event handler class'''

    def __init__(self, engine: 'Engine'):
        super().__init__()
        self.engine = engine

    def wait_for_events(self):
        '''Wait for events and handle them.'''
        for event in tcod.event.wait():
            self.handle_event(event)

    def handle_event(self, event: tcod.event.Event) -> None:
        '''
        Handle an event by transforming it into an Action and processing it until it is completed. If the Action
        succeeds, also process actions from other Entities.

        Parameters
        ----------
        event : tcod.event.Event
            The event to handle
        '''
        action = self.dispatch(event)

        # Unhandled event. Ignore it.
        if not action:
            log.EVENTS.debug('Unhandled event: %s', event)
            return

        self.engine.process_input_action(action)

    def ev_quit(self, event: tcod.event.Quit) -> Optional[Action]:
        return ExitAction(self.engine.hero)

class MainGameEventHandler(EventHandler):
    '''
    Handler of `tcod` events for the main game.

    Receives input from the player and dispatches actions to the game engine to interat with the hero and other objects
    in the game.
    '''

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

class GameOverEventHandler(EventHandler):
    '''When the game is over (the hero dies, the player quits, etc), this event handler takes over.'''

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[Action]:
        action: Optional[Action] = None

        hero = self.engine.hero

        sym = event.sym
        match sym:
            case tcod.event.KeySym.ESCAPE:
                action = ExitAction(hero)

        return action