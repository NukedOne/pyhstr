# pylint: disable=redefined-outer-name
# pylint: disable=unused-argument
# pylint: disable=unused-import

import os
import pytest

from pyhstr import utilities
from pyhstr.utilities import (
    Shell,
    detect_shell,
    echo,
    get_bpython_history_path,
    get_ipython_history,
    read,
    remove_duplicates,
    sort,
    write,
)

from tests.fixtures import (
    fake_bpython,
    fake_fcntl,
    fake_ipython,
    fake_standard,
    fake_termios,
    random_history,
    params,
)


@pytest.mark.all
def test_sort():
    history = [3, 2, 4, 6, 2, 4, 3, 3, 4, 5, 6, 3, 2, 4, 5, 5, 3]
    assert sort(history) == [3, 4, 5, 2, 6]


@pytest.mark.all
def test_remove_duplicates():
    history = [3, 2, 4, 6, 2, 4, 3, 3, 4, 5, 6, 3, 2, 4, 5, 5, 3]
    assert remove_duplicates(history) == [3, 2, 4, 6, 5]


@pytest.mark.parametrize("shell, fixture", params)
def test_detect_shell(shell, fixture):
    assert detect_shell() == shell


@pytest.mark.bpython
def test_get_bpython_history_path():
    assert get_bpython_history_path() is not None


@pytest.mark.bpython
def test_get_bpython_history_path_none(monkeypatch):
    monkeypatch.setattr(utilities, "Struct", None)
    assert get_bpython_history_path() is None


@pytest.mark.ipython
@pytest.mark.skipif(os.environ["PYTHON_SHELL"] != "ipython", reason="ipython only")
def test_get_ipython_history(fake_ipython):
    history = get_ipython_history()
    assert isinstance(history, list)


@pytest.mark.all
@pytest.mark.history_length(100)
def test_echo(fake_fcntl, fake_termios, random_history):
    for command in random_history:
        echo(command)
        for byte in command.encode("utf-8"):
            assert (0, None, bytes([byte])) in fake_fcntl.echoed


@pytest.mark.all
@pytest.mark.history_length(100)
def test_write(tmp_path, random_history):
    with pytest.raises(AssertionError):
        write(None, random_history)
    path = tmp_path / "spam"
    write(path, random_history)
    assert (path).exists()


@pytest.mark.all
def test_read_none():
    with pytest.raises(AssertionError):
        read(None)


@pytest.mark.all
def test_read_file_creation(tmp_path):
    assert read(tmp_path / "spam") == [""]


@pytest.mark.all
def test_read_some(tmp_path):
    history = tmp_path / "spam"
    history.write_text("eggs")
    assert read(history) == ["eggs"]
