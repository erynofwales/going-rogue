# Eryn Wells <eryn@erynwells.me>

from typing import TYPE_CHECKING

from .actions import Action, WaitAction
from .components import Component
from .object import Entity

if TYPE_CHECKING:
    from .engine import Engine

class AI(Component):
    def __init__(self, entity: Entity) -> None:
        super().__init__()
        self.entity = entity

    def act(self, engine: 'Engine') -> Action:
        raise NotImplementedError()

class HostileEnemy(AI):
    def act(self, engine: 'Engine') -> Action:
        return WaitAction(self.entity)