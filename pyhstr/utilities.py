import collections
import fcntl
import termios
import pathlib


def sort(thing):
    return [
        x[0] for x in sorted(
            collections.Counter(thing).items(), key=lambda y: -y[1]
        )
    ]


def write(path, thing):
    with open(path, "w") as f:
        for thingy in thing:
            print(thingy, file=f)


def read(path):
    try:
        history = []
        with open(path, "r") as f:
            for command in f:
                history.append(command.strip())
        return history
    except FileNotFoundError as e:
        pathlib.Path(e.filename).touch()


def echo(command):
    command = command.encode("utf-8")
    for byte in command:
        fcntl.ioctl(0, termios.TIOCSTI, bytes([byte]))


def remove_duplicates(thing):
    without_duplicates = []
    for thingy in thing:
        if thingy not in without_duplicates:
            without_duplicates.append(thingy)
    return without_duplicates
