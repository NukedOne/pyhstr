# pyhstr

Inspired by hstr, **pyhstr** is a history suggest box that lets you quickly search, navigate, and manage your Python shell history. At this point, it supports the standard Python shell, IPython, and bpython. The plan is to support ptpython as well, but some help is needed for that to happen (see [issue #7](https://github.com/xvm32/pyhstr/issues/7)).

## Installation


```
pip install pyhstr
```

## Usage

The **standard** shell and **bpython**:

  ```python
  >>> from pyhstr import hh
  >>> hh
  ```

**IPython**:

  ```ipython
  In [1]: import pyhstr
  In [2]: %hh
  ```

Making an alias should be more convenient though, for example:

```bash
alias py='python3 -ic "from pyhstr import hh"'
```

## Screencast

![screenshot](pyhstr.gif)

## Development

```
git clone https://github.com/xvm32/pyhstr
cd pyhstr
python3 -m venv env
source env/bin/activate
pip install poetry
poetry install
```

To run tests, mypy checks, and style checks, you need to have Pythons:

- 3.6
- 3.7
- 3.8
- 3.9

For installing all the Python versions, I recommend [pyenv](https://github.com/pyenv/pyenv).

Once you have them, run:

```
tox
```