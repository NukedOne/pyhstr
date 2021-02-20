# pylint: disable=too-few-public-methods
# pylint: disable=invalid-name
# pylint: disable=no-self-use
# pylint: disable=unused-argument

from pathlib import Path
import os
import random
import shutil
import string
import pytest

from pyhstr import (
    __main__,
    application,
    utilities,
    user_interface,
)
from pyhstr.utilities import Shell, read, write


class FakeReadline:
    def __init__(self):
        self.history = read("tests/history/fake_python_history")

    def get_history_item(self, i):
        return self.history[i - 1]

    def remove_history_item(self, i):
        self.history.pop(i)

    def write_history_file(self, path):
        write(Path(path), self.history)

    def get_current_history_length(self):
        return len(self.history)

class FakeCurses:
    LINES = 10
    COLS = 80

    COLOR_BLACK = 0
    COLOR_RED = 1
    COLOR_GREEN = 2
    COLOR_CYAN = 6
    COLOR_WHITE = 7

    A_BOLD = 1 << (13 + 8)

    class error(Exception):
        pass

    def __init__(self):
        self.color_pairs = {}

    def init_pair(self, idx, fg, bg):
        self.color_pairs[idx] = (fg, bg)

    def color_pair(self, idx):
        return idx << (0 + 8)


class FakeStdscr:
    def __init__(self):
        self.addstred = []
        self.addched = []

    def addstr(self, *args):
        self.addstred.append(args)

    def addch(self, *args):
        self.addched.append(args)

    def box(self, *args):
        pass

    def timeout(self, *args):
        pass

    def subwin(self, *args):
        return FakeStdscr()

    def clear(self):
        pass

    def erase(self):
        pass

    def refresh(self):
        pass

    def getch(self):
        pass

    def nodelay(self, *args):
        pass

    def attron(self, *args):
        pass

    def attroff(self, *args):
        pass

    def getmaxyx(self):
        return FakeCurses.LINES, FakeCurses.COLS


def fake_get_terminal_size(*args, **kwargs):
    return FakeCurses.COLS, FakeCurses.LINES


@pytest.fixture
def fake_readline(monkeypatch):
    monkeypatch.setattr(application, "readline", FakeReadline())


@pytest.fixture
def fake_curses(monkeypatch):
    fc = FakeCurses()
    monkeypatch.setattr(__main__, "curses", fc)
    monkeypatch.setattr(user_interface, "curses", fc)
    monkeypatch.setattr(shutil, "get_terminal_size", fake_get_terminal_size)
    return fc


@pytest.fixture
def fake_stdscr():
    return FakeStdscr()


class FakeTermios:
    TIOCSTI = None


class FakeFcntl:
    def __init__(self):
        self.echoed = []

    def ioctl(self, *args):
        self.echoed.append(args)


@pytest.fixture
def fake_fcntl(monkeypatch):
    fake_f = FakeFcntl()
    monkeypatch.setattr(utilities, "ioctl", fake_f.ioctl)
    return fake_f


@pytest.fixture
def fake_termios(monkeypatch):
    monkeypatch.setattr(utilities, "TIOCSTI", FakeTermios().TIOCSTI)


def fake_get_ipython_history():
    return read(application.SHELLS[Shell.IPYTHON]["hist"])


@pytest.fixture
def fake_ipython(monkeypatch):
    monkeypatch.setattr(application, "SHELL", Shell.IPYTHON)
    monkeypatch.setattr(application, "get_ipython_history", fake_get_ipython_history)
    monkeypatch.setitem(
        application.SHELLS,
        Shell.IPYTHON,
        {
            "hist": Path("tests/history/fake_ipython_history"),
            "fav": Path("tests/favorites/fake_ipython_favorites"),
        },
    )


@pytest.fixture
def fake_bpython(monkeypatch):
    monkeypatch.setattr(application, "SHELL", Shell.BPYTHON)
    monkeypatch.setattr(help, "__module__", "bpython")
    monkeypatch.setitem(
        application.SHELLS,
        Shell.BPYTHON,
        {
            "hist": Path("tests/history/fake_bpython_history"),
            "fav": Path("tests/favorites/fake_bpython_favorites"),
        },
    )


@pytest.fixture
def fake_standard(monkeypatch):
    monkeypatch.setattr(application, "SHELL", Shell.STANDARD)
    monkeypatch.setitem(
        application.SHELLS,
        Shell.STANDARD,
        {
            "hist": Path("tests/history/fake_python_history"),
            "fav": Path("tests/favorites/fake_python_favorites"),
        },
    )


@pytest.fixture
def random_history(request):
    length = request.node.get_closest_marker("history_length").args[0]
    chars = string.ascii_letters + string.digits + r"!@#$%^&*()_+,./;'\\[]<>?:\"|{}"
    return [
        "".join([random.choice(chars) for _ in range(random.randint(40, 80))])
        for _ in range(length)
    ]


params = [
    pytest.param(
        Shell.STANDARD,
        pytest.lazy_fixture("fake_standard"),
        marks=[
            pytest.mark.skipif(
                os.environ["PYTHON_SHELL"] != "python",
                reason="standard only",
            ),
            pytest.mark.python,
        ],
    ),
    pytest.param(
        Shell.BPYTHON,
        pytest.lazy_fixture("fake_bpython"),
        marks=[
            pytest.mark.skipif(
                os.environ["PYTHON_SHELL"] != "bpython",
                reason="bpython only",
            ),
            pytest.mark.bpython,
        ],
    ),
    pytest.param(
        Shell.IPYTHON,
        pytest.lazy_fixture("fake_ipython"),
        marks=[
            pytest.mark.skipif(
                os.environ["PYTHON_SHELL"] != "ipython",
                reason="ipython only",
            ),
            pytest.mark.ipython,
        ],
    ),
]
