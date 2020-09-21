"""History manager extension for the standard Python shell and IPython"""

__version__ = '0.0.3'

import curses
import sys

from pyhstr.application import main, IS_IPYTHON

hh = object()
original = sys.displayhook

def spam(arg):
    if arg == hh:
        curses.wrapper(main)
    else:
        original(arg)

if not IS_IPYTHON:
    sys.displayhook = spam
else:
    from IPython.core.magic import register_line_magic

    @register_line_magic
    def hh(line):
        """
        This line magic mirrors the behaviour of sys.displayhook
        in the regular Python shell. Use %hh to invoke.
        """
        curses.wrapper(main)