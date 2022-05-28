#!/usr/bin/env python3
# Eryn Wells <eryn@erynwells.me>

'''
This module defines all of the actions that can be performed by the game. These actions can come from the player (e.g.
via keyboard input), or from non-player entities (e.g. AI deciboard input), or from non-player entities (e.g. AI
decisions).

Class Hierarchy
---------------

Action : Base class of all actions
    MoveAction : Base class for all actions that are performed with a direction
        BumpAction
        WalkAction
        MeleeAction
    ExitAction
    WaitAction
'''

from typing import TYPE_CHECKING

from .. import items
from .. import log
from ..geometry import Direction
from ..object import Actor, Item
from .action import Action
from .result import ActionResult

if TYPE_CHECKING:
    from ..engine import Engine

class ExitAction(Action):
    '''Exit the game.'''

    def __init__(self):
        super().__init__(None)

    def perform(self, engine: 'Engine') -> ActionResult:
        raise SystemExit()

class RegenerateRoomsAction(Action):
    '''Regenerate the dungeon map'''

    def perform(self, engine: 'Engine') -> ActionResult:
        return ActionResult(self, success=False)

# pylint: disable=abstract-method
class MoveAction(Action):
    '''An abstract Action that requires a direction to complete.'''

    def __init__(self, actor: Actor, direction: Direction):
        super().__init__(actor)
        self.direction = direction

    def __repr__(self):
        return f'{self.__class__.__name__}({self.actor!r}, {self.direction!r})'

    def __str__(self) -> str:
        return f'{self.__class__.__name__} toward {self.direction} by {self.actor!s}'

class BumpAction(MoveAction):
    '''Attempt to perform a movement action in a direction.

    This action tests if an action in the direction is possible and returns the action that can be completed.

    Attributes
    ----------
    direction : Direction
        The direction to test
    '''

    def perform(self, engine: 'Engine') -> ActionResult:
        new_position = self.actor.position + self.direction

        position_is_in_bounds = engine.map.tile_is_in_bounds(new_position)
        position_is_walkable = engine.map.tile_is_walkable(new_position)

        for ent in engine.entities:
            if new_position != ent.position or not ent.blocks_movement:
                continue
            entity_occupying_position = ent
            break
        else:
            entity_occupying_position = None

        log.ACTIONS.info('Bumping %s into %s (in_bounds:%s walkable:%s overlaps:%s)',
            self.actor,
            new_position,
            position_is_in_bounds,
            position_is_walkable,
            entity_occupying_position)

        if not position_is_in_bounds or not position_is_walkable:
            return self.failure()

        if entity_occupying_position:
            assert entity_occupying_position.blocks_movement
            return ActionResult(self, alternate=MeleeAction(self.actor, self.direction, entity_occupying_position))

        return ActionResult(self, alternate=WalkAction(self.actor, self.direction))


class WalkAction(MoveAction):
    '''Walk one step in the given direction.'''

    def perform(self, engine: 'Engine') -> ActionResult:
        new_position = self.actor.position + self.direction

        log.ACTIONS.debug('Moving %s to %s', self.actor, new_position)
        self.actor.position = new_position

        try:
            should_recover_hit_points = self.actor.fighter.passively_recover_hit_points(5)
            if should_recover_hit_points:
                return ActionResult(self, alternate=HealAction(self.actor, 1))
        except AttributeError:
            pass

        return self.success()

class MeleeAction(MoveAction):
    '''Perform a melee attack on another Actor'''

    def __init__(self, actor: Actor, direction: Direction, target: Actor):
        super().__init__(actor, direction)
        self.target = target

    def perform(self, engine: 'Engine') -> ActionResult:
        try:
            damage = self.actor.fighter.attack_power - self.target.fighter.defense
            if damage > 0 and self.target:
                log.ACTIONS.debug('%s attacks %s for %d damage!', self.actor, self.target, damage)
                self.target.fighter.hit_points -= damage

                if self.actor == engine.hero:
                    engine.message_log.add_message(f'You attack the {self.target.name} for {damage} damage!', fg=(127, 255, 127))
                elif self.target == engine.hero:
                    engine.message_log.add_message(f'The {self.actor.name} attacks you for {damage} damage!', fg=(255, 127, 127))
            else:
                log.ACTIONS.debug('%s attacks %s but does no damage!', self.actor, self.target)

            if self.target.fighter.is_dead:
                log.ACTIONS.info('%s is dead!', self.target)
                return ActionResult(self, alternate=DieAction(self.target))
        except AttributeError:
            return self.failure()
        else:
            return self.success()

class WaitAction(Action):
    '''Wait a turn'''

    def perform(self, engine: 'Engine') -> ActionResult:
        log.ACTIONS.debug('%s is waiting a turn', self.actor)

        if self.actor == engine.hero:
            should_recover_hit_points = self.actor.fighter.passively_recover_hit_points(10)
            if should_recover_hit_points:
                return ActionResult(self, alternate=HealAction(self.actor, 1))

        return self.success()

class DieAction(Action):
    '''Kill an Actor'''

    def perform(self, engine: 'Engine') -> ActionResult:
        engine.kill_actor(self.actor)

        if self.actor == engine.hero:
            engine.message_log.add_message('You die...', fg=(255, 127, 127))
        else:
            engine.message_log.add_message(f'The {self.actor.name} dies', fg=(127, 255, 127))

        if self.actor.yields_corpse_on_death:
            log.ACTIONS.debug('%s leaves a corpse behind', self.actor)
            corpse = Item(kind=items.Corpse, name=f'{self.actor.name} Corpse', position=self.actor.position)
            return ActionResult(self, alternate=DropItemAction(self.actor, corpse))

        return self.success()

class DropItemAction(Action):
    '''Drop an item'''

    def __init__(self, actor: 'Actor', item: 'Item'):
        super().__init__(actor)
        self.item = item

    def perform(self, engine: 'Engine') -> ActionResult:
        engine.entities.add(self.item)
        return self.success()

class HealAction(Action):
    '''Heal a target actor some number of hit points'''

    def __init__(self, actor: 'Actor', hit_points_to_recover: int):
        super().__init__(actor)
        self.hit_points_to_recover = hit_points_to_recover

    def perform(self, engine: 'Engine') -> ActionResult:
        fighter = self.actor.fighter
        if not fighter:
            log.ACTIONS.error('Attempted to heal %s but it has no hit points', self.actor)
            return self.failure()

        fighter.hit_points += self.hit_points_to_recover

        return self.success()
