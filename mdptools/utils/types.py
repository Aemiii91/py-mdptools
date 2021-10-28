# pylint: disable=unused-import
from typing import Callable, Union, TYPE_CHECKING

Digraph = any
MarkovDecisionProcess = any

if TYPE_CHECKING:
    from graphviz.dot import Digraph
    from ..mdp import MarkovDecisionProcess

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

ColorMap = dict[str,list[str]]
