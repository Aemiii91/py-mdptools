from ..types import ColorMap
from .utils import re
from .highlight import highlight as _h


def format_str(obj, color_map: ColorMap = None, colors: bool = True) -> str:
    return __format_strings(
        __format_floats(
            __round_floats(obj.__repr__() if colors else f"{obj}"), colors
        ),
        color_map,
        colors,
    )


def format_tup(f, s, sep: str, wrap: bool = False) -> str:
    ss = f"{f}{sep}{s}" if s else f"{f}"
    return f"({ss})" if s and wrap else ss


def to_identifier(name: str) -> str:
    return re.sub(r"\W+|^(?=\d+)", "_", name)


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
