import collections
import fcntl
import termios


class EntryCounter:
    def __init__(self, app):
        self.value = 0
        self.app = app

    def inc(self, page_size):
        self.value += 1
        self.value = self.value % page_size
        if self.value == 0:
            self.app.page.inc(self.app.user_interface.get_number_of_pages())

    def dec(self, page_size):
        self.value -= 1
        self.value = self.value % page_size
        # in both places, we are subtracting -1
        # because indexing starts from zero
        if self.value == (page_size - 1):
            self.app.page.dec(self.app.user_interface.get_number_of_pages())
            self.value = self.app.user_interface.get_page_size(self.app.page.value) - 1

class PageCounter:
    def __init__(self):
        self.value = 1

    def inc(self, total_pages):
        if self.value == total_pages:
            self.value = 1
        else:
            self.value += 1

    def dec(self, total_pages):
        if self.value == 1:
            self.value = total_pages
        else:
            self.value -= 1


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
