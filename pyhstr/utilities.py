import collections
import fcntl
import termios


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
    history = []
    with open(path, "r") as f:
        for command in f:
            history.append(command.strip())
    return history


def echo(command):
    command = command.encode("utf-8")
    for byte in command:
        fcntl.ioctl(0, termios.TIOCSTI, bytes([byte]))
