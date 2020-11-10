import collections
import enum
import fcntl
import pathlib
import termios
import sys


def sort(thing):
    return [
        x for x, _ in collections.Counter(thing).most_common()
    ]


def write(path, thing):
    with open(path, "w") as f:
        for thingy in thing:
            print(thingy, file=f)


def read(path):
    try:
        with open(path, "r") as f:
            return [command.strip() for command in f]
    except FileNotFoundError as e:
        pathlib.Path(e.filename).touch()


def echo(command):
    command = command.encode("utf-8")
    for byte in command:
        fcntl.ioctl(0, termios.TIOCSTI, bytes([byte]))


def remove_duplicates(thing):
    return list(dict.fromkeys(thing))


def get_ipython_history():
    import IPython
    return [
        entry for session_number, line_number, entry in
        IPython.get_ipython().history_manager.search()
    ]


class Shell(enum.Enum):
    STANDARD = "python"
    IPYTHON = "ipython"
    BPYTHON = "bpython"


def detect_shell():
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
