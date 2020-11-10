import curses
from pathlib import Path

from pyhstr.user_interface import UserInterface
from pyhstr.utilities import (
    echo, detect_shell, read, get_ipython_history,
    remove_duplicates, sort, write, Shell
)

SHELL = detect_shell()

PYTHON_HISTORY = Path("~/.python_history").expanduser()
BPYTHON_HISTORY = Path("~/.pythonhist").expanduser() # FIXME: get this programatically
PYTHON_FAVORITES = Path("~/.config/pyhstr/pyfavorites").expanduser()
IPYTHON_FAVORITES = Path("~/.config/pyhstr/ipyfavorites").expanduser()
BPYTHON_FAVORITES = Path("~/.config/pyhstr/bpyfavorites").expanduser()

FAVORITES_MAP = {
    Shell.IPYTHON: IPYTHON_FAVORITES,
    Shell.BPYTHON: BPYTHON_FAVORITES,
    Shell.STANDARD: PYTHON_FAVORITES
}

BINDINGS = {
    curses.KEY_UP: -1,
    curses.KEY_DOWN: 1,
    curses.KEY_PPAGE: -1,
    curses.KEY_NPAGE: 1
}


class App:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.user_interface = UserInterface(self)
        history = self.get_history()
        self.all_entries = {
            0: sort(history),
            1: sort(read(FAVORITES_MAP[SHELL])),
            2: remove_duplicates(history)
        }
        self.to_restore = self.all_entries.copy()
        self.case_sensitivity = False
        self.view = 0 # 0 = sorted; 1 = favorites; 2 = history
        self.regex_match = False

    @staticmethod
    def get_history():
        if SHELL == Shell.IPYTHON:
            return get_ipython_history()
        elif SHELL == SHELL.BPYTHON:
            return read(BPYTHON_HISTORY)
        return read(PYTHON_HISTORY)

    def search(self):
        self.user_interface.page.selected.value = 0
        self.user_interface.page.value = 1

        self.all_entries[self.view] = [
            cmd for cmd in self.all_entries[self.view]
            if self.user_interface.create_search_string_regex().search(cmd)
        ]

        self.user_interface.populate_screen()

    def delete_from_history(self, command):
        self.user_interface.prompt_for_deletion(command)
        answer = self.stdscr.getch()

        if answer == ord("y"):
            for cmd in self.all_entries[2]:
                if cmd == command:
                    self.all_entries[2].remove(cmd)
            write(PYTHON_HISTORY, self.all_entries[2])
            self.user_interface.populate_screen()

        elif answer == ord("n"):
            self.user_interface.populate_screen()

    def toggle_case(self):
        self.case_sensitivity = not self.case_sensitivity

    def toggle_view(self):
        self.view = (self.view + 1) % 3

    def toggle_match(self):
        self.regex_match = not self.regex_match

    def add_to_or_remove_from_favorites(self, command):
        if command not in self.all_entries[1]:
            self.all_entries[1].append(command)
        else:
            self.all_entries[1].remove(command)
        write(FAVORITES_MAP[SHELL], self.all_entries[1])


def main(stdscr): # pylint: disable=too-many-statements
    app = App(stdscr)
    app.user_interface.init_color_pairs()
    app.user_interface.populate_screen()

    while True:
        try:
            user_input = app.stdscr.get_wch()
        except curses.error:
            continue
        except KeyboardInterrupt:
            break

        if user_input == "\x05": # C-e
            app.toggle_match()
            app.user_interface.page.selected.value = 0
            app.user_interface.populate_screen()

        elif user_input == "\x06": # C-f
            command = app.user_interface.page.get_selected()
            app.add_to_or_remove_from_favorites(command)

        elif user_input == "\t": # TAB
            command = app.user_interface.page.get_selected()
            echo(command)
            break

        elif user_input == "\n": # ENTER
            command = app.user_interface.page.get_selected()
            echo(command)
            echo("\n")
            break

        elif user_input == "\x14": # C-t
            app.toggle_case()
            app.user_interface.populate_screen()

        elif user_input == "\x1b": # ESC
            break

        elif user_input == "\x1f": # C-/
            app.toggle_view()
            app.user_interface.page.selected.value = 0
            app.user_interface.populate_screen()

        elif user_input in {curses.KEY_UP, curses.KEY_DOWN}:
            app.user_interface.page.selected.move(BINDINGS[user_input])
            app.user_interface.populate_screen()

        elif user_input in {curses.KEY_NPAGE, curses.KEY_PPAGE}:
            app.user_interface.page.turn(BINDINGS[user_input])
            app.user_interface.populate_screen()

        elif user_input == curses.KEY_BACKSPACE:
            app.user_interface.search_string = app.user_interface.search_string[:-1]
            if not app.user_interface.search_string:
                app.user_interface.page.selected.value = 0
            app.all_entries = app.to_restore.copy()
            app.search()

        elif user_input == curses.KEY_DC: # del
            command = app.user_interface.page.get_selected()
            app.delete_from_history(command)

        else:
            app.user_interface.search_string += user_input
            app.all_entries = app.to_restore.copy()
            app.search()
