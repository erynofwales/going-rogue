#!/usr/bin/env python3
# Eryn Wells <eryn@erynwells.me>

'''This module defines all of the actions that can be performed by the game. These actions can come from the player
(e.g. via keyboard input), or from non-player entities (e.g. AI deciboard input), or from non-player entities (e.g. AI
decisions).

Class Hierarchy
---------------

Action : Base class of all actions
    MoveAction : Base class for all actions that are performed with a direction
        WalkAction
        MeleeAction
    ExitAction
'''

import logging
from typing import Optional, TYPE_CHECKING
from .geometry import Direction
from .object import Entity

if TYPE_CHECKING:
    from .engine import Engine

LOG = logging.getLogger('events')

class ActionResult:
    '''The result of an Action.

    `Action.perform()` returns an instance of this class to inform the caller of the result

    Attributes
    ----------
    action : Action
        The Action that was performed
    success : bool, optional
        True if the action succeeded
    done : bool, optional
        True if the action is complete, and no follow-up action is needed
    alternate : Action, optional
        An alternate action to perform if this action failed
    '''

    def __init__(self, action: 'Action', *,
                 success: Optional[bool] = None,
                 done: Optional[bool] = None,
                 alternate: Optional['Action'] = None):
        self.action = action
        self.alternate = alternate

        if success is not None:
            self.success = success
        elif alternate:
            self.success = False
        else:
            self.success = True

        if done is not None:
            self.done = done
        elif self.success:
            self.done = True
        else:
            self.done = not alternate

    def __repr__(self):
        return f'{self.__class__.__name__}({self.action}, success={self.success}, done={self.done}, alternate={self.alternate})'

class Action:
    '''An action that an Entity should perform.'''

    def perform(self, engine: 'Engine', entity: Entity) -> ActionResult:
        '''Perform this action.

        Parameters
        ----------
        engine : Engine
            The game engine
        entity : Entity
            The entity that this action is being performed on

        Returns
        -------
        ActionResult
            A result object reflecting how the action was handled, and what follow-up actions, if any, are needed to
            complete the action.
        '''
        raise NotImplementedError()

    def __repr__(self):
        return f'{self.__class__.__name__}()'

class ExitAction(Action):
    '''Exit the game.'''

    def perform(self, engine: 'Engine', entity: Entity) -> ActionResult:
        raise SystemExit()

class RegenerateRoomsAction(Action):
    '''Regenerate the dungeon map'''

    def perform(self, engine: 'Engine', entity: Entity) -> ActionResult:
        return ActionResult(self, success=False)

# pylint: disable=abstract-method
class MoveAction(Action):
    '''An abstract Action that requires a direction to complete.'''

    def __init__(self, direction: Direction):
        super().__init__()
        self.direction = direction

    def __repr__(self):
        return f'{self.__class__.__name__}({self.direction})'

class BumpAction(MoveAction):
    '''Attempt to perform a movement action in a direction.

    This action tests if an action in the direction is possible and returns the action that can be completed.

    Attributes
    ----------
    direction : Direction
        The direction to test
    '''

    def perform(self, engine: 'Engine', entity: Entity) -> ActionResult:
        new_position = entity.position + self.direction

        position_is_in_bounds = engine.map.tile_is_in_bounds(new_position)
        position_is_walkable = engine.map.tile_is_walkable(new_position)

        for ent in engine.entities:
            if new_position != ent.position:
                continue
            entity_occupying_position = ent
            break
        else:
            entity_occupying_position = None

        LOG.info('Bumping %s (in_bounds:%s walkable:%s overlaps:%s)',
                 new_position,
                 position_is_in_bounds,
                 position_is_walkable,
                 entity_occupying_position)

        if not position_is_in_bounds or not position_is_walkable:
            return ActionResult(self, success=False)

        if entity_occupying_position:
            return ActionResult(self, alternate=MeleeAction(self.direction, entity_occupying_position))

        return ActionResult(self, alternate=WalkAction(self.direction))


class WalkAction(MoveAction):
    '''Walk one step in the given direction.'''

    def perform(self, engine: 'Engine', entity: Entity) -> ActionResult:
        new_position = entity.position + self.direction

        LOG.info('Moving %s to %s', entity, new_position)
        entity.position = new_position

        return ActionResult(self, success=True)

class MeleeAction(MoveAction):
    '''Perform a melee attack on another entity'''

    def __init__(self, direction: Direction, target: Entity):
        super().__init__(direction)
        self.target = target

    def perform(self, engine: 'Engine', entity: Entity) -> ActionResult:
        LOG.info('Attack! %s', self.target)
        return ActionResult(self, success=True)
