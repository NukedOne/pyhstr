import curses
import more_itertools


COLORS = {
    "normal": 1,
    "highlighted-white": 2,
    "highlighted-green": 3
}
PYHSTR_LABEL = "Type to filter, UP/DOWN move, RET/TAB select, DEL remove, C-f add favorite, ESC quit"


class UserInterface:
    def __init__(self, app):
        self.app = app

    def _addstr(self, y_coord, x_coord, text, color_info):
        """
        Works around curses' limitation of drawing at bottom right corner
        of the screen, as seen on https://stackoverflow.com/q/36387625
        """
        screen_height, screen_width = self.app.stdscr.getmaxyx()
        if x_coord + len(text) == screen_width and y_coord == screen_height-1:
            try:
                self.app.stdscr.addstr(y_coord, x_coord, text, color_info)
            except curses.error:
                pass
        else:
            self.app.stdscr.addstr(y_coord, x_coord, text, color_info)

    def init_color_pairs(self):
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(2, 0, 15)
        curses.init_pair(3, 15, curses.COLOR_GREEN)

    def populate_screen(self, entries):
        self.app.stdscr.clear()
        PAGE_STATUS = "page {}/{}".format(self.app.page.value, len(self.app._look_into()) - 1)
        PYHSTR_STATUS = "- mode:{} (C-/) - match:exact (C-e) - case:sensitive (C-t) - {}".format(self.app.mode, PAGE_STATUS)
        for index, entry in enumerate(entries):
            if index == self.app.selected.value:
                self._addstr(index + 3, 0, entry.ljust(curses.COLS), curses.color_pair(COLORS["highlighted-green"]))
            else:
                self._addstr(index + 3, 0, entry.ljust(curses.COLS), curses.color_pair(COLORS["normal"]))
        self._addstr(1, 0, PYHSTR_LABEL, curses.color_pair(COLORS["normal"]))
        self._addstr(2, 0, PYHSTR_STATUS.ljust(curses.COLS), curses.color_pair(COLORS["highlighted-white"]))
        self._addstr(0, 0, f">>> {self.app.search_string}", curses.color_pair(COLORS["normal"]))

    def get_number_of_entries_on_the_page(self):
        return len(self.app._look_into()[self.app.page.value])

    def get_number_of_pages(self):
        return len(self.app._look_into())

    def slice(self, thing):
        return list(more_itertools.sliced(thing, curses.LINES - 3)) # account for 3 lines at the top