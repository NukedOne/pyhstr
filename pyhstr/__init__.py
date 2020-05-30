"""History manager extension for the standard Python shell"""

__version__ = '0.0.1'

import curses
import sys

from pyhstr.application import main

hh = object()
original = sys.displayhook

def spam(arg):
    if arg == hh:
        curses.wrapper(main)
    else:
        original(arg)

sys.displayhook = spam
