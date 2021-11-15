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
from ..utils import flatten, highlight as _h, partition, itertools
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

    def apply(self, update: Command) -> "State":
        """Apply a command on the state"""
        return State(self.s, imdict(update(self.ctx)))

    def intersection(self, other: Iterable[str]) -> "State":
        """Returns a new state with the intersection of this state and another set"""
        return State(self.s.intersection(other), self.ctx)

    def __repr__(self) -> str:
        ctx = [f"{k}={v}" for k, v in self.ctx.items()]
        return "{" + ",".join(list(self.s) + ctx) + "}"

    def __str__(self) -> str:
        values = [_h.state(ss) for ss in self.s]
        values += [_h.variable(f"{k}={v}") for k, v in self.ctx.items()]
        return (
            next(iter(values))
            if len(values) == 1
            else "{" + ",".join(values) + "}"
        )

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

    def __call__(self, p: MDP) -> str:
        return next((ss for ss in self.s if ss in p), "")


def state(*s: StateDescription, ctx: dict[str, int] = None) -> State:
    if ctx is None:
        ctx = {}
    ctx = imdict(ctx)
    if s[0] is None:
        return State(frozenset(), ctx)
    return State(frozenset(flatten(s)), ctx)


def state_update(s: StateDescription) -> tuple[State, Command]:
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
