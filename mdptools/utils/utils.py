import re
import itertools
import logging
from os import get_terminal_size
from functools import reduce
import numpy as np
from collections import Counter

from ..types import (
    RenameFunction,
    Callable,
    Iterable,
    Union,
    Hashable,
    MarkovDecisionProcess as MDP,
    State,
    imdict,
    defaultdict,
    Generator,
)


logger = logging.getLogger()
_log_handler = logging.StreamHandler()
logger.addHandler(_log_handler)


def set_logging_level(level):
    """Set the global logging level"""
    logger.setLevel(level)


def log_info_enabled() -> bool:
    """Whether info logging is enabled"""
    return logger.isEnabledFor(logging.INFO)


def set_log_silence(silent: bool):
    if silent:
        logger.removeHandler(_log_handler)
    else:
        logger.addHandler(_log_handler)


def get_terminal_width():
    try:
        width, _ = get_terminal_size()
    except OSError:
        width = 80
    return width


def float_is(n: float, target: float) -> bool:
    """Check if distance to target is smaller than can be represented"""
    return np.abs(n - target) < 10 * np.spacing(np.float64(1))


def items_union(
    items: Iterable[tuple[str, frozenset]]
) -> imdict[str, frozenset]:
    """Combines multiple items (str, set)"""
    ret = defaultdict(frozenset)
    for key, value in items:
        ret[key] = ret[key].union(value)
    return imdict(ret)


def flatten(s: Union[str, Iterable]) -> Generator[str, None, None]:
    """Flattens a collection of string[]"""
    if isinstance(s, str):
        yield s
        return
    for ls in s:
        yield from flatten(ls)


def partition(
    *predicates: Callable[[any], bool], it: Iterable, convert_to: type = list
) -> tuple[list, ...]:
    """Use a predicate to partition entries into false entries and true entries

    Usage: partition(is_odd, it=range(10)) -> 0 2 4 6 8   and  1 3 5 7 9
    """
    # Create a predicate for the all false case
    filter_false = lambda el: not any(pred(el) for pred in predicates)
    # Create a list of pairs of predicates and iterables
    iters = zip(
        (filter_false, *predicates), itertools.tee(it, len(predicates) + 1)
    )
    return tuple(convert_to(filter(pred, _it)) for pred, _it in iters)


def rename_map(names: Iterable, rename: RenameFunction) -> dict[str, str]:
    """Apply and map the value of a rename function on a collection of names"""
    rename = _ensure_rename_function(rename)
    return {name: rename(name) for name in names}


def _ensure_rename_function(rename: RenameFunction) -> Callable[[str], str]:
    # Supply a tuple[str, str] to do string replacement (regex can be used)
    if isinstance(rename, tuple):
        old, new = rename
        rename = lambda s: re.sub(old, new, s)
    # Supply a list of rename functions
    elif isinstance(rename, list):
        rename_list = [_ensure_rename_function(el) for el in rename]
        rename = lambda s: reduce(lambda sb, fn: fn(sb), rename_list, s)
    # Supply a rename map, mapping whole names to new ones
    elif isinstance(rename, dict):
        re_map = rename
        rename = lambda s: re_map[s] if s in re_map else s
    # If a function wasn't supplied, return noop
    elif rename is None or not isinstance(rename, Callable):
        return lambda s: s
    return rename


def ordered_state_str(
    s: State, m: MDP, sep: str = "_", formatter: Callable[[str], str] = None
) -> str:
    """Stringify a collection of local state names, ordered by process"""
    if m.is_process:
        return tuple_str(s, sep)
    if formatter is None:
        formatter = lambda s: s
    return sep.join(formatter(s(p)) for p in m.processes)


def tuple_str(tup: Union[tuple, str], sep: str = "_") -> str:
    """Join and flatten a tuple to a string"""
    if isinstance(tup, str):
        return tup
    return sep.join(tuple_str(s) for s in tup)


def id_register() -> Callable[[Hashable], int]:
    """Returns a function which returns a uid for an object"""
    uid = -1

    def next_id():
        nonlocal uid
        uid += 1
        return uid

    register = defaultdict(next_id)
    return lambda key=None: (uid, register) if key is None else register[key]


def minmax_register() -> Callable[[str, int], dict]:
    """Returns a function which, when called with a key and value,
    will keep track of the value's minimum and maximum
    """
    register = defaultdict(lambda: (float("inf"), float("-inf")))

    def register_value(key: str = None, value: int = None):
        if value is None or key is None:
            return register
        c_min, c_max = register[key]
        register[key] = (min(value, c_min), max(value, c_max))
        return value

    return register_value


def write_file(filename: str, content: str):
    """Safely write to a file"""
    from os import makedirs, path

    if not filename:
        return

    if path.dirname(filename):
        makedirs(path.dirname(filename), exist_ok=True)

    with open(filename, "w+", encoding="utf-8") as f:
        f.write(content)
