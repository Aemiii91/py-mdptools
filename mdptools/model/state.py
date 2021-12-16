from ..types import (
    MarkovDecisionProcess as MDP,
    Command,
    dataclass,
    field,
    StateDescription,
    Iterator,
    imdict,
    Iterable,
)
from ..utils import flatten, partition, ordered_state_str
from .commands import command, is_update, is_guard


@dataclass(eq=True, frozen=True)
class State:
    s: frozenset[str] = field(compare=True)
    ctx: imdict[str, int] = field(compare=True)

    def rename(self, states: dict[str, str]) -> "State":
        """Rename the state"""

        def rename(ss: str) -> str:
            if ss in states:
                return states[ss]
            return ss

        return State(frozenset(rename(ss) for ss in self.s), self.ctx)

    def apply(self, update: Command, ctx: imdict[str, int] = None) -> "State":
        """Apply a command on the state"""
        if update:
            return State(self.s, imdict(update({**(ctx or {}), **self.ctx})))
        return self

    def intersection(self, other: Iterable[str]) -> "State":
        """Returns a new state with the intersection of this state and another set"""
        return State(self.s.intersection(other), self.ctx)

    def to_str(
        self,
        parent: MDP = None,
        sep: str = ",",
        colors: bool = False,
        wrap: bool = False,
        include_objects: bool = True,
    ) -> str:
        """Stringify the state, possibly ordering by the process order of a parent system"""
        return ordered_state_str(
            self, parent, sep, colors, wrap, include_objects
        )

    def __repr__(self) -> str:
        return self.to_str(None, wrap=True)

    def __str__(self) -> str:
        return self.to_str(None, colors=True, wrap=True)

    def __iter__(self) -> Iterator[str]:
        return iter(self.s)

    def __contains__(self, key: str) -> bool:
        return key in self.s

    def __len__(self) -> int:
        return len(self.s)

    def __eq__(self, other: "State") -> bool:
        if not isinstance(other, State):
            other = state(*other)
        return (self.s, self.ctx) == (other.s, other.ctx)

    def __add__(self, other: "State") -> "State":
        ctx = imdict({**self.ctx, **other.ctx})
        return State(self.s.union(other.s), ctx)

    def __sub__(self, other: "State") -> "State":
        return State(self.s.difference(other.s), self.ctx)

    def __le__(self, other: "State") -> bool:
        return self.s <= other.s

    def __call__(self, p: MDP) -> str:
        return next((ss for ss in self.s if ss in p), "")


def state(*s: StateDescription, ctx: dict[str, int] = None) -> State:
    """Create an instance of the State class"""
    if ctx is None:
        ctx = {}
    ctx = imdict(ctx)
    if s[0] is None:
        return State(frozenset(), ctx)
    return State(frozenset(flatten(s)), ctx)


def state_update(s: StateDescription) -> tuple[State, Command]:
    """Create a state and update pair"""
    if (
        isinstance(s, tuple)
        and len(s) == 2
        and isinstance(s[0], State)
        and isinstance(s[1], Command)
    ):
        s, upd = s
    else:
        s, update_str, _ = partition(is_update, is_guard, it=flatten(s))
        upd = command(update_str)
    return (state(s), upd)


def state_apply(s: StateDescription) -> State:
    """Create the initial state, applying any updates given"""
    s, upd = state_update(s)
    return s.apply(upd)
