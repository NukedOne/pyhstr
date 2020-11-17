import collections
import pathlib
import random
import string
import timeit

from pyhstr.utilities import get_bpython_history_path, remove_duplicates, sort


CHARS = string.ascii_letters + string.digits + r"!@#$%^&*()_+,./;'\\[]<>?:\"|{}"


def old_remove_duplicates(thing):
    without_duplicates = []
    for thingy in thing:
        if thingy not in without_duplicates:
            without_duplicates.append(thingy)
    return without_duplicates


def old_sort(thing):
    return [
        x[0] for x in sorted(
            collections.Counter(thing).items(), key=lambda y: -y[1]
        )
    ]


def generate_random_history():
    return [
        "".join(
            [
                random.choice(CHARS)
                for _ in range(random.randint(40, 80))
            ]
        )
        for _ in range(100)
    ]


def test_new_sort_does_not_break_sorting():
    history = generate_random_history()
    assert old_sort(history) == sort(history)


def test_new_remove_duplicates_does_not_break_removing_duplicates():
    history = generate_random_history()
    assert old_remove_duplicates(history) == remove_duplicates(history)


def test_new_remove_duplicates_is_faster_than_old():
    time_old = timeit.timeit(
        "old_remove_duplicates(generate_random_history())",
        setup="from tests.test_utilities import old_remove_duplicates, generate_random_history",
        number=1000
    )
    time_new = timeit.timeit(
        "remove_duplicates(generate_random_history())",
        setup="from pyhstr.utilities import remove_duplicates;" +
              "from tests.test_utilities import generate_random_history",
        number=1000
    )
    assert time_new < time_old


def test_get_default_bpython_history_path():
    assert get_bpython_history_path() == pathlib.Path("~/.pythonhist").expanduser()
