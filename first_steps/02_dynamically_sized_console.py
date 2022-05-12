#!/usr/bin/env python3
import tcod

WIDTH, HEIGHT = 720, 480  # Window pixel resolution (when not maximized.)
FLAGS = tcod.context.SDL_WINDOW_RESIZABLE | tcod.context.SDL_WINDOW_MAXIMIZED


def main() -> None:
    """Script entry point."""
	# New window with pixel resolution of width×height.
    with tcod.context.new(width=WIDTH, height=HEIGHT, sdl_window_flags=FLAGS) as context:
        while True:
			# Console size based on window resolution and tile size.
            console = context.new_console(order="F")
            console.print(0, 0, "Hello World")
            context.present(console, integer_scaling=True)

            for event in tcod.event.wait():
				# Sets tile coordinates for mouse events.
                context.convert_event(event)  
                print(event)

                if isinstance(event, tcod.event.Quit):
                    raise SystemExit()
                elif isinstance(event, tcod.event.WindowResized) and event.type == "WINDOWRESIZED":
                    pass  # The next call to context.new_console may return a different size.


if __name__ == "__main__":
    main()
