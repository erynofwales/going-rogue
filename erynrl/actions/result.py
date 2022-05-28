# Eryn Wells <eryn@erynwells.me>

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .action import Action

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
        return f'{self.__class__.__name__}({self.action!r}, success={self.success}, done={self.done}, alternate={self.alternate!r})'
