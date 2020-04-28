import collections
import fcntl
import termios


class EntryCounter:
    def __init__(self, app):
        self.value = 0
        self.app = app

    def inc(self):
        page_size = self.app.user_interface.get_page_size()
        self.value += 1
        self.value %= page_size
        if self.value == 0:
            self.app.page.inc()

    def dec(self):
        page_size = self.app.user_interface.get_page_size()
        self.value -= 1
        self.value %= page_size
        # in both places, we are subtracting 1 because indexing starts from zero
        if self.value == (page_size - 1):
            self.app.page.dec()
            self.value = self.app.user_interface.get_page_size() - 1

class PageCounter:
    def __init__(self, app):
        self.value = 1
        self.app = app

    def inc(self):
        """
        Paging starts from 1 but we want it to start at 0,
        because that's how our calculation with modulo works.

        So, if the indexing started from zero, we would have had:

        self.value = (self.value + 1) % total_pages

        ...which is increment and wrap around.

        Since we want the value to start at 1, we should:
            - subtract 1 from it when using it, because we want it to
            comply with the condition that page values start from 1,
            so we can use it in the modulo calculation (modulo needs
            zero-based indexing);
            - add 1 when setting it, because what modulo gives is 
            zero-based indexing, and we want to match the pages start
            from 1 condition.

        This gives:

        self.value = ((self.value - 1 + 1) % total_pages) + 1

        ... where -1+1 happens to cancel itself.
        """
        self.value = (self.value % self.app.user_interface.total_pages()) + 1

    def dec(self):
        """
        See the docstring for inc().

        self.value = ((self.value - 1 - 1) % total_pages) + 1
        """
        self.value = ((self.value - 2) % self.app.user_interface.total_pages()) + 1

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
