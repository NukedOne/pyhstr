import curses
import more_itertools


class Writer:
    def write(self, path, thing):
        with open(path, "w") as f:
            for thingy in thing:
                print(thingy, file=f)


class Reader:
    def read(self, path):
        history = []
        with open(path, "r") as f:
            for command in f:
                command = command.strip()
                if command not in history:
                    history.append(command)
        return list(more_itertools.sliced(history, curses.LINES - 3)) # account for 3 lines at the top
