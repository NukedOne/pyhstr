# pylint: disable=unused-argument
# pylint: disable=unused-import
# pylint: disable=redefined-outer-name


import os
import pytest
from pyhstr import application
from pyhstr.application import App
from pyhstr.utilities import (
    Shell,
    View,
    read,
)

from tests.fixtures import (
    fake_stdscr,
    fake_bpython,
    fake_ipython,
    fake_standard,
    params,
)


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
