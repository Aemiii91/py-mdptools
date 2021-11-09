from .utils import re
from .highlight import highlight as _h


def format_str(obj, color: str = "", use_colors: bool = True) -> str:
    return __format_strings(
        __format_floats(
            __round_floats(obj.__repr__() if use_colors else f"{obj}"),
            use_colors,
        ),
        color,
        use_colors,
    )


def format_tup(f, s, sep: str, wrap: bool = False) -> str:
    ss = f"{f}{sep}{s}" if s else f"{f}"
    return f"({ss})" if s and wrap else ss


def to_identifier(name: str) -> str:
    return re.sub(r"\W+|^(?=\d+)", "_", name)


_re_str = re.compile(r"\"([^\"\n]*?)\"|'([^'\n]*?)'")


def __format_strings(s: str, color: str, use_colors: bool) -> str:
    if use_colors:
        return re.sub(_re_str, color + r"\1\2" + _h.reset, s)
    return re.sub(_re_str, r"\1\2", s)


_re_float = re.compile(
    r"(^|[^\w\\'])"
    r"(?:(?:(?:(0*[1-9][0-9]*)|0+)(?:\.?0+|(\.?0*[1-9][0-9]*)))|(\.[0-9]+))"
    r"([^\w\\']|$)"
)


def __format_floats(s: str, colors: bool = True) -> str:
    if colors:
        return re.sub(
            _re_float, r"\1" + _h.numeral + r"\2\3\4" + _h.reset + r"\5", s
        )
    return re.sub(_re_float, r"\1\2\3\4\5", s)


def __round_floats(s: str) -> str:
    round_re = r"(\.[0-9]*?[1-9]+)0+[1-9](?![0-9])"
    return re.sub(round_re, r"\1", s)