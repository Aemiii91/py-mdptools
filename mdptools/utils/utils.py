import re

from .types import StrongTransitionMap, RenameFunction, Callable


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


def parse_sas_str(sas: any) -> tuple[str, str, str]:
    res = [None, None, None]

    if sas is None:
        return res

    if not isinstance(sas, str):
        sas = "->".join(sas)

    for idx, value in enumerate(re.split(r"\s*->\s*", f"{sas}")):
        if idx < len(res) and value != '':
            res[idx] = value

    return res


def walk_dict(obj, callback, path: list[str] = None, default_value: float = 1.0):
    if path is None:
        path = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            walk_dict(value, callback, path + [key])
    elif isinstance(obj, set):
        for key in obj:
            callback(path + [key], default_value)
    elif isinstance(obj, str):
        callback(path + [obj], default_value)
    else:
        callback(path, obj)


def rename_map(obj: dict, rename: RenameFunction) -> dict[str, str]:
    rename = ensure_rename_function(rename)
    return { s: rename(s) for s in obj }


def rename_transition_map(old_map: StrongTransitionMap, states_map: dict[str, str],
        actions_map: dict[str, str]) -> StrongTransitionMap:
    return { states_map[s]: { actions_map[a]: { states_map[s_prime]: p
                for s_prime, p in dist_a.items() }
            for a, dist_a in act_s.items() }
        for s, act_s in old_map.items() }


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
