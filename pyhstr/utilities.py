from collections import Counter, OrderedDict
from enum import Enum
from fcntl import ioctl
from termios import TIOCSTI
from pathlib import Path
from typing import List, Optional

try:
    import IPython
except ModuleNotFoundError:  # pragma: no cover
    IPython = None

try:
    from bpython.config import (
        Struct,
        get_config_home,
        loadini,
    )
except ModuleNotFoundError:  # pragma: no cover
    Struct = get_config_home = loadini = None


class Shell(Enum):
    STANDARD = "python"
    IPYTHON = "ipython"
    BPYTHON = "bpython"


class View(Enum):
    SORTED = 0
    FAVORITES = 1
    ALL = 2


def detect_shell() -> Shell:
    if _is_ipython():
        return Shell.IPYTHON
    elif _is_bpython():
        return Shell.BPYTHON
    return Shell.STANDARD


def _is_ipython() -> bool:
    return IPython is not None and IPython.get_ipython() is not None


def _is_bpython() -> bool:
    return help.__module__.startswith("bpython")


def sort(thing: List[str]) -> List[str]:
    return remove_duplicates(_sort_by_freq(_sort_by_pos(thing)))


def remove_duplicates(thing: List[str]) -> List[str]:
    return list(OrderedDict.fromkeys(thing))


def _sort_by_freq(thing: List[str]) -> List[str]:
    return sorted(
        thing,
        key=lambda item: Counter(thing)[item],
        reverse=True,
    )


def _sort_by_pos(thing: List[str]) -> List[str]:
    return sorted(
        thing,
        key=lambda item: {x: i for i, x in enumerate(thing)}[item],
        reverse=True,
    )


def echo(command: str) -> None:
    for byte in command.encode("utf-8"):
        ioctl(0, TIOCSTI, bytes([byte]))


def get_ipython_history() -> List[str]:
    return [
        entry
        for session_number, line_number, entry
        in IPython.get_ipython().history_manager.search()
    ]


def get_bpython_history_path() -> Optional[Path]:
    try:
        config = Struct()
        loadini(config, Path(get_config_home()).expanduser() / "config")
        return Path(config.hist_file).expanduser()
    except TypeError:
        return None


def write(path: Optional[Path], thing: List[str]) -> None:
    assert path is not None
    if not path.parent.exists():
        path.parent.mkdir(exist_ok=True)
    with open(path, "w") as f:
        for thingy in thing:
            print(thingy, file=f)


def read(path: Optional[Path]) -> List[str]:
    assert path is not None
    try:
        with open(path, "r") as f:
            return [command.strip() for command in f]
    except FileNotFoundError:
        return [""]
