# pyhstr

**pyhstr** is history suggest box for the standard Python shell.
It also works with IPython and bpython. Inspired by hstr.

### Installation

```bash
pip install pyhstr
```

### Usage

This currently works for the standard and IPython shells.
In standard shell and bpython, just first import `hh` from `pyhstr`, and then use `hh` to invoke the program. 
In IPython, it's enough to import `pyhstr` and then use `%hh`.

Making an alias should be more convenient though:

```bash
alias py='python3 -ic "from pyhstr import hh"'
```

![screenshot](pyhstr.gif)
