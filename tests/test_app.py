# pylint: disable=unused-argument
# pylint: disable=unused-import
# pylint: disable=redefined-outer-name
# pylint: disable=too-many-arguments


import os
import shutil
import pytest
from pyhstr import application
from pyhstr.application import App
from pyhstr.utilities import (
    Shell,
    View,
    read,
)

from tests.fixtures import (
    fake_curses,
    fake_stdscr,
    fake_bpython,
    fake_ipython,
    fake_readline,
    fake_standard,
    params,
)


@pytest.mark.python
@pytest.mark.parametrize("command", ["1 + 1 == 2", 'ord("r")', "print(sys.argv)"])
def test_delete_python_history(
    command, fake_stdscr, fake_standard, fake_readline, tmp_path
):
    shutil.copyfile("tests/history/fake_python_history", tmp_path / "history")
    app = App(fake_stdscr)
    app.delete_python_history(command)
    assert command not in read("tests/history/fake_python_history")
    shutil.move(tmp_path / "history", "tests/history/fake_python_history")


@pytest.mark.all
def test_create_search_regex_none(fake_stdscr):
    app = App(fake_stdscr)
    app.regex_mode = True
    app.search_string = "print("
    assert app.create_search_regex() is None


@pytest.mark.all
@pytest.mark.parametrize(
    "search_string, expected, regex_mode, case_sensitivity",
    [
        [
            "spam",
            ['"spam".encode("utf-8")', 'print("SPAM")'],
            False,
            False,
        ],
        [
            "SPAM",
            ['print("SPAM")'],
            False,
            True,
        ],
        [
            "spam",
            ['"spam".encode("utf-8")'],
            False,
            True,
        ],
        [
            "[0-9]+",
            [
                '"spam".encode("utf-8")',
                "[x for x in range(100) if x % 2]",
                "1 + 1 == 2",
                "tau == 2 * pi",
                "4 / 2",
                "2 ** 10",
                "[x for x in range(100)]",
            ],
            True,
            False,
        ],
    ],
)
def test_search(
    search_string,
    expected,
    regex_mode,
    case_sensitivity,
    fake_stdscr,
    fake_curses,
    fake_standard,
):
    app = App(fake_stdscr)
    app.search_string = search_string
    app.regex_mode = regex_mode
    app.case_sensitivity = case_sensitivity
    app.search()
    assert all(x in expected for x in app.commands[app.view])


@pytest.mark.parametrize("shell, fixture", params)
def test_get_history(shell, fixture, fake_stdscr):
    app = App(fake_stdscr)
    assert app.get_history() == read(f"tests/history/fake_{shell.value}_history")


@pytest.mark.all
@pytest.mark.parametrize("regex_mode", [True, False])
def test_toggle_regex_mode(regex_mode, fake_stdscr):
    app = App(fake_stdscr)
    app.regex_mode = regex_mode
    app.toggle_regex_mode()
    assert app.regex_mode == (not regex_mode)


@pytest.mark.all
@pytest.mark.parametrize("case", [True, False])
def test_toggle_case(case, fake_stdscr):
    app = App(fake_stdscr)
    app.case_sensitivity = case
    app.toggle_case()
    assert app.case_sensitivity == (not case)


@pytest.mark.all
@pytest.mark.parametrize(
    "before, expected",
    [
        [View.SORTED, View.FAVORITES],
        [View.FAVORITES, View.ALL],
        [View.ALL, View.SORTED],
    ],
)
def test_toggle_view(before, expected, fake_stdscr):
    app = App(fake_stdscr)
    app.view = before
    app.toggle_view()
    assert app.view == expected


@pytest.mark.parametrize("shell, fixture", params)
def test_add_or_rm_fav(shell, fixture, fake_stdscr):
    app = App(fake_stdscr)
    path = application.SHELLS[shell]["fav"]
    for value in (True, False):
        app.add_or_rm_fav("egg")
        favs = read(path)
        assert favs.__contains__("egg") == value
