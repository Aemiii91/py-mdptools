# pylint: disable=unused-import
from typing import Callable, Union, Iterable, TYPE_CHECKING

Digraph = any
MarkovDecisionProcess = any

if TYPE_CHECKING:
    from graphviz.dot import Digraph
    from ..mdp import MarkovDecisionProcess


States = tuple[str]
State = Union[str, States]
Action = str
StateOrAction = Union[State, Action]
Transition = tuple[States, Action, dict[States, float]]

LooseTransitionMap = dict[
    State,
    Union[
        set[Action],
        dict[Action, Union[dict[State, float], float]],
    ],
]
DistributionMap = dict[State, float]
ActionMap = dict[Action, DistributionMap]
TransitionMap = dict[State, ActionMap]

ErrorCode = tuple[int, str]
ColorMap = dict[str, list[str]]
RenameFunction = Union[
    tuple[str, str], list[str], dict[str, str], Callable[[str], str]
]
