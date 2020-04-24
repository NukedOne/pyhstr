import collections
import curses
import fcntl
import termios
import os

import more_itertools
import q

from pyhstr.user_interface import UserInterface, COLORS, PYHSTR_LABEL
from pyhstr.utilities import EntryCounter, PageCounter


PYTHON_HISTORY = os.path.expanduser("~/.python_history")
FAVORITES = os.path.expanduser("~/.config/pyhstr/favorites")
 

class App:

    CASES = {
        "sensitive": 0,
        "insensitive": 1
    }

    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.user_interface = UserInterface(self)
        self.all_entries = self.slice(self.read(PYTHON_HISTORY))
        self.search_results = []
        self.search_string = ""
        self.search_mode = False
        self.page = PageCounter()
        self.selected = EntryCounter(self)
        self.case = self.CASES["insensitive"]

    def _get_key(self, d, value):
        for k, v in d.items():
            if v == value:
                return k

    def _look_into(self):
        if self.search_mode:
            return self.search_results
        return self.all_entries

    def echo(self, command):
        command = command.encode("utf-8")
        for byte in command:
            fcntl.ioctl(0, termios.TIOCSTI, bytes([byte]))

    def write(self, path, thing):
        with open(path, "w") as f:
            for thingy in thing:
                print(thingy, file=f)
 
    def read(self, path):
        history = []
        with open(path, "r") as f:
            for command in f:
                history.append(command.strip())
        return [
            x[0] for x in sorted(
                collections.Counter(history).items(), key=lambda y: -y[1]
            )
        ]

    def search(self):
        if self.search_string:
            self.search_mode = True
        else:
            self.search_mode = False

        self.selected.value = 0
        self.page.value = 0
        self.search_results.clear()
        
        for entry in more_itertools.flatten(self.all_entries):
            if self.case == self.CASES["sensitive"]:
                if self.search_string in entry:
                    self.search_results.append(entry)
            else:
                if self.search_string.lower() in entry.lower():
                    self.search_results.append(entry)                
        
        self.search_results = self.slice(self.search_results)
        
        if self.search_results:
            self.user_interface.populate_screen(self.search_results[self.page.value])
        else:
            self.user_interface.populate_screen(self.search_results)

    def toggle_case(self):
        if self.case == self.CASES["insensitive"]:
            self.case = self.CASES["sensitive"]
        else:
            self.case = self.CASES["insensitive"]

    def delete_from_history(self, command):
        self.user_interface.prompt_for_deletion(command)
        answer = self.stdscr.getch()
        
        if answer == ord("y"):
            for page in self.all_entries:
                for cmd in page:
                    if cmd == command:
                        page.remove(cmd)
            self.write(PYTHON_HISTORY, more_itertools.flatten(self.all_entries))
            self.all_entries = self.slice(self.read(PYTHON_HISTORY))
            self.user_interface.populate_screen(self._look_into()[self.page.value])
        
        elif answer == ord("n"):
            self.user_interface.populate_screen(self._look_into()[self.page.value])

    def slice(self, thing):
        return list(more_itertools.sliced(thing, curses.LINES - 3)) # account for 3 lines at the top


def main(stdscr):
    app = App(stdscr)
    app.user_interface.init_color_pairs()
    app.user_interface.populate_screen(app.all_entries[app.page.value])

    while True:
        try:
            user_input = app.stdscr.getch()
        except curses.error:
            continue
   
        if user_input == 9: # TAB
            command = app._look_into()[app.page.value][app.selected.value]
            app.echo(command)
            break

        elif user_input == 10: # ENTER ("\n")
            command = app._look_into()[app.page.value][app.selected.value]
            app.echo(command)
            app.echo("\n")
            break

        elif user_input == 20: # C-t
            app.toggle_case()
            app.user_interface.populate_screen(app._look_into()[app.page.value])

        elif user_input == 27: # ESC
            break

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

        elif user_input == curses.KEY_DC: # del
            command = app._look_into()[app.page.value][app.selected.value]
            app.delete_from_history(command)

        else:
            app.search_string += chr(user_input)
            app.search()


if __name__ == "__main__":
    curses.wrapper(main)
