import curses
import fcntl
import termios
import os

import more_itertools
import q

from pyhstr.io import Reader, Writer
from pyhstr.util import EntryCounter, PageCounter

PYTHON_HISTORY = os.path.expanduser("~/.python_history")
FAVORITES = os.path.expanduser("~/.config/pyhstr/favorites")
COLORS = {
    "normal": 1,
    "highlighted-white": 2,
    "highlighted-green": 3
}
PYHSTR_LABEL = "Type to filter, UP/DOWN move, RET/TAB select, DEL remove, C-f add favorite, ESC quit"
 

class App:

    MODES = {
        "std": 0,
        "fav": 1
    }

    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.reader = Reader()
        self.writer = Writer()
        self.all_entries = self.reader.read(PYTHON_HISTORY)
        self.favorites = self.reader.read(FAVORITES)
        self.search_results = []
        self.search_string = ""
        self.search_mode = False
        self.page = PageCounter()
        self.selected = EntryCounter(self)
        self.mode = self.MODES["std"]

    def _addstr(self, y_coord, x_coord, text, color_info):
        """
        Works around curses' limitation of drawing at bottom right corner
        of the screen, as seen on https://stackoverflow.com/q/36387625
        """
        screen_height, screen_width = self.stdscr.getmaxyx()
        if x_coord + len(text) == screen_width and y_coord == screen_height-1:
            try:
                self.stdscr.addstr(y_coord, x_coord, text, color_info)
            except curses.error:
                pass
        else:
            self.stdscr.addstr(y_coord, x_coord, text, color_info)


    def populate_screen(self, entries):
        self.stdscr.clear()
        PAGE_STATUS = "page {}/{}".format(self.page.value, len(self.look_into()) - 1)
        PYHSTR_STATUS = "- mode:{} (C-/) - match:exact (C-e) - case:sensitive (C-t) - {}".format(self.mode, PAGE_STATUS)
        for index, entry in enumerate(entries):
            if index == self.selected.value:
                self._addstr(index + 3, 0, entry.ljust(curses.COLS), curses.color_pair(COLORS["highlighted-green"]))
            else:
                self._addstr(index + 3, 0, entry.ljust(curses.COLS), curses.color_pair(COLORS["normal"]))
        self._addstr(1, 0, PYHSTR_LABEL, curses.color_pair(COLORS["normal"]))
        self._addstr(2, 0, PYHSTR_STATUS.ljust(curses.COLS), curses.color_pair(COLORS["highlighted-white"]))
        self._addstr(0, 0, f">>> {self.search_string}", curses.color_pair(COLORS["normal"]))

    def init_color_pairs(self):
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(2, 0, 15)
        curses.init_pair(3, 15, curses.COLOR_GREEN)

    def get_number_of_entries_on_the_page(self):
        return len(self.look_into()[self.page.value])

    def get_number_of_pages(self):
        return len(self.look_into())

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
        for entry in more_itertools.flatten(self.std_or_fav()):
            if self.search_string in entry:
                self.search_results.append(entry)
        self.search_results = list(more_itertools.sliced(self.search_results, curses.LINES - 3))
        if self.search_results:
            self.populate_screen(self.search_results[self.page.value])
        else:
            self.populate_screen(self.search_results)

    def std_or_fav(self):
        if self.mode == self.MODES["fav"]:
            return self.favorites
        return self.all_entries

    def look_into(self):
        if self.search_mode:
            return self.search_results
        return self.all_entries if self.mode != self.MODES["fav"] else self.favorites

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
        self.write(FAVORITES, favorites)
        self.favorites = self.reader.read(FAVORITES)

    def check_if_in_favorites(self):
        command = self.look_into()[self.page.value][self.selected.value]
        for cmd in more_itertools.flatten(self.favorites):
            if command == cmd:
                return True
        return False

    def delete_from_favorites(self):
        command = self.look_into()[self.page.value][self.selected.value]
        favorites = self.favorites
        favorites = list(more_itertools.flatten(favorites))
        favorites.remove(command)
        self.write(FAVORITES, favorites)
        self.favorites = self.reader.read(FAVORITES)

def main(stdscr):
    app = App(stdscr)
    app.init_color_pairs()
    app.populate_screen(app.all_entries[app.page.value])

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
            app.populate_screen(app.std_or_fav()[app.page.value])

        elif user_input == curses.KEY_UP:
            boundary = app.get_number_of_entries_on_the_page()
            app.selected.dec(boundary)
            app.populate_screen(app.look_into()[app.page.value])

        elif user_input == curses.KEY_DOWN:
            boundary = app.get_number_of_entries_on_the_page()
            app.selected.inc(boundary)
            app.populate_screen(app.look_into()[app.page.value])

        elif user_input == curses.KEY_NPAGE:
            boundary = app.get_number_of_pages()
            app.page.inc(boundary)
            app.populate_screen(app.look_into()[app.page.value])

        elif user_input == curses.KEY_PPAGE:
            boundary = app.get_number_of_pages()
            app.page.dec(boundary)
            app.populate_screen(app.look_into()[app.page.value])

        elif user_input == curses.KEY_BACKSPACE:
            app.search_string = app.search_string[:-1]
            app.search()

        else:
            app.search_string += chr(user_input)
            app.search()


if __name__ == "__main__":
    curses.wrapper(main)
