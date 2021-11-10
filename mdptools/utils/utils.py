import re
import itertools
import operator
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
    imdict,
    defaultdict,
)


def float_is(n: float, target: float) -> bool:
    return n - target < 10 * np.spacing(np.float64(1))


def items_union(
    items: Iterable[tuple[str, frozenset]]
) -> imdict[str, frozenset]:
    ret = defaultdict(frozenset)
    for key, value in items:
        ret[key] = ret[key].union(value)
    return imdict(ret)


def flatten(s: Union[tuple, set, list]):
    from ..model import State

    if isinstance(s, str):
        yield s
        return
    for ls in s:
        if isinstance(ls, State):
            yield from flatten(ls.s)
        elif isinstance(ls, Iterable):
            yield from flatten(ls)
        else:
            raise TypeError


def partition(pred, iterable):
    """Use a predicate to partition entries into false entries and true entries

    Usage: partition(is_odd, range(10)) -> 0 2 4 6 8   and  1 3 5 7 9
    """
    t1, t2 = itertools.tee(iterable)
    return itertools.filterfalse(pred, t1), filter(pred, t2)


def rename_map(names: Iterable, rename: RenameFunction) -> dict[str, str]:
    rename = __ensure_rename_function(rename)
    return {name: rename(name) for name in names}


def __ensure_rename_function(rename: RenameFunction) -> Callable[[str], str]:
    if isinstance(rename, tuple):
        old, new = rename
        rename = lambda s: re.sub(old, new, s)
    elif isinstance(rename, list):
        rename_list = [__ensure_rename_function(el) for el in rename]
        rename = lambda s: reduce(lambda sb, fn: fn(sb), rename_list, s)
    elif isinstance(rename, dict):
        re_map = rename
        rename = lambda s: re_map[s] if s in re_map else s
    elif rename is None or not isinstance(rename, Callable):
        return lambda s: s
    return rename


def ordered_state_str(s: Iterable[str], m: MDP, sep: str = "_") -> str:
    if m.is_process:
        return tuple_str(s, sep)
    return sep.join(ss for p in m.processes for ss in s if ss in p.states)


def tuple_str(tup: Union[tuple, str], sep: str = "_") -> str:
    if isinstance(tup, str):
        return tup
    return sep.join(tuple_str(s) for s in tup)


def id_bank() -> Callable[[Hashable], int]:
    _id = 0
    _bank = {}

    def get_id(key: Hashable = None) -> int:
        nonlocal _id
        if key is None:
            return (_id - 1, _bank)
        if key not in _bank:
            _bank[key] = _id
            _id += 1
        return _bank[key]

    return get_id


def minmax_bank() -> Callable[[str, int], dict]:
    _bank = {}

    def register(key: str = None, value: int = None):
        if value is None:
            if key is None:
                return _bank
            return _bank[key]
        if key not in _bank:
            _bank[key] = (value, value)
        else:
            c = _bank[key]
            _bank[key] = (min(value, c[0]), max(value, c[1]))
        return value

    return register


def write_file(filename: str, content: str):
    """Safely writes to a file"""
    from os import makedirs, path

    if not filename:
        return

    if path.dirname(filename):
        makedirs(path.dirname(filename), exist_ok=True)

    with open(filename, "w+", encoding="utf-8") as f:
        f.write(content)
