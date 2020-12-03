import collections
import enum
import fcntl
import sys
import termios
from pathlib import Path
from typing import List, Optional

try:
    import IPython
except ModuleNotFoundError:
    IPython = None

try:
    from bpython.config import (
        Struct,
        get_config_home,
        loadini,
    )
except ModuleNotFoundError:
    Struct = get_config_home = loadini = None


class Shell(enum.Enum):
    STANDARD = "python"
    IPYTHON = "ipython"
    BPYTHON = "bpython"


class View(enum.Enum):
    SORTED = 0
    FAVORITES = 1
    ALL = 2


def sort(thing: List[str]) -> List[str]:
    positions = {entry: position for position, entry in enumerate(thing)}
    frequencies = collections.Counter(thing)
    thing.sort(key=lambda x: positions[x], reverse=True)
    thing.sort(key=lambda x: frequencies[x], reverse=True)
    return remove_duplicates(thing)


def write(path: Optional[Path], thing: List[str]) -> None:
    assert path is not None
    with open(path, "w") as f:
        for thingy in thing:
            print(thingy, file=f)


def read(path: Optional[Path]) -> List[str]:
    assert path is not None
    try:
        with open(path, "r") as f:
            return [command.strip() for command in f]
    except FileNotFoundError:
        path.parent.mkdir(exist_ok=True)
        path.touch()
        return [""]


def echo(command: str) -> None:
    for byte in command.encode("utf-8"):
        fcntl.ioctl(0, termios.TIOCSTI, bytes([byte]))


def remove_duplicates(thing: List[str]) -> List[str]:
    return list(collections.OrderedDict.fromkeys(thing))


def get_ipython_history() -> List[str]:
    return [
        entry
        for session_number, line_number, entry in IPython.get_ipython().history_manager.search()
    ]


def get_bpython_history_path() -> Optional[Path]:
    if all(x is not None for x in {Struct, get_config_home, loadini}):
        config = Struct()
        loadini(config, Path(get_config_home()).expanduser() / "config")
        return Path(config.hist_file).expanduser()
    return None


def is_ipython():
    return IPython.get_ipython() is not None


def is_bpython():
    return Path(sys.argv[0]).name == Shell.BPYTHON.value


def detect_shell() -> Shell:
    if is_ipython():
        return Shell.IPYTHON
    elif is_bpython():
        return Shell.BPYTHON
    return Shell.STANDARD
