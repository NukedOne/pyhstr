import re
import readline

from pathlib import Path
from typing import Any, Dict, List, Optional, Pattern, TYPE_CHECKING

try:
    import IPython
except ModuleNotFoundError:  # pragma: no cover
    IPython = None

from pyhstr.user_interface import UserInterface
from pyhstr.utilities import (
    Shell,
    View,
    detect_shell,
    get_bpython_history_path,
    get_ipython_history,
    read,
    remove_duplicates,
    sort,
    write,
)

if TYPE_CHECKING:
    from _curses import _CursesWindow  # pylint: disable=no-name-in-module
else:
    _CursesWindow = Any


SHELL = detect_shell()

SHELLS: Dict[Shell, Dict[str, Optional[Path]]] = {
    Shell.IPYTHON: {
        "hist": None,
        "fav": Path("~/.config/pyhstr/ipython_favorites").expanduser(),
    },
    Shell.BPYTHON: {
        "hist": get_bpython_history_path(),
        "fav": Path("~/.config/pyhstr/bpython_favorites").expanduser(),
    },
    Shell.STANDARD: {
        "hist": Path("~/.python_history").expanduser(),
        "fav": Path("~/.config/pyhstr/python_favorites").expanduser(),
    },
}


class App:
    def __init__(self, stdscr: _CursesWindow):
        self.stdscr = stdscr
        self.user_interface = UserInterface(self)
        self.raw_history: List[str] = self.get_history()
        self.commands: Dict[View, List[str]] = {
            View.SORTED: sort(self.raw_history),
            View.FAVORITES: sort(read(SHELLS[SHELL]["fav"])),
            View.ALL: remove_duplicates(self.raw_history),
        }
        self.to_restore = self.commands.copy()
        self.regex_mode: bool = False
        self.case_sensitivity: bool = False
        self.view: View = View.SORTED
        self.search_string = ""

    def get_history(self) -> List[str]:  # pylint: disable=no-self-use
        if SHELL == Shell.IPYTHON:
            return get_ipython_history()
        return read(SHELLS[SHELL]["hist"])

    def search(self) -> None:
        self.user_interface.page.selected.value = 0
        self.user_interface.page.value = 1

        search_regex = self.create_search_regex()

        if search_regex is not None:
            self.commands[self.view] = [
                cmd for cmd in self.commands[self.view] if search_regex.search(cmd)
            ]
            self.stdscr.clear()
            self.user_interface.populate_screen()
        else:
            self.commands[self.view] = []
            self.stdscr.clear()
            self.user_interface.populate_screen()
            self.user_interface.show_regex_error()

    def create_search_regex(self) -> Optional[Pattern]:
        try:
            search_string = (
                self.search_string if self.regex_mode else re.escape(self.search_string)
            )
            return re.compile(
                search_string, re.IGNORECASE if not self.case_sensitivity else 0
            )
        except re.error:
            return None

    def delete_python_history(self, command: str) -> None:  # pylint: disable=no-self-use
        readline_history = [
            readline.get_history_item(i + 1)
            for i in range(readline.get_current_history_length())
        ]

        cmd_indexes = [i for i, cmd in enumerate(readline_history) if cmd == command]

        for cmd_idx in reversed(cmd_indexes):
            readline.remove_history_item(cmd_idx)

        readline.write_history_file(str(SHELLS[Shell.STANDARD]["hist"]))

    def delete_ipython_history(self, command: str) -> None:  # pylint: disable=no-self-use
        IPython.get_ipython().history_manager.db.execute(
            "DELETE FROM history WHERE source=(?)", (command,)
        )

    def delete_bpython_history(self, command: str) -> None:
        self.raw_history = [cmd for cmd in self.raw_history if cmd != command]
        write(SHELLS[Shell.BPYTHON]["hist"], self.raw_history)

    def delete_from_history(self, command: str) -> None:
        if SHELL == Shell.STANDARD:
            self.delete_python_history(command)
        elif SHELL == Shell.IPYTHON:
            self.delete_ipython_history(command)
        elif SHELL == Shell.BPYTHON:
            self.delete_bpython_history(command)
        else:
            pass  # future implementations

        for view in self.commands.values():
            for cmd in view:
                if cmd == command:
                    view.remove(cmd)

        self.to_restore = self.commands.copy()

    def add_or_rm_fav(self, command: str) -> None:
        if command not in self.commands[View.FAVORITES]:
            self.commands[View.FAVORITES].append(command)
        else:
            self.commands[View.FAVORITES].remove(command)

    def toggle_regex_mode(self) -> None:
        self.regex_mode = not self.regex_mode

    def toggle_case(self) -> None:
        self.case_sensitivity = not self.case_sensitivity

    def toggle_view(self) -> None:
        self.view = View((self.view.value + 1) % 3)
