# pyhstr

**pyhstr** is history suggest box for the standard Python shell. Inspired by hstr.

### Installation

```bash
pip install pyhstr
```

### Usage

You need to import `hh` from `pyhstr` and then use `hh` to invoke the program. 

Making an alias should be more convenient though:

```bash
alias py='python3 -ic "from pyhstr import hh"'
```

![screenshot](pyhstr.gif)

### FIXME 

- make it work for ipython (how do I set sys.displayhook on IPython? (help needed))
