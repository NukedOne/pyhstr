import curses
from pyhstr.application import main


class SpamEggs:
    def __repr__(self):
        curses.wrapper(main)
        return '>>>'


hh = SpamEggs()