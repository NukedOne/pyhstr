import curses
import os


from pyhstr.user_interface import UserInterface
from pyhstr.utilities import (
    echo, read, sort, write
)


PYTHON_HISTORY = os.path.expanduser("~/.python_history")


class App:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.user_interface = UserInterface(self)
        self.all_entries = sort(read(PYTHON_HISTORY))
        self.to_restore = self.all_entries[:]
        self.case_sensitivity = False

    def search(self):
        self.user_interface.page.selected.value = 0
        self.user_interface.page.value = 1

        if self.case_sensitivity:
            self.all_entries = [
                cmd for cmd in self.all_entries if self.user_interface.search_string in cmd
            ]
        else:
            self.all_entries = [
                cmd for cmd in self.all_entries if self.user_interface.search_string.lower() in cmd.lower()
            ]

        self.user_interface.populate_screen()

    def delete_from_history(self, command):
        self.user_interface.prompt_for_deletion(command)
        answer = self.stdscr.getch()

        if answer == ord("y"):
            for cmd in self.all_entries:
                if cmd == command:
                    self.all_entries.remove(cmd)
            write(PYTHON_HISTORY, self.all_entries)
            self.user_interface.populate_screen()

        elif answer == ord("n"):
            self.user_interface.populate_screen()

    def toggle_case(self):
        self.case_sensitivity = not self.case_sensitivity


def main(stdscr):
    app = App(stdscr)
    app.user_interface.init_color_pairs()
    app.user_interface.populate_screen()

    while True:
        try:
            user_input = app.stdscr.getch()
        except curses.error:
            continue

        if user_input == 9: # TAB
            command = app.user_interface.page.get_selected()
            echo(command)
            break

        elif user_input == 10: # ENTER ("\n")
            command = app.user_interface.page.get_selected()
            echo(command)
            echo("\n")
            break

        elif user_input == 20: # C-t
            app.toggle_case()
            app.user_interface.populate_screen()

        elif user_input == 27: # ESC
            break

        elif user_input == curses.KEY_UP:
            app.user_interface.page.selected.dec()
            app.user_interface.populate_screen()

        elif user_input == curses.KEY_DOWN:
            app.user_interface.page.selected.inc()
            app.user_interface.populate_screen()

        elif user_input == curses.KEY_NPAGE:
            app.user_interface.page.inc()
            app.user_interface.populate_screen()

        elif user_input == curses.KEY_PPAGE:
            app.user_interface.page.dec()
            app.user_interface.populate_screen()

        elif user_input == curses.KEY_BACKSPACE:
            app.user_interface.search_string = app.user_interface.search_string[:-1]
            if not app.user_interface.search_string:
                app.user_interface.page.selected.value = 0
            app.all_entries = app.to_restore[:]
            app.search()

        elif user_input == curses.KEY_DC: # del
            command = app.user_interface.page.get_selected()
            app.delete_from_history(command)

        else:
            app.user_interface.search_string += chr(user_input)
            app.search()

# don't forget to remove this
if __name__ == "__main__":
    curses.wrapper(main)
    
