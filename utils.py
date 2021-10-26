import re
from bcolors import bc, bcolors, bcolors_disable


def use_colors(value: bool):
    global bc
    if value:
        bc = bcolors
    else:
        bc = bcolors_disable


def color_text(color, text: str) -> str:
    return color + text + bc.RESET

_c = color_text


_str_re = r"\"([^\"\n]*?)\"|'([^'\n]*?)'"
_float_re = r"([^\w\\])(?:(?:(?:(0*[1-9][0-9]+)|(0+))(\.[0-9]*)?)|(\.[0-9]+))([^\w\\])"


def lit_str(obj) -> str:
    res = obj.__str__()
    res = re.sub(_str_re, bc.LIGHTGREEN + r"\1\2" + bc.RESET, res)
    res = re.sub(_float_re, r"\1" + bc.ORANGE + r"\2\4\5" + bc.RESET + r"\6", res)
    return res


def map_list(lst: list[str]) -> dict[str, int]:
    if isinstance(lst, str):
        lst = re.split(r"\s*,\s*", lst)
    return {value: index for index, value in enumerate(lst)}


def parse_sas_str(sas: any) -> tuple[str, str, str]:
    res = [None, None, None]
    if not isinstance(sas, str):
        sas = ",".join(sas)
    for idx, value in enumerate(re.split(r"\s*,\s*", sas)):
        if idx < len(res):
            res[idx] = value
    return res


def walk_dict(obj, callback, path: list[str] = []):
    if isinstance(obj, dict):
        for key, value in obj.items():
            walk_dict(value, callback, path + [key])
    elif isinstance(obj, set):
        for key in obj:
            callback(path + [key], 1.0)
    elif isinstance(obj, str):
        callback(path + [obj], 1.0)
    else:
        callback(path, obj)


def prompt_fail(buffer, prompt, code):
    buffer.append(f"{_c(bc.LIGHTRED, 'Failed')}: {_c(bc.PURPLE, prompt)}\n        >> {code}")

def prompt_error(error, tip, code):
    return f"{bc.RED}{error}{bc.RESET}\n           {tip}\n           >> {code}"