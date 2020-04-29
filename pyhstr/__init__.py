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
