# pylint: disable=unused-argument
# pylint: disable=unused-import
# pylint: disable=redefined-outer-name
# pylint: disable=too-many-arguments


import pytest

from pyhstr.application import App
from pyhstr.user_interface import (
    COLORS,
    Direction,
    Page,
    UserInterface,
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
        [0, Direction.NEXT, 1, 1],
        [1, Direction.NEXT, 2, 1],
        [2, Direction.NEXT, 3, 1],
        [3, Direction.NEXT, 4, 1],
        [4, Direction.NEXT, 5, 1],
        [5, Direction.NEXT, 6, 1],
        [6, Direction.NEXT, 0, 2],
        [6, Direction.PREVIOUS, 5, 1],
        [5, Direction.PREVIOUS, 4, 1],
        [4, Direction.PREVIOUS, 3, 1],
        [3, Direction.PREVIOUS, 2, 1],
        [2, Direction.PREVIOUS, 1, 1],
        [1, Direction.PREVIOUS, 0, 1],
        [0, Direction.PREVIOUS, 3, 4],
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
    page = Page(App(fake_stdscr))
    page.selected = current_selected
    page.move_selected(direction)
    assert page.selected == expected_selected
    assert page.value == expected_page


@pytest.mark.all
@pytest.mark.parametrize(
    "current, direction, expected",
    [
        [1, Direction.NEXT, 2],
        [2, Direction.NEXT, 3],
        [3, Direction.NEXT, 4],
        [4, Direction.NEXT, 1],
        [4, Direction.PREVIOUS, 3],
        [3, Direction.PREVIOUS, 2],
        [2, Direction.PREVIOUS, 1],
        [1, Direction.PREVIOUS, 4],
    ]
)
def test_page_turn(
    current,
    direction,
    expected,
    fake_curses,
    fake_stdscr,
    fake_standard,
):
    page = Page(App(fake_stdscr))
    page.value = current
    page.turn(direction)
    assert page.value == expected


@pytest.mark.all
def test_total_pages(fake_curses, fake_stdscr, fake_standard):
    user_interface = UserInterface(App(fake_stdscr))
    assert user_interface.total_pages() == 4


@pytest.mark.all
def test_page_get_size(fake_curses, fake_stdscr, fake_standard):
    page = Page(App(fake_stdscr))
    assert page.get_size() == 7


@pytest.mark.all
def test_page_get_commands(fake_curses, fake_stdscr, fake_standard):
    page = Page(App(fake_stdscr))
    assert page.get_commands() == [
        'print("SPAM")',
        'assert hasattr(subprocess, \'run\'), "install a newer python lel"',
        '__import__("math").pi',
        'print(sys.executable)',
        'print(sys.argv)',
        'from math import tau',
        '[x for x in range(100)]',
    ]


@pytest.mark.all
def test_page_get_selected(fake_curses, fake_stdscr, fake_standard):
    page = Page(App(fake_stdscr))
    page.selected = 2
    assert page.get_selected() == '__import__("math").pi'


@pytest.mark.all
def test_prompt_for_deletion(fake_curses, fake_stdscr, fake_standard):
    user_interface = UserInterface(App(fake_stdscr))
    command = '__import__("math").pi'
    user_interface.prompt_for_deletion(command)
    assert (
        1, 1, f"Do you want to delete all occurences of {command}? y/n", 0
     ) in fake_stdscr.addstred


@pytest.mark.all
def test_show_regex_error(fake_curses, fake_stdscr, fake_standard):
    user_interface = UserInterface(App(fake_stdscr))
    user_interface.show_regex_error()
    assert (
        1, 1, "Invalid regex. Try again.", 0
     ) in fake_stdscr.addstred


@pytest.mark.all
def test_init_color_pairs(fake_curses, fake_stdscr):
    user_interface = UserInterface(App(fake_stdscr))
    user_interface.init_color_pairs()
    for v in COLORS.values():
        assert v != 0
