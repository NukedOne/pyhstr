import curses


COLORS = {
    # yet to be initialized
    "normal": None,
    "highlighted-white": None,
    "highlighted-green": None,
    "highlighted-red": None,
}
PYHSTR_LABEL = "Type to filter, UP/DOWN move, RET/TAB select, DEL remove, ESC quit"
PYHSTR_STATUS = " - case:{} (C-t) - page {}/{}"


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

    @staticmethod
    def init_color_pairs():
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(2, 0, 15)
        curses.init_pair(3, 15, curses.COLOR_GREEN)
        curses.init_pair(4, 15, curses.COLOR_RED)
        COLORS["normal"] = curses.color_pair(1)
        COLORS["highlighted-white"] = curses.color_pair(2)
        COLORS["highlighted-green"] = curses.color_pair(3)
        COLORS["highlighted-red"] = curses.color_pair(4)

    def populate_screen(self, entries):
        self.app.stdscr.clear()
        pyhstr_status = PYHSTR_STATUS.format(
            self.app.get_key(self.app.CASES, self.app.case),
            self.app.page.value,
            len(self.app.searched_or_all()) - 1
        )

        for index, entry in enumerate(entries):
            if index == self.app.selected.value:
                self._addstr(index + 3, 0, entry.ljust(curses.COLS), COLORS["highlighted-green"])
            else:
                self._addstr(index + 3, 0, entry.ljust(curses.COLS), COLORS["normal"])

        self._addstr(1, 0, PYHSTR_LABEL, COLORS["normal"])
        self._addstr(2, 0, pyhstr_status.ljust(curses.COLS), COLORS["highlighted-white"])
        self._addstr(0, 0, f">>> {self.app.search_string}", COLORS["normal"])

    def get_number_of_entries_on_the_page(self):
        return len(self.app.searched_or_all()[self.app.page.value])

    def get_number_of_pages(self):
        return len(self.app.searched_or_all())

    def prompt_for_deletion(self, command):
        prompt = f"Do you want to delete all occurences of {command}? y/n"
        self._addstr(1, 0, "".ljust(curses.COLS), COLORS["normal"])
        self._addstr(1, 0, prompt, COLORS["highlighted-red"])
