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