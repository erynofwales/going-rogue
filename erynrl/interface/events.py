# Eryn Wells <eryn@erynwells.me>

'''Defines event handling mechanisms.'''

from typing import TYPE_CHECKING

from tcod import event as tev

if TYPE_CHECKING:
    from . import Interface


class InterfaceEventHandler(tev.EventDispatch[bool]):
    '''The event handler for the user interface.'''

    def __init__(self, interface: 'Interface'):
        super().__init__()
        self.interface = interface

        self._handlers = []
        self._refresh_handlers()

    def _refresh_handlers(self):
        self._handlers = [
            self.interface.map_window.event_handler,
            self.interface.message_window.event_handler,
            self.interface.info_window.event_handler,
        ]

    def ev_keydown(self, event: tev.KeyDown) -> bool:
        return self._handle_event(event)

    def ev_keyup(self, event: tev.KeyUp) -> bool:
        return self._handle_event(event)

    def ev_mousemotion(self, event: tev.MouseMotion) -> bool:
        return self._handle_event(event)

    def ev_mousebuttondown(self, event: tev.MouseButtonDown) -> bool:
        return self._handle_event(event)

    def ev_mousebuttonup(self, event: tev.MouseButtonUp) -> bool:
        return self._handle_event(event)

    def _handle_event(self, event: tev.Event) -> bool:
        for handler in self._handlers:
            if handler and handler.dispatch(event):
                return True

        return False
