# pyhstr

Work in progress, but it's pretty usable already.

### Installation

```bash
git clone https://github.com/xvm32/pyhstr.git
cd pyhstr
python3 -m pip install -e .
```

### Usage

You should make an alias:

```bash
alias py='python3 -ic "from pyhstr.init import hh"'
```

Then:

```
>>> hh
```

![screenshot](pyhstr.gif)

### FIXME 

- implement search by regex
- make it work for ipython
- gracefully handling the echoing