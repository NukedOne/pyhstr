"""History manager extension for the standard Python shell and IPython"""

__version__ = "0.5.1"

import curses
import sys

try:
    import IPython
except ModuleNotFoundError:  # pragma: no cover
    IPython = None

from pyhstr.__main__ import main
from pyhstr.application import SHELL
from pyhstr.utilities import Shell

hh = object()
original = sys.displayhook


def spam(arg: object) -> None:
    if arg == hh:
        curses.wrapper(main)
    else:
        original(arg)


if SHELL != Shell.IPYTHON:
    sys.displayhook = spam
else:

    @IPython.core.magic.register_line_magic
    def hh(line: str) -> None:  # pylint: disable=function-redefined,unused-argument
        """
        This line magic mirrors the behaviour of sys.displayhook
        in the regular Python shell. Use %hh to invoke.
        """
        curses.wrapper(main)
