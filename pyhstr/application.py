import curses
import os

import more_itertools

from pyhstr.user_interface import UserInterface
from pyhstr.utilities import (
    echo, EntryCounter, PageCounter, read, slice, sort, write
)


PYTHON_HISTORY = os.path.expanduser("~/.python_history")


class App:

    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.user_interface = UserInterface(self)
        self.all_entries = slice(sort(read(PYTHON_HISTORY)), curses.LINES - 3)
        self.search_results = []
        self.search_string = ""
        self.search_mode = False
        self.page = PageCounter()
        self.selected = EntryCounter(self)
        self.case_sensitivity = False

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

        self.search_results = slice(self.search_results, curses.LINES - 3)

        if self.search_results:
            self.user_interface.populate_screen(self.search_results[self.page.value])
        else:
            self.user_interface.populate_screen(self.search_results)

    def delete_from_history(self, command):
        self.user_interface.prompt_for_deletion(command)
        answer = self.stdscr.getch()

        if answer == ord("y"):
            for page in self.all_entries:
                for cmd in page:
                    if cmd == command:
                        page.remove(cmd)
            write(PYTHON_HISTORY, more_itertools.flatten(self.all_entries))
            self.all_entries = slice(read(PYTHON_HISTORY), curses.LINES - 3)
            self.user_interface.populate_screen(self.searched_or_all()[self.page.value])

        elif answer == ord("n"):
            self.user_interface.populate_screen(self.searched_or_all()[self.page.value])

    def toggle_case(self):
        self.case_sensitivity = not self.case_sensitivity

    def searched_or_all(self):
        if self.search_mode:
            return self.search_results
        return self.all_entries


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
            command = app.searched_or_all()[app.page.value][app.selected.value]
            echo(command)
            break

        elif user_input == 10: # ENTER ("\n")
            command = app.searched_or_all()[app.page.value][app.selected.value]
            echo(command)
            echo("\n")
            break

        elif user_input == 20: # C-t
            app.toggle_case()
            app.user_interface.populate_screen(app.searched_or_all()[app.page.value])

        elif user_input == 27: # ESC
            break

        elif user_input == curses.KEY_UP:
            boundary = app.user_interface.get_number_of_entries_on_the_page()
            app.selected.dec()
            app.user_interface.populate_screen(app.searched_or_all()[app.page.value])

        elif user_input == curses.KEY_DOWN:
            boundary = app.user_interface.get_number_of_entries_on_the_page()
            app.selected.inc(boundary)
            app.user_interface.populate_screen(app.searched_or_all()[app.page.value])

        elif user_input == curses.KEY_NPAGE:
            boundary = app.user_interface.get_number_of_pages()
            app.page.inc(boundary)
            app.user_interface.populate_screen(app.searched_or_all()[app.page.value])

        elif user_input == curses.KEY_PPAGE:
            boundary = app.user_interface.get_number_of_pages()
            app.page.dec(boundary)
            app.user_interface.populate_screen(app.searched_or_all()[app.page.value])

        elif user_input == curses.KEY_BACKSPACE:
            app.search_string = app.search_string[:-1]
            if not app.search_string:
                app.selected.value = 0
            app.search()

        elif user_input == curses.KEY_DC: # del
            command = app.searched_or_all()[app.page.value][app.selected.value]
            app.delete_from_history(command)

        else:
            app.search_string += chr(user_input)
            app.search()


if __name__ == "__main__":
    curses.wrapper(main)
