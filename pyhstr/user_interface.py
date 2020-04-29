import curses
import sys

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
        self.page = Page(self.app)
        self.search_string = ""

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

    def populate_screen(self):
        self.app.stdscr.clear()
        pyhstr_status = PYHSTR_STATUS.format(
            "sensitive" if self.app.case_sensitivity else "insensitive",
            self.app.user_interface.page.value,
            self.app.user_interface.page.total_pages()
        )
        entries = self.page.get_page()
        for index, entry in enumerate(entries):
            try:
                if index == self.app.user_interface.page.selected.value:
                    self._addstr(index + 3, 0, entry.ljust(curses.COLS), COLORS["highlighted-green"])
                else:
                    self._addstr(index + 3, 0, entry.ljust(curses.COLS), COLORS["normal"])
            except curses.error:
                pass

        self._addstr(1, 0, PYHSTR_LABEL, COLORS["normal"])
        self._addstr(2, 0, pyhstr_status.ljust(curses.COLS), COLORS["highlighted-white"])
        self._addstr(0, 0, f"{sys.ps1}{self.search_string}", COLORS["normal"])

    def prompt_for_deletion(self, command):
        prompt = f"Do you want to delete all occurences of {command}? y/n"
        self._addstr(1, 0, "".ljust(curses.COLS), COLORS["normal"])
        self._addstr(1, 0, prompt, COLORS["highlighted-red"])


class EntryCounter:
    def __init__(self, app):
        self.value = 0
        self.app = app

    def inc(self):
        page_size = self.app.user_interface.page.get_page_size()
        self.value += 1
        self.value %= page_size
        if self.value == 0:
            self.app.user_interface.page.inc()

    def dec(self):
        page_size = self.app.user_interface.page.get_page_size()
        self.value -= 1
        self.value %= page_size
        # in both places, we are subtracting 1 because indexing starts from zero
        if self.value == (page_size - 1):
            self.app.user_interface.page.dec()
            self.value = self.app.user_interface.page.get_page_size() - 1


class Page:
    def __init__(self, app):
        self.value = 1
        self.app = app
        self.selected = EntryCounter(self.app)

    def inc(self):
        """
        Paging starts from 1 but we want it to start at 0,
        because that's how our calculation with modulo works.

        So, if the indexing started from zero, we would have had:

        self.value = (self.value + 1) % total_pages

        ...which is increment and wrap around.

        Since we want the value to start at 1, we should:
        
        - subtract 1 from it when using it, because we want it to
        comply with the condition that page values start from 1,
        so we can use it in the modulo calculation (modulo needs
        zero-based indexing);
        
        - add 1 when setting it, because what modulo gives is 
        zero-based indexing, and we want to match the pages start
        from 1 condition.

        This gives:

        self.value = ((self.value - 1 + 1) % total_pages) + 1

        ... where -1+1 happens to cancel itself.
        """
        self.value = (self.value % self.total_pages()) + 1

    def dec(self):
        """
        See the docstring for inc().

        self.value = ((self.value - 1 - 1) % total_pages) + 1
        """
        self.value = ((self.value - 2) % self.total_pages()) + 1

    def total_pages(self):
        return len(range(0, len(self.app.all_entries), curses.LINES - 3))

    def get_page_size(self):
        return len(
            self.app.all_entries[
                (self.value - 1) * (curses.LINES - 3) : self.value * (curses.LINES - 3)
            ]
        )

    def get_page(self):
        return self.app.all_entries[
            (self.value - 1) * self.get_page_size() : self.value * self.get_page_size()
        ]
    
    def get_selected(self):
        return self.get_page()[self.selected.value]
