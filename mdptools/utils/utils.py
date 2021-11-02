from functools import reduce
import re
from itertools import chain

from .types import TransitionMap, RenameFunction, Callable, Iterable, Union


PARALLEL_SEPARATOR = "_"
INDEX_KEY_SEPARATOR = "->"


def map_list(lst: list[str]) -> dict[str, int]:
    if lst is None:
        return {}
    if isinstance(lst, str):
        lst = re.split(r"\s*,\s*", lst)
    return {value: index for index, value in enumerate(lst)}


def key_by_value(obj: dict, value) -> str:
    if not value in obj.values():
        return None
    return list(obj.keys())[list(obj.values()).index(value)]


def parse_indices(indices: Union[Iterable, str]) -> tuple[str, str, str]:
    res = [None, None, None]

    if indices is None:
        return res

    if isinstance(indices, str):
        indices = tuple(
            re.split(r"\s*" + INDEX_KEY_SEPARATOR + r"\s*", indices)
        )

    res = tuple(indices[i] if len(indices) > i else None for i in range(3))

    return res


def tree_walker(
    obj: Union[dict, set, str, any],
    callback: Callable[[list, any], None],
    path: list[str] = None,
    default_value: float = 1.0,
):
    if path is None:
        path = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            tree_walker(value, callback, path + [key])
    elif isinstance(obj, set):
        for key in obj:
            callback(path + [key], default_value)
    elif isinstance(obj, (str, tuple)):
        callback(path + [obj], default_value)
    else:
        callback(path, obj)


def rename_map(obj: dict, rename: RenameFunction) -> dict[str, str]:
    rename = ensure_rename_function(rename)
    return {s: rename(s) for s in obj}


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


def ensure_rename_function(rename: RenameFunction) -> Callable[[str], str]:
    if isinstance(rename, tuple):
        old, new = rename
        rename = lambda s: re.sub(old, new, s)
    elif isinstance(rename, list):
        rename_list = iter(rename)
        rename = lambda _: next(rename_list)
    elif isinstance(rename, dict):
        re_map = rename
        rename = lambda s: re_map[s] if s in re_map else s
    elif rename is None or not isinstance(rename, Callable):
        return lambda s: s
    return rename


def apply_filter(_list: Iterable, _filter: list[bool]):
    """Applies a boolean filter on a list"""
    return [element for idx, element in enumerate(_list) if _filter[idx]]
