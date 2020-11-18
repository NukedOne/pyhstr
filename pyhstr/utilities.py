import collections
import enum
import fcntl
import pathlib
import termios
from typing import List, Optional
import sys


def sort(thing: List[str]) -> List[str]:
    return [
        x for x, _ in collections.Counter(thing).most_common()
    ]


def write(path: Optional[pathlib.Path], thing: List[str]) -> None:
    assert path is not None
    with open(path, "w") as f:
        for thingy in thing:
            print(thingy, file=f)


def read(path: Optional[pathlib.Path]) -> List[str]:
    assert path is not None
    try:
        with open(path, "r") as f:
            return [command.strip() for command in f]
    except FileNotFoundError as e:
        pathlib.Path(e.filename).touch()
        return [""]


def echo(command: str) -> None:
    for byte in command.encode("utf-8"):
        fcntl.ioctl(0, termios.TIOCSTI, bytes([byte]))


def remove_duplicates(thing: List[str]) -> List[str]:
    return list(collections.OrderedDict.fromkeys(thing))


def get_ipython_history() -> List[str]:
    import IPython
    return [
        entry for session_number, line_number, entry in
        IPython.get_ipython().history_manager.search()
    ]


def get_bpython_history_path() -> Optional[pathlib.Path]:
    try:
        from bpython.config import get_config_home, loadini, Struct
        config = Struct()
        loadini(config, pathlib.Path(get_config_home()).expanduser() / "config")
        return pathlib.Path(config.hist_file).expanduser()
    except ImportError:
        return None


class Shell(enum.Enum):
    STANDARD = "python"
    IPYTHON = "ipython"
    BPYTHON = "bpython"


def detect_shell() -> Shell:
    try:
        import IPython
        if IPython.get_ipython() is not None:
            return Shell.IPYTHON
    except ImportError:
        pass
    exe = pathlib.Path(sys.argv[0]).name
    if exe == Shell.BPYTHON.value:
        return Shell.BPYTHON
    return Shell.STANDARD
