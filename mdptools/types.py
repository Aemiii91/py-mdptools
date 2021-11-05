# pylint: disable=unused-import
from dataclasses import dataclass, field
from typing import (
    Callable,
    Generator,
    Iterator,
    NamedTuple,
    Union,
    Iterable,
    TYPE_CHECKING,
)

Digraph = any
MarkovDecisionProcess = any

if TYPE_CHECKING:
    from graphviz.dot import Digraph
    from .mdp import MarkovDecisionProcess


@dataclass(eq=True, frozen=True)
class State:
    s: tuple[str, ...] = field(compare=True)

    def __new__(cls, *s: Union[str, "State"]):
        try:
            initializer = cls.__initializer
        except AttributeError:
            initializer = cls.__initializer = cls.__init__
            cls.__init__ = lambda *a, **k: None
        ret = object.__new__(cls)
        initializer(ret, tuple(flatten_state(s)))
        return ret

    def __repr__(self) -> str:
        return self.s[0] if len(self.s) == 1 else "(" + ",".join(self.s) + ")"

    def __getitem__(self, index):
        return self.s[index]

    def __iter__(self) -> Iterator[str]:
        return iter(self.s)

    def __contains__(self, key: str) -> bool:
        return key in self.s

    def __len__(self) -> int:
        return len(self.s)


def flatten_state(tup: tuple):
    for element in tup:
        if isinstance(element, str):
            yield element
        elif isinstance(element, State):
            yield from flatten_state(element.s)
        elif isinstance(element, tuple):
            yield from flatten_state(element)
        elif isinstance(element, Generator):
            yield from flatten_state(tuple(element))
        else:
            raise TypeError


Action = str
StateOrAction = Union[State, Action]

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


@dataclass(eq=True, frozen=True)
class Transition:
    pre: State
    action: Action
    post: DistributionMap

    def __str__(self):
        return f"[{self.action}] {self.pre} -> " + " + ".join(
            f"{p}:{s_}" if p != 1.0 else f"{s_}" for s_, p in self.post.items()
        )

    def __repr__(self) -> str:
        from .utils.highlight import highlight as _h
        from .utils.stringify import literal_string

        return (
            f"[{_h[_h.action, self.action]}] {_h[_h.state, self.pre]} -> "
            + " + ".join(
                f"{literal_string(p)}:{_h[_h.state, s_]}"
                if p != 1.0
                else f"{_h[_h.state, s_]}"
                for s_, p in self.post.items()
            )
        )

    def __getitem__(self, index):
        return (self.pre, self.action, self.post)[index]
