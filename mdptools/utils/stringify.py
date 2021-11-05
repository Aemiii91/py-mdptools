import re
from ..types import ColorMap, MarkovDecisionProcess
from .highlight import highlight as _h
from .prompt import fail


def stringify(mdp: MarkovDecisionProcess) -> str:
    lines = []
    # Name and validity
    lines += [
        f"{_h[_h.variable, mdp.name]} -> {_h[_h.types, 'MDP']} "
        f"[{_h[_h.ok, 'Valid'] if mdp.is_valid else _h[_h.fail, 'Invalid']}]:"
    ]
    # States and start state
    lines += [
        f"  {_h[_h.variable, 'S']} := {literal_string(tuple(mdp.S), _h.state)},"
        f" {_h[_h.variable, 'init']} := {literal_string(mdp.init, _h.state)} "
        + _h[_h.comment, f"// {len(mdp.S)}"]
    ]
    # Actions
    lines += [
        f"  {_h[_h.variable, 'A']} := {literal_string(tuple(mdp.A), _h.action)} "
        + _h[_h.comment, f"// {len(mdp.A)}"]
    ]
    # Enabled transitions
    lines += [
        (
            en_s := mdp.actions(s),
            f"  {_h[_h.function, 'en']}({literal_string(s, _h.state)}) ->"
            f" {literal_string(en_s, __mdp_color_map(mdp))} "
            + _h[_h.comment, f"// {len(en_s)}"],
        )[-1]
        for s in mdp.S
    ]
    # Errors
    lines += [fail(msg, code) for (_, msg), code in mdp.errors]
    return "\n".join(lines)


def literal_string(
    obj, color_map: ColorMap = None, colors: bool = True
) -> str:
    return __format_strings(
        __format_floats(__round_floats(obj.__repr__()), colors),
        color_map,
        colors,
    )


def to_identifier(name: str) -> str:
    return re.sub(r"\W+|^(?=\d+)", "_", name)


def __mdp_color_map(mdp: MarkovDecisionProcess) -> ColorMap:
    if _h.state == "":
        return {}
    return {_h.state: list(mdp.S.keys()), _h.action: list(mdp.A.keys())}


def __format_strings(
    s: str, color_map: ColorMap = None, colors: bool = True
) -> str:
    str_re = r"\"([^\"\n]*?)\"|'([^'\n]*?)'"
    # pylint: disable=undefined-variable
    if colors:
        return re.sub(
            str_re,
            lambda x: (
                word := f"{x[1] or ''}{x[2] or ''}",
                color := __word_color(word, color_map),
                color + word + _h.reset,
            )[-1],
            s,
        )
    return re.sub(str_re, r"\1\2", s)


def __format_floats(s: str, colors: bool = True) -> str:
    float_re = (
        r"(^|[^\w\\'])"
        r"(?:(?:(?:(0*[1-9][0-9]*)|0+)(?:\.?0+|(\.?0*[1-9][0-9]*)))|(\.[0-9]+))"
        r"([^\w\\']|$)"
    )
    if colors:
        return re.sub(
            float_re, r"\1" + _h.numeral + r"\2\3\4" + _h.reset + r"\5", s
        )
    return re.sub(float_re, r"\1\2\3\4\5", s)


def __round_floats(s: str) -> str:
    round_re = r"(\.[0-9]*?[1-9]+)0+[1-9](?![0-9])"
    return re.sub(round_re, r"\1", s)


def __word_color(word: str, color_map: ColorMap = None) -> str:
    if isinstance(color_map, str):
        return color_map
    if color_map is not None:
        for new_color, words in color_map.items():
            if word in words:
                return new_color
    return _h.string
