# pylint: disable=unused-import
from typing import Callable, Union, Iterable, TYPE_CHECKING

Digraph = any
MarkovDecisionProcess = any

if TYPE_CHECKING:
    from graphviz.dot import Digraph
    from ..mdp import MarkovDecisionProcess


States = tuple[str]
State = Union[str, States]
Transition = tuple[States, str, dict[States, float]]

LooseTransitionMap = dict[
    str,
    Union[
        set[str],
        dict[str, Union[dict[str, float], float]],
    ],
]
DistributionMap = dict[State, float]
ActionMap = dict[str, DistributionMap]
TransitionMap = dict[State, ActionMap]

ErrorCode = tuple[int, str]
ColorMap = dict[str, list[str]]
RenameFunction = Union[
    tuple[str, str], list[str], dict[str, str], Callable[[str], str]
]
