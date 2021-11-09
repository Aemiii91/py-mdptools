# pylint: disable=unused-import
from dataclasses import dataclass, field
from collections import defaultdict
from typing import (
    Callable,
    Generator,
    Iterator,
    Optional,
    TypedDict,
    Union,
    Iterable,
    Hashable,
    TYPE_CHECKING,
)

Digraph = any
MarkovDecisionProcess = any
State = any
Transition = any
Guard = any
Update = any

if TYPE_CHECKING:
    from graphviz.dot import Digraph
    from .mdp import MarkovDecisionProcess
    from .model import State, Transition, Guard, Update


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


StateDescription = Union[str, tuple, set, "State"]

Action = str
StateOrAction = Union[State, Action]

Distribution = imdict[tuple[State, Update], float]
ActionMap = dict[Action, Distribution]
TransitionMap = dict[tuple[State, Guard], ActionMap]


DistributionDescription = dict[StateDescription, float]
TransitionDescription = tuple[
    str, StateDescription, Union[StateDescription, DistributionDescription]
]


ErrorCode = tuple[int, str]
ColorMap = dict[str, list[str]]
RenameMap = dict[tuple[str, ...], tuple[str, ...]]
RenameFunction = Union[
    tuple[str, str], list[str], dict[str, str], Callable[[str], str]
]

SetMethod = Callable[[MarkovDecisionProcess, State], list[Transition]]
