import curses
import sys
from typing import Dict, List, Union, TYPE_CHECKING
from pyhstr.utilities import View

if TYPE_CHECKING:
    from pyhstr.application import App  # pylint: disable=cyclic-import


COLORS: Dict[str, int] = {
    # yet to be initialized
    "normal": 0,
    "highlighted-white": 0,
    "highlighted-green": 0,
    "highlighted-red": 0,
    "white": 0,
    "bold-red": 0,
}

PYHSTR_LABEL = (
    "Type to filter, UP/DOWN move, RET/TAB select, DEL remove, ESC quit, C-f add/rm fav"
)
PYHSTR_STATUS = "- view:{} (C-/) - regex:{} (C-e) - case:{} (C-t) - page {}/{} -"

PS1 = getattr(sys, "ps1", ">>> ")

DISPLAY: Dict[str, Dict[Union[View, bool], str]] = {
    "view": {
        View.SORTED: "sorted",
        View.FAVORITES: "favorites",
        View.ALL: "history",
    },
    "case": {
        True: "sensitive",
        False: "insensitive",
    },
    "regex_mode": {
        True: "on",
        False: "off",
    },
}


class UserInterface:
    def __init__(self, app: "App"):
        self.app = app
        self.page = Page(self.app)

    def _addstr(self, y_coord: int, x_coord: int, text: str, color_info: int) -> None:
        """
        Works around curses' limitation of drawing at bottom right corner
        of the screen, as seen on https://stackoverflow.com/q/36387625
        """
        screen_height: int
        screen_width: int
        screen_height, screen_width = self.app.stdscr.getmaxyx()
        if x_coord + len(text) == screen_width and y_coord == screen_height - 1:
            try:
                self.app.stdscr.addstr(y_coord, x_coord, text, color_info)
            except curses.error:
                pass
        else:
            self.app.stdscr.addstr(y_coord, x_coord, text, color_info)

    @staticmethod
    def init_color_pairs() -> None:
        mapping: Dict[int, List[int]] = {
            1: [curses.COLOR_WHITE, curses.COLOR_BLACK],
            2: [curses.COLOR_BLACK, curses.COLOR_WHITE],
            3: [curses.COLOR_WHITE, curses.COLOR_GREEN],
            4: [curses.COLOR_WHITE, curses.COLOR_RED],
            5: [curses.COLOR_CYAN, curses.COLOR_BLACK],
            6: [curses.COLOR_RED, curses.COLOR_BLACK, curses.A_BOLD],
        }

        for idx, color in enumerate(COLORS, 1):
            curses.init_pair(idx, mapping[idx][0], mapping[idx][1])
            if len(mapping[idx]) > 2:
                COLORS[color] = curses.color_pair(idx) | mapping[idx][2]
            else:
                COLORS[color] = curses.color_pair(idx)

    def populate_screen(self) -> None:
        current_page = self.app.user_interface.page.value
        total_pages = self.app.user_interface.page.total_pages()

        status = PYHSTR_STATUS.format(
            DISPLAY["view"][self.app.view],
            DISPLAY["regex_mode"][self.app.regex_mode],
            DISPLAY["case"][self.app.case_sensitivity],
            current_page if total_pages > 0 else 0,
            total_pages,
        ).ljust(curses.COLS - 1)

        cmds = self.page.get_commands()

        for cmd_idx, cmd in enumerate(cmds):
            # print everything first (normal),
            # then print found matches (in red)
            # then print favorites (white)
            # then print selected on top of all that (green)
            try:
                padded_cmd = cmd.ljust(curses.COLS - 1)
                self._addstr(cmd_idx + 3, 1, padded_cmd, COLORS["normal"])
                matched_chars = self.get_matched_chars(cmd)

                if matched_chars:
                    for char_idx, char in enumerate(cmd):
                        if char_idx in matched_chars:
                            self.app.stdscr.attron(COLORS["bold-red"])
                            self.app.stdscr.addch(cmd_idx + 3, char_idx + 1, char)
                            self.app.stdscr.attroff(COLORS["bold-red"])

                if cmd in self.app.commands[View.FAVORITES]:
                    self._addstr(cmd_idx + 3, 1, padded_cmd, COLORS["white"])

                if cmd_idx == self.app.user_interface.page.selected.value:
                    self._addstr(
                        cmd_idx + 3, 1, padded_cmd, COLORS["highlighted-green"]
                    )
            except curses.error:
                pass

        self._addstr(1, 1, PYHSTR_LABEL, COLORS["normal"])
        self._addstr(2, 1, status, COLORS["highlighted-white"])
        self._addstr(0, 1, PS1 + self.app.search_string, COLORS["normal"])

    def prompt_for_deletion(self, command: str) -> None:
        prompt = f"Do you want to delete all occurences of {command}? y/n"
        self._addstr(1, 0, "".ljust(curses.COLS), COLORS["normal"])
        self._addstr(1, 1, prompt, COLORS["highlighted-red"])

    def show_regex_error(self) -> None:
        prompt = "Invalid regex. Try again."
        self._addstr(1, 0, "".ljust(curses.COLS), COLORS["normal"])
        self._addstr(1, 1, prompt, COLORS["highlighted-red"])
        self._addstr(0, 1, PS1 + self.app.search_string, COLORS["normal"])

    def get_matched_chars(self, command: str) -> List[int]:
        regex = self.app.create_search_regex()
        return (
            []
            if regex is None
            else [
                cmd_idx
                for m in regex.finditer(command)
                for cmd_idx in range(m.start(), m.end())
            ]
        )


class Page:
    def __init__(self, app: "App"):
        self.value = 1
        self.app = app
        self.selected = SelectedCmd(self)

    def turn(self, direction: int) -> None:
        """
        Paging starts from 1 but we want it to start at 0,
        because that's how our calculation with modulo works.

        So, if the cmd_idxing started from zero, we would have had:

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
        self.app.stdscr.clear()
        self.value = ((self.value - 1 + direction) % self.total_pages()) + 1

    def total_pages(self) -> int:
        return len(range(0, len(self.app.commands[self.app.view]), curses.LINES - 3))

    def get_size(self) -> int:
        return len(self.get_commands())

    def get_commands(self) -> List[str]:
        return self.app.commands[self.app.view][
            (self.value - 1) * (curses.LINES - 3) : self.value * (curses.LINES - 3)
        ]

    def get_selected(self) -> str:
        return self.get_commands()[self.selected.value]


class SelectedCmd:  # pylint: disable=too-few-public-methods
    def __init__(self, page: Page):
        self.value = 0
        self.page = page

    def move(self, direction: int) -> None:
        page_size = self.page.get_size()
        self.value += direction

        try:
            self.value %= page_size
        except ZeroDivisionError:
            return None

        if direction == 1 and self.value == 0:
            self.page.turn(1)
        elif direction == -1 and self.value == (page_size - 1):
            self.page.turn(-1)
            self.value = self.page.get_size() - 1
