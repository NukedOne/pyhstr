# pylint: disable=unused-argument
# pylint: disable=unused-import
# pylint: disable=redefined-outer-name
# pylint: disable=too-many-arguments


import pytest

from pyhstr.application import App
from pyhstr.user_interface import (
    Page,
    SelectedCmd,
)
from tests.fixtures import (
    fake_curses,
    fake_standard,
    fake_stdscr,
)


@pytest.mark.all
@pytest.mark.parametrize(
    "current_selected, direction, expected_selected, expected_page",
    [
        [0, 1, 1, 1],
        [1, 1, 2, 1],
        [2, 1, 3, 1],
        [3, 1, 4, 1],
        [4, 1, 5, 1],
        [5, 1, 6, 1],
        [6, 1, 0, 2],
        [6, -1, 5, 1],
        [5, -1, 4, 1],
        [4, -1, 3, 1],
        [3, -1, 2, 1],
        [2, -1, 1, 1],
        [1, -1, 0, 1],
        [0, -1, 3, 4],
    ],
)
def test_selected_move(
    current_selected,
    direction,
    expected_selected,
    expected_page,
    fake_curses,
    fake_stdscr,
    fake_standard,
):
    selected = SelectedCmd(Page(App(fake_stdscr)))
    selected.value = current_selected
    selected.move(direction)
    assert selected.value == expected_selected
    assert selected.page.value == expected_page
