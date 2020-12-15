# pyhstr

![build status](https://github.com/xvm32/pyhstr/workflows/pyhstr/badge.svg) [![codecov](https://codecov.io/gh/xvm32/pyhstr/branch/master/graph/badge.svg?token=ZMY0VUX8WS)](https://codecov.io/gh/xvm32/pyhstr) [![PyPI version](https://badge.fury.io/py/pyhstr.svg)](https://badge.fury.io/py/pyhstr) ![Python Versions](https://img.shields.io/pypi/pyversions/pyhstr?logo=data:image/svg%2bxml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAxMDAgMTAwIj4KICA8ZGVmcz4KICAgIDxsaW5lYXJHcmFkaWVudCBpZD0icHlZZWxsb3ciIGdyYWRpZW50VHJhbnNmb3JtPSJyb3RhdGUoNDUpIj4KICAgICAgPHN0b3Agc3RvcC1jb2xvcj0iI2ZlNSIgb2Zmc2V0PSIwLjYiLz4KICAgICAgPHN0b3Agc3RvcC1jb2xvcj0iI2RhMSIgb2Zmc2V0PSIxIi8+CiAgICA8L2xpbmVhckdyYWRpZW50PgogICAgPGxpbmVhckdyYWRpZW50IGlkPSJweUJsdWUiIGdyYWRpZW50VHJhbnNmb3JtPSJyb3RhdGUoNDUpIj4KICAgICAgPHN0b3Agc3RvcC1jb2xvcj0iIzY5ZiIgb2Zmc2V0PSIwLjQiLz4KICAgICAgPHN0b3Agc3RvcC1jb2xvcj0iIzQ2OCIgb2Zmc2V0PSIxIi8+CiAgICA8L2xpbmVhckdyYWRpZW50PgogIDwvZGVmcz4KCiAgPHBhdGggZD0iTTI3LDE2YzAtNyw5LTEzLDI0LTEzYzE1LDAsMjMsNiwyMywxM2wwLDIyYzAsNy01LDEyLTExLDEybC0yNCwwYy04LDAtMTQsNi0xNCwxNWwwLDEwbC05LDBjLTgsMC0xMy05LTEzLTI0YzAtMTQsNS0yMywxMy0yM2wzNSwwbDAtM2wtMjQsMGwwLTlsMCwweiBNODgsNTB2MSIgZmlsbD0idXJsKCNweUJsdWUpIi8+CiAgPHBhdGggZD0iTTc0LDg3YzAsNy04LDEzLTIzLDEzYy0xNSwwLTI0LTYtMjQtMTNsMC0yMmMwLTcsNi0xMiwxMi0xMmwyNCwwYzgsMCwxNC03LDE0LTE1bDAtMTBsOSwwYzcsMCwxMyw5LDEzLDIzYzAsMTUtNiwyNC0xMywyNGwtMzUsMGwwLDNsMjMsMGwwLDlsMCwweiBNMTQwLDUwdjEiIGZpbGw9InVybCgjcHlZZWxsb3cpIi8+CgogIDxjaXJjbGUgcj0iNCIgY3g9IjY0IiBjeT0iODgiIGZpbGw9IiNGRkYiLz4KICA8Y2lyY2xlIHI9IjQiIGN4PSIzNyIgY3k9IjE1IiBmaWxsPSIjRkZGIi8+Cjwvc3ZnPgo=) ![GitHub](https://img.shields.io/github/license/xvm32/pyhstr)

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

You will need [poetry](https://github.com/python-poetry/poetry), preferably with these options in config:

```toml
virtualenvs.create = true
virtualenvs.in-project = true
```

Then clone the repo, cd into it, make a venv, activate it, and install the project:

```sh
git clone https://github.com/xvm32/pyhstr
cd pyhstr
poetry env use python3
. .venv/bin/activate
poetry install
```

To run tests, mypy checks, and style checks, you need to have Pythons:

- 3.7
- 3.8
- 3.9

For installing all the Python versions, I recommend [pyenv](https://github.com/pyenv/pyenv).

Once you have them, run:

```
tox
```

## Licensing

Licensed under the [MIT License](https://opensource.org/licenses/MIT). For details, see [LICENSE](https://github.com/xvm32/pyhstr/blob/master/LICENSE).