import re
from .types import ColorMap, MarkovDecisionProcess
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
        f"  {_h[_h.variable, 'S']} := {lit_str(tuple(mdp.S), _h.state)},"
        f" {_h[_h.variable, 's_init']} := {_h[_h.state, mdp.s_init]} "
        + _h[_h.comment, f"// {len(mdp.S)}"]
    ]
    # Actions
    lines += [
        f"  {_h[_h.variable, 'A']} := {lit_str(tuple(mdp.A), _h.action)} "
        + _h[_h.comment, f"// {len(mdp.A)}"]
    ]
    # Enabled transitions
    lines += [
        (
            en_s := mdp[s],
            f"  {_h[_h.function, 'en']}({_h[_h.state, s]}) ->"
            f" {lit_str(en_s, mdp_color_map(mdp))} "
            + _h[_h.comment, f"// {len(en_s)}"],
        )[-1]
        for s in mdp.S
    ]
    # Errors
    lines += [fail(msg, code) for (_, msg), code in mdp.errors]
    return "\n".join(lines)


def mdp_color_map(mdp: MarkovDecisionProcess) -> ColorMap:
    if _h.state == "":
        return {}
    return {_h.state: list(mdp.S.keys()), _h.action: list(mdp.A.keys())}


def lit_str(obj, color_map: ColorMap = None) -> str:
    return format_strings(
        format_floats(round_floats(obj.__str__())), color_map
    )


def format_strings(s: str, color_map: ColorMap = None) -> str:
    str_re = r"\"([^\"\n]*?)\"|'([^'\n]*?)'"
    # pylint: disable=undefined-variable
    return re.sub(
        str_re,
        lambda x: (
            word := f"{x[1] or ''}{x[2] or ''}",
            color := word_color(word, color_map),
            color + word + _h.reset,
        )[-1],
        s,
    )


def format_floats(s: str) -> str:
    float_re = (
        r"([^\w\\'])"
        r"(?:(?:(?:(0*[1-9][0-9]*)|0+)(?:\.?0+|(\.?0*[1-9][0-9]*)))|(\.[0-9]+))"
        r"([^\w\\'])"
    )
    return re.sub(
        float_re, r"\1" + _h.numeral + r"\2\3\4" + _h.reset + r"\5", s
    )


def round_floats(s: str) -> str:
    round_re = r"(\.[0-9]*?[1-9]+)0+[1-9](?![0-9])"
    return re.sub(round_re, r"\1", s)


def word_color(word: str, color_map: ColorMap = None) -> str:
    if isinstance(color_map, str):
        return color_map
    if color_map is not None:
        for new_color, words in color_map.items():
            if word in words:
                return new_color
    return _h.string
