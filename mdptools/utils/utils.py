import itertools
import re
from functools import reduce
from itertools import filterfalse, tee

from ..types import (
    State,
    StateOrAction,
    TransitionMap,
    RenameFunction,
    Callable,
    Iterable,
    Union,
)


INDEX_KEY_SEPARATOR = "->"


def map_list(
    lst: Union[list[StateOrAction], str], convert: Callable[[str], any] = None
) -> dict[StateOrAction, int]:
    if lst is None:
        return {}
    if isinstance(lst, str):
        lst = re.split(r"\s*,\s*", lst)
    if convert is not None:
        lst = map(convert, lst)
    return {value: index for index, value in enumerate(lst)}


def flatten(s: Union[tuple, set, list]):
    from ..state import State

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
    t1, t2 = tee(iterable)
    return filterfalse(pred, t1), filter(pred, t2)


def partition_multi(
    predicates: list, iterable: Iterable
) -> tuple[filter, ...]:
    it, *iters = tee(iterable, len(predicates) + 1)
    g = [filterfalse(lambda el: any(pred(el) for pred in predicates), it)]
    for idx, pred in enumerate(predicates):
        g += [filter(pred, iters[idx])]
    return tuple(g)


def is_guard(s: str) -> bool:
    return any(c in s for c in "=<>")


def is_update(s: str) -> bool:
    return ":=" in s


def key_by_value(obj: dict, value) -> str:
    if not value in obj.values():
        return None
    return list(obj.keys())[list(obj.values()).index(value)]


def parse_indices(
    indices: Union[Iterable, str]
) -> tuple["State", str, "State"]:
    from ..state import State, state

    res = [None, None, None]

    if indices is None:
        return res

    if isinstance(indices, str):
        indices = tuple(
            re.split(r"\s*" + INDEX_KEY_SEPARATOR + r"\s*", indices)
        )

    if isinstance(indices, State):
        return [indices, None, None]

    if len(indices) > 0:
        res[0] = state(indices[0])
    if len(indices) > 1:
        res[1] = indices[1]
    if len(indices) > 2:
        res[2] = state(indices[2])

    return res


def tree_walker(
    obj: Union[dict, set, str, float],
    callback: Callable[[list[StateOrAction], float], None],
    path: list[StateOrAction] = None,
    default_value: float = 1.0,
):
    from ..state import State

    if path is None:
        path = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            tree_walker(value, callback, path + [key])
    elif isinstance(obj, set):
        for key in obj:
            callback(path + [key], default_value)
    elif isinstance(obj, (str, State)):
        callback(path + [obj], default_value)
    else:
        callback(path, obj)


def rename_map(
    obj: dict, rename: RenameFunction
) -> dict[StateOrAction, StateOrAction]:
    from ..state import state

    rename = __ensure_rename_function(rename)
    return {
        s: state(rename(sb) for sb in s) if isinstance(s, State) else rename(s)
        for s in obj
    }


def rename_transition_map(
    old_map: TransitionMap,
    states_map: dict[str, str],
    actions_map: dict[str, str],
) -> TransitionMap:
    return {
        states_map[s]: {
            actions_map[a]: {
                states_map[s_prime]: p for s_prime, p in dist_a.items()
            }
            for a, dist_a in act_s.items()
        }
        for s, act_s in old_map.items()
    }


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


def apply_filter(_list: Iterable, _filter: list[bool]):
    """Applies a boolean filter on a list"""
    return [element for idx, element in enumerate(_list) if _filter[idx]]


def write_file(filename: str, content: str):
    """Safely writes to a file"""
    from os import makedirs, path

    if filename is None or filename == "":
        return

    if path.dirname(filename) != "":
        makedirs(path.dirname(filename), exist_ok=True)

    with open(filename, "w+", encoding="utf-8") as f:
        f.write(content)
