# Eryn Wells <eryn@erynwells.me>

from typing import Optional, TYPE_CHECKING

import tcod
import tcod.event as tev

from .actions.action import Action
from .actions.game import BumpAction, ExitAction, RegenerateRoomsAction, WaitAction
from .geometry import Direction

if TYPE_CHECKING:
    from .engine import Engine


class EngineEventHandler(tev.EventDispatch[Action]):
    '''Handles event on behalf of the game engine, dispatching Actions back to the engine.'''

    def __init__(self, engine: 'Engine'):
        super().__init__()
        self.engine = engine

    def ev_keydown(self, event: tev.KeyDown) -> Optional[Action]:
        action: Optional[Action] = None

        hero = self.engine.hero

        is_shift_pressed = bool(event.mod & tcod.event.Modifier.SHIFT)

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
            case tcod.event.KeySym.SPACE:
                action = RegenerateRoomsAction()
            case tcod.event.KeySym.PERIOD:
                if not is_shift_pressed:
                    action = WaitAction(hero)

        return action

    def ev_quit(self, event: tcod.event.Quit) -> Optional[Action]:
        return ExitAction()


class GameOverEventHandler(tev.EventDispatch[Action]):
    '''When the game is over (the hero dies, the player quits, etc), this event handler takes over.'''

    def __init__(self, engine: 'Engine'):
        super().__init__()
        self.engine = engine

    def ev_quit(self, event: tev.Quit) -> Optional[Action]:
        return ExitAction()
