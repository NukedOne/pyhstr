# pyhstr

**pyhstr** is history suggest box for the standard Python shell. Inspired by hstr.

### Installation

```bash
git clone https://github.com/xvm32/pyhstr.git
cd pyhstr
python3 -m pip install -e .
```

### Usage

You should make an alias:

```bash
alias py='python3 -ic "from pyhstr import hh"'
```

![screenshot](pyhstr.gif)

### FIXME 

- make it work for ipython (how do I set sys.displayhook on IPython? (help needed))
