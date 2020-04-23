import curses
import fcntl
import termios
import os

import more_itertools
import q

from pyhstr.io import Reader, Writer
from pyhstr.ui import UserInterface
from pyhstr.util import EntryCounter, PageCounter


PYTHON_HISTORY = os.path.expanduser("~/.python_history")
FAVORITES = os.path.expanduser("~/.config/pyhstr/favorites")
 

class App:

    MODES = {
        "std": 0,
        "fav": 1
    }

    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.reader = Reader()
        self.writer = Writer()
        self.user_interface = UserInterface(self)
        self.all_entries = self.user_interface.slice(self.reader.read(PYTHON_HISTORY))
        self.favorites = self.user_interface.slice(self.reader.read(FAVORITES))
        self.search_results = []
        self.search_string = ""
        self.search_mode = False
        self.page = PageCounter()
        self.selected = EntryCounter(self)
        self.mode = self.MODES["std"]

    def _std_or_fav(self):
        if self.mode == self.MODES["fav"]:
            return self.favorites
        return self.all_entries

    def _look_into(self):
        if self.search_mode:
            return self.search_results
        return self.all_entries if self.mode != self.MODES["fav"] else self.favorites

    def echo(self, command):
        command = command.encode("utf-8")
        for byte in command:
            fcntl.ioctl(0, termios.TIOCSTI, bytes([byte]))

    def search(self):
        if self.search_string:
            self.search_mode = True
        else:
            self.search_mode = False
        self.page.value = 0
        self.search_results.clear()
        for entry in more_itertools.flatten(self._std_or_fav()):
            if self.search_string in entry:
                self.search_results.append(entry)
        self.search_results = list(more_itertools.sliced(self.search_results, curses.LINES - 3))
        if self.search_results:
            self.user_interface.populate_screen(self.search_results[self.page.value])
        else:
            self.user_interface.populate_screen(self.search_results)

    def toggle_mode(self):
        self.selected.value = 0
        if self.mode == self.MODES["std"]:
            self.mode = self.MODES["fav"]
        else:
            self.mode = self.MODES["std"]

    def add_to_favorites(self):
        favorites = self.favorites
        favorites = list(more_itertools.flatten(favorites))
        favorites.append(self.look_into()[self.page.value][self.selected.value])
        self.writer.write(FAVORITES, favorites)
        self.favorites = self.reader.read(FAVORITES)

    def check_if_in_favorites(self):
        command = self._look_into()[self.page.value][self.selected.value]
        for cmd in more_itertools.flatten(self.favorites):
            if command == cmd:
                return True
        return False

    def delete_from_favorites(self):
        command = self.look_into()[self.page.value][self.selected.value]
        favorites = self.favorites
        favorites = list(more_itertools.flatten(favorites))
        favorites.remove(command)
        self.writer.write(FAVORITES, favorites)
        self.favorites = self.reader.read(FAVORITES)


def main(stdscr):
    app = App(stdscr)
    app.user_interface.init_color_pairs()
    app.user_interface.populate_screen(app.all_entries[app.page.value])

    while True:
        try:
            user_input = app.stdscr.getch()
        except curses.error:
            continue

        if user_input == 6: # C-f
            if not app.check_if_in_favorites():
                app.add_to_favorites()
            else:
                app.delete_from_favorites()

        elif user_input == 9: # TAB
            command = app.look_into()[app.page.value][app.selected.value]
            app.echo(command)
            break

        elif user_input == 10: # ENTER ("\n")
            command = app.look_into()[app.page.value][app.selected.value]
            app.echo(command)
            app.echo("\n")
            break

        elif user_input == 27: # ESC
            break

        elif user_input == 31: # C-/
            app.toggle_mode()
            app.user_interface.populate_screen(app._std_or_fav()[app.page.value])

        elif user_input == curses.KEY_UP:
            boundary = app.user_interface.get_number_of_entries_on_the_page()
            app.selected.dec(boundary)
            app.user_interface.populate_screen(app._look_into()[app.page.value])

        elif user_input == curses.KEY_DOWN:
            boundary = app.user_interface.get_number_of_entries_on_the_page()
            app.selected.inc(boundary)
            app.user_interface.populate_screen(app._look_into()[app.page.value])

        elif user_input == curses.KEY_NPAGE:
            boundary = app.user_interface.get_number_of_pages()
            app.page.inc(boundary)
            app.user_interface.populate_screen(app._look_into()[app.page.value])

        elif user_input == curses.KEY_PPAGE:
            boundary = app.user_interface.get_number_of_pages()
            app.page.dec(boundary)
            app.user_interface.populate_screen(app._look_into()[app.page.value])

        elif user_input == curses.KEY_BACKSPACE:
            app.search_string = app.search_string[:-1]
            if not app.search_string:
                app.selected.value = 0
            app.search()

        else:
            app.search_string += chr(user_input)
            app.search()


if __name__ == "__main__":
    curses.wrapper(main)
