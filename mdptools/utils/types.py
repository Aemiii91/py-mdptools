from typing import Callable, Union


RenameFunction = Union[
    tuple[str, str],
    list[str],
    dict[str, str],
    Callable[[str], str]]


StrongTransitionMap = dict[str, dict[str, dict[str, float]]]


LooseTransitionMap = dict[str, Union[
    set[str],
    dict[str, Union[
        dict[str, float],
        float]],
    ]]

ErrorCode = tuple[int, str]
