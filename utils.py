import re
from typing import TYPE_CHECKING
from bcolors import bcolors, bcolors_disable


MDP = any

if TYPE_CHECKING:
    from mdp import MDP


bc = bcolors_disable


def use_colors(value: bool = True):
    global bc
    if value:
        bc = bcolors
    else:
        bc = bcolors_disable


class color_text:
    def __getitem__(self, indices) -> str:
        color, text = indices
        return color + text + bc.RESET    
    @property
    def state(self): return bc.LIGHTCYAN
    @property
    def action(self): return bc.LIGHTGREEN
    @property
    def function(self): return bc.LIGHTBLUE
    @property
    def variable(self): return bc.PINK
    @property
    def string(self): return bc.YELLOW
    @property
    def comment(self): return bc.LIGHTGREY
    @property
    def ok(self): return bc.LIGHTGREEN
    @property
    def fail(self): return bc.LIGHTRED
    @property
    def error(self): return bc.RED
    @property
    def numeral(self): return bc.ORANGE
    @property
    def typing(self): return bc.GREEN
    @property
    def note(self): return bc.PURPLE


_c = color_text()


def word_color(word: str, color_map: dict[str,list[str]] = {}):
    if isinstance(color_map, str):
        return color_map
    for new_color, words in color_map.items():
        if word in words:
            return new_color
    return _c.string


def format_strings(s: str, color_map: dict[str,list[str]] = {}) -> str:
    str_re = r"\"([^\"\n]*?)\"|'([^'\n]*?)'"
    return re.sub(str_re, lambda x: (
        word := f"{x[1] or ''}{x[2] or ''}",
        color := word_color(word, color_map),
        color + word + bc.RESET)[-1], s)


def format_floats(s: str) -> str:
    float_re = r"([^\w\\'])(?:(?:(?:(0*[1-9][0-9]*)|0+)(?:\.?0+|(\.?0*[1-9][0-9]*)))|(\.[0-9]+))([^\w\\'])"
    return re.sub(float_re, r"\1" + _c.numeral + r"\2\3\4" + bc.RESET + r"\5", s)


def round_floats(s: str) -> str:
    round_re = r"(\.[0-9]*?[1-9]+)0+[1-9](?![0-9])"
    return re.sub(round_re, r"\1", s)


def lit_str(obj, color_map: dict[str,list[str]] = {}) -> str:
    return format_strings(format_floats(round_floats(obj.__str__())), color_map)


def map_list(lst: list[str]) -> dict[str, int]:
    if isinstance(lst, str):
        lst = re.split(r"\s*,\s*", lst)
    return {value: index for index, value in enumerate(lst)}


def key_by_value(obj: dict, value) -> str:
    if not value in obj.values():
        return None
    return list(obj.keys())[list(obj.values()).index(value)]


def parse_sas_str(sas: any) -> tuple[str, str, str]:
    res = [None, None, None]
    
    if not isinstance(sas, str):
        sas = ",".join(sas)

    for idx, value in enumerate(re.split(r"\s*,\s*", f"{sas}")):
        if idx < len(res) and value != '':
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


def prompt_fail(prompt, code):
    return f"[{_c[_c.fail, 'Failed']}] {_c[_c.note, prompt]}\n         >> {code}"


def prompt_error(error, tip, code):
    return f"{_c[_c.error, error]}\n           {tip}\n           >> {code}"


def mdp_to_str(mdp: MDP):
    lines = []
    # Name and validity
    lines += [f"{_c[_c.variable, mdp.name]} -> {_c[_c.typing, 'MDP']} "
              f"[{_c[_c.ok, 'Valid'] if mdp.is_valid else _c[_c.fail, 'Invalid']}]:"]
    # States and start state
    lines += [f"  {_c[_c.variable, 'S']} := {lit_str(tuple(mdp.S), _c.state)},"
              f" {_c[_c.variable, 's_init']} := {_c[_c.state, mdp.s_init]}"
             + _c[_c.comment, f"// {len(mdp.S)}"]]
    # Actions
    lines += [f"  {_c[_c.variable, 'A']} := {lit_str(tuple(mdp.A), _c.action)} "
             + _c[_c.comment, f"// {len(mdp.A)}"]]
    # Enabled transitions
    lines += [(en_s := mdp[s], f"  {_c[_c.function, 'en']}({_c[_c.state, s]}) ->"
              f" {lit_str(en_s, mdp_color_map(mdp))} " + _c[_c.comment, f"// {len(en_s)}"])[-1]
              for s in mdp.S]
    # Errors
    lines += mdp.errors
    return "\n".join(lines)


def mdp_color_map(mdp: MDP):
    if _c.state == '':
        return {}
    return {
        _c.state: list(mdp.S.keys()),
        _c.action: list(mdp.A.keys())
    }


def dist_wrong_value(s, a, value):
    return prompt_error(
        "Set is not allowed as a distribution value.",
        "Please use a Dictionary instead.",
        f"{_c[_c.function, 'Dist']}({_c[_c.state, s]}, {_c[_c.action, a]}) -> {lit_str(value)}")