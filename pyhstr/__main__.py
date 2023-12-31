import curses
from typing import Any, TYPE_CHECKING

from pyhstr.application import App, View
from pyhstr.user_interface import Direction
from pyhstr.utilities import echo

if TYPE_CHECKING:
    from _curses import _CursesWindow  # pylint: disable=no-name-in-module
else:
    _CursesWindow = Any


KEY_BINDINGS = {
    curses.KEY_UP: Direction.PREVIOUS,
    curses.KEY_DOWN: Direction.NEXT,
    curses.KEY_PPAGE: Direction.PREVIOUS,
    curses.KEY_NPAGE: Direction.NEXT,
}

CTRL_E = "\x05"
CTRL_F = "\x06"
CTRL_T = "\x14"
CTRL_SLASH = "\x1f"
TAB = "\t"
ENTER = "\n"
ESC = "\x1b"
DEL = curses.KEY_DC


def main(stdscr: _CursesWindow) -> None:  # pylint: disable=too-many-statements
    app = App(stdscr)
    app.user_interface.init_color_pairs()
    app.user_interface.populate_screen()

    while True:
        try:
            user_input = app.stdscr.get_wch()
        except curses.error:
            app.stdscr.clear()
            app.user_interface.populate_screen()
            continue
        except KeyboardInterrupt:
            break

        # user_input is Union[int, str], sometimes isinstance needed to make mypy happy

        if user_input == CTRL_E:
            app.toggle_regex_mode()
            app.user_interface.page.selected = 0
            app.user_interface.populate_screen()

        elif user_input == CTRL_F:
            command = app.user_interface.page.get_selected()
            if app.view == View.FAVORITES:
                app.user_interface.page.retain_selection()
            app.add_or_rm_fav(command)
            app.stdscr.clear()
            app.user_interface.populate_screen()

        elif user_input == TAB:
            command = app.user_interface.page.get_selected()
            echo(command)
            break

        elif user_input == ENTER:
            command = app.user_interface.page.get_selected()
            echo(command)
            echo("\n")
            break

        elif user_input == CTRL_T:
            app.toggle_case()
            app.user_interface.populate_screen()

        elif user_input == ESC:
            break

        elif user_input == CTRL_SLASH:
            app.toggle_view()
            app.user_interface.page.selected = 0
            app.user_interface.page.value = 1
            app.stdscr.clear()
            app.user_interface.populate_screen()

        elif user_input in {curses.KEY_UP, curses.KEY_DOWN}:
            assert isinstance(user_input, int)
            app.user_interface.page.move_selected(KEY_BINDINGS[user_input])
            app.user_interface.populate_screen()

        elif user_input in {curses.KEY_NPAGE, curses.KEY_PPAGE}:
            assert isinstance(user_input, int)
            app.user_interface.page.turn(KEY_BINDINGS[user_input])
            app.user_interface.populate_screen()

        elif user_input == curses.KEY_BACKSPACE:
            app.search_string = app.search_string[:-1]
            if not app.search_string:
                app.user_interface.page.selected = 0
            app.commands = app.to_restore.copy()
            app.search()

        elif user_input == DEL:
            command = app.user_interface.page.get_selected()
            app.user_interface.prompt_for_deletion(command)
            answer = app.stdscr.getch()
            if answer == ord("y"):
                app.user_interface.page.retain_selection()
                app.delete_from_history(command)
            app.stdscr.clear()
            app.user_interface.populate_screen()

        elif isinstance(user_input, str):
            # not another special int character like curses.KEY_UP
            app.search_string += user_input
            app.commands = app.to_restore.copy()
            app.search()

    stdscr.clear()
    stdscr.refresh()
    curses.doupdate()
