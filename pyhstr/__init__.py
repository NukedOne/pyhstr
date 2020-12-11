"""History manager extension for the standard Python shell and IPython"""

__version__ = "0.4.1"

import curses
import sys

try:
    import IPython
except ModuleNotFoundError:  # pragma: no cover
    IPython = None

from pyhstr.application import SHELL, main
from pyhstr.utilities import Shell

hh = object()
original = sys.displayhook


def spam(arg):
    if arg == hh:
        curses.wrapper(main)
    else:
        original(arg)


if SHELL != Shell.IPYTHON:
    sys.displayhook = spam
else:

    @IPython.core.magic.register_line_magic
    def hh(line):  # pylint: disable=function-redefined,unused-argument
        """
        This line magic mirrors the behaviour of sys.displayhook
        in the regular Python shell. Use %hh to invoke.
        """
        curses.wrapper(main)
