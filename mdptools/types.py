# pylint: disable=unused-import
from dataclasses import dataclass, field
import re
from typing import (
    Callable,
    Generator,
    Iterator,
    NamedTuple,
    Optional,
    TypedDict,
    Union,
    Iterable,
    TYPE_CHECKING,
)

Digraph = any
MarkovDecisionProcess = any
MarkovDecisionProcess2 = any
State = any
Transition = any
Guard = any
Update = any

if TYPE_CHECKING:
    from graphviz.dot import Digraph
    from .mdp import MarkovDecisionProcess
    from .mdp2 import MarkovDecisionProcess2
    from .state import State
    from .transition import Transition
    from .commands import Guard, Update


StateDescription = Union[str, tuple, set, "State"]

Action = str
StateOrAction = Union[State, Action]

LooseTransitionMap = dict[
    State,
    Union[
        set[Action],
        dict[Action, Union[dict[State, float], float]],
    ],
]
Distribution = dict[tuple[State, Update], float]
ActionMap = dict[Action, Distribution]
TransitionMap = dict[tuple[State, Guard], ActionMap]


DistributionDescription = dict[StateDescription, float]
TransitionDescription = tuple[
    str, StateDescription, Union[StateDescription, DistributionDescription]
]


class ProcessDescription(TypedDict, total=False):
    name: Optional[str]
    init: Optional[StateDescription]
    transitions: list[TransitionDescription]


ErrorCode = tuple[int, str]
ColorMap = dict[str, list[str]]
RenameFunction = Union[
    tuple[str, str], list[str], dict[str, str], Callable[[str], str]
]


class imdict(dict):
    def __hash__(self):
        return hash(frozenset(self.items()))

    def _immutable(self, *args, **kws):
        raise TypeError("object is immutable")

    __setitem__ = _immutable
    __delitem__ = _immutable
    clear = _immutable
    update = _immutable
    setdefault = _immutable
    pop = _immutable
    popitem = _immutable
