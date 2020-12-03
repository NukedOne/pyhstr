# pylint: disable=too-few-public-methods
# pylint: disable=invalid-name
# pylint: disable=no-self-use
# pylint: disable=unused-argument

from pathlib import Path
import os
import random
import string
import sys
import pytest

from pyhstr import (
    application,
    utilities,
)
from pyhstr.utilities import Shell, read


class FakeStdscr:
    def __init__(self):
        self.addstred = []

    def addstr(self, *args):
        self.addstred.append(args)

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
    monkeypatch.setattr(utilities, "fcntl", fake_f)
    return fake_f


@pytest.fixture
def fake_termios(monkeypatch):
    monkeypatch.setattr(utilities, "termios", FakeTermios())


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
    monkeypatch.setattr(sys, "argv", ["bpython"])
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
