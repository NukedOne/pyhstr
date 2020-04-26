import curses
import os

from pyhstr.user_interface import UserInterface
from pyhstr.utilities import (
    echo, EntryCounter, PageCounter, read, sort, write
)


PYTHON_HISTORY = os.path.expanduser("~/.python_history")


class App:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.user_interface = UserInterface(self)
        self.all_entries = sort(read(PYTHON_HISTORY))
        self.search_string = ""
        self.page = PageCounter()
        self.selected = EntryCounter(self)
        self.case_sensitivity = False

    def search(self):
        self.selected.value = 0
        self.page.value = 1

        if self.case_sensitivity:
            self.all_entries = [
                cmd for cmd in self.all_entries if self.search_string in cmd
            ]
        else:
            self.all_entries = [
                cmd for cmd in self.all_entries if self.search_string.lower() in cmd.lower()
            ]

        self.user_interface.populate_screen(self.user_interface.get_page(self.page.value))

    def delete_from_history(self, command):
        self.user_interface.prompt_for_deletion(command)
        answer = self.stdscr.getch()

        if answer == ord("y"):
            for cmd in self.all_entries:
                if cmd == command:
                    self.all_entries.remove(cmd)
            write(PYTHON_HISTORY, self.all_entries)
            self.all_entries = read(PYTHON_HISTORY)
            self.user_interface.populate_screen(self.user_interface.get_page(self.page.value))

        elif answer == ord("n"):
            self.user_interface.populate_screen(self.user_interface.get_page(self.page.value))

    def toggle_case(self):
        self.case_sensitivity = not self.case_sensitivity


def main(stdscr):
    app = App(stdscr)
    app.user_interface.init_color_pairs()
    app.user_interface.populate_screen(app.user_interface.get_page(app.page.value))

    while True:
        try:
            user_input = app.stdscr.getch()
        except curses.error:
            continue

        if user_input == 9: # TAB
            command = app.user_interface.get_page(app.page.value)[app.selected.value]
            echo(command)
            break

        elif user_input == 10: # ENTER ("\n")
            command = app.user_interface.get_page(app.page.value)[app.selected.value]
            echo(command)
            echo("\n")
            break

        elif user_input == 20: # C-t
            app.toggle_case()
            app.user_interface.populate_screen(app.user_interface.get_page(app.page.value))

        elif user_input == 27: # ESC
            break

        elif user_input == curses.KEY_UP:
            page_size = app.user_interface.get_page_size(app.page.value)
            app.selected.dec(page_size)
            app.user_interface.populate_screen(app.user_interface.get_page(app.page.value))

        elif user_input == curses.KEY_DOWN:
            page_size = app.user_interface.get_page_size(app.page.value)
            app.selected.inc(page_size)
            app.user_interface.populate_screen(app.user_interface.get_page(app.page.value))

        elif user_input == curses.KEY_NPAGE:
            total_pages = app.user_interface.get_number_of_pages()
            app.page.inc(total_pages)
            app.user_interface.populate_screen(app.user_interface.get_page(app.page.value))

        elif user_input == curses.KEY_PPAGE:
            total_pages = app.user_interface.get_number_of_pages()
            app.page.dec(total_pages)
            app.user_interface.populate_screen(app.user_interface.get_page(app.page.value))

        elif user_input == curses.KEY_BACKSPACE:
            app.search_string = app.search_string[:-1]
            if not app.search_string:
                app.selected.value = 0
            app.all_entries = sort(read(PYTHON_HISTORY))
            app.search()

        elif user_input == curses.KEY_DC: # del
            command = app.user_interface.get_page(app.page.value)[app.selected.value]
            app.delete_from_history(command)

        else:
            app.search_string += chr(user_input)
            app.search()


if __name__ == "__main__":
    curses.wrapper(main)
