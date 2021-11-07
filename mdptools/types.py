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

if TYPE_CHECKING:
    from graphviz.dot import Digraph
    from .mdp import MarkovDecisionProcess
    from .mdp2 import MarkovDecisionProcess2


StateDescription = Union[str, tuple, set, "State"]


@dataclass(eq=True, frozen=True)
class State:
    s: frozenset[str] = field(compare=True)

    def __new__(cls, *s: StateDescription):
        from .utils import flatten

        try:
            initializer = cls.__initializer
        except AttributeError:
            initializer = cls.__initializer = cls.__init__
            cls.__init__ = lambda *a, **k: None

        if s[0] is None:
            return None

        ret = object.__new__(cls)
        initializer(ret, frozenset(flatten(s)))
        return ret

    def __repr__(self) -> str:
        return (
            next(iter(self.s))
            if len(self.s) == 1
            else "{" + ",".join(self.s) + "}"
        )

    def __getitem__(self, index):
        return self.s[index]

    def __iter__(self) -> Iterator[str]:
        return iter(self.s)

    def __contains__(self, key: str) -> bool:
        return key in self.s

    def __len__(self) -> int:
        return len(self.s)


Action = str
StateOrAction = Union[State, Action]

LooseTransitionMap = dict[
    State,
    Union[
        set[Action],
        dict[Action, Union[dict[State, float], float]],
    ],
]
Distribution = dict[tuple[State, str], float]
ActionMap = dict[Action, Distribution]
TransitionMap = dict[State, ActionMap]


@dataclass(eq=True, frozen=True)
class Guard:
    _repr: str
    call: Callable[[dict], bool]

    def __new__(cls, pred: str):
        try:
            initializer = cls.__initializer
        except AttributeError:
            initializer = cls.__initializer = cls.__init__
            cls.__init__ = lambda *a, **k: None
        ret = object.__new__(cls)
        initializer(ret, pred, make_guard(pred))
        return ret

    def __repr__(self) -> str:
        return self._repr


def make_guard(pred: str) -> Callable[[dict], bool]:
    guards = re.findall(r"([a-zA-Z_]\w*)\s*(=|>|<|>=|<=)\s*(\d+)", pred)
    if guards:
        obj, op, value = guards[0]
        if op == "=":
            return lambda objects: objects[obj] == value
    return lambda _: True


@dataclass(eq=True, frozen=True)
class Transition:
    action: Action
    pre: State
    guard: Guard
    post: Distribution
    active: set[MarkovDecisionProcess2] = None

    def __repr__(self):
        pre = format_tup(self.pre, self.guard, sep=" & ")
        return f"[{self.action}] {pre} -> " + " + ".join(
            f"{p}:{format_tup(*s_, sep=', ', wrap=True)}"
            if p != 1.0
            else f"{format_tup(*s_, sep=', ')}"
            for s_, p in self.post.items()
        )

    def __getitem__(self, index):
        return (self.action, self.pre, self.guard, self.post)[index]


def format_tup(f, s, sep: str, wrap: bool = False) -> str:
    ss = f"{f}{sep}{s}" if s else f"{f}"
    return f"({ss})" if s and wrap else ss


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
