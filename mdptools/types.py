# pylint: disable=unused-import
from dataclasses import dataclass, field
from collections import defaultdict
from typing import (
    Callable,
    Generator,
    Iterator,
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
Command = any

if TYPE_CHECKING:
    from graphviz.dot import Digraph
    from .mdp import MarkovDecisionProcess
    from .model import State, Transition, Guard, Command


class imdict(dict):
    def __hash__(self):
        return hash(frozenset(self.items()))

    def _immutable(self, *a, **kw):
        raise TypeError("object is immutable")

    __setitem__ = _immutable
    __delitem__ = _immutable


StateDescription = Union[str, tuple, set, "State"]

Action = str

Distribution = imdict[tuple[State, Command], float]
ActionMap = dict[Action, Distribution]
# TransitionMap = dict[tuple[State, Guard], ActionMap]


DistributionDescription = dict[StateDescription, float]
TransitionDescription = tuple[
    str, StateDescription, Union[StateDescription, DistributionDescription]
]


ErrorCode = tuple[int, str]

RenameFn = Union[
    tuple[str, str],
    dict[str, str],
    Callable[[str], str],
]
RenameFunction = Union[
    RenameFn,
    list[RenameFn],
]

SetMethod = Callable[[MarkovDecisionProcess, State], list[Transition]]
