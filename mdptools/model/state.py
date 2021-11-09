from ..types import (
    Update,
    dataclass,
    field,
    StateDescription,
    Iterator,
    imdict,
)
from ..utils import flatten, highlight as _h, partition
from .commands import update, is_update


@dataclass(eq=True, frozen=True)
class State:
    s: frozenset[str] = field(compare=True)
    ctx: imdict[str, int] = field(compare=True)

    def rename(self, states: dict[str, str]) -> "State":
        def rename(ss: str) -> str:
            if ss in states:
                return states[ss]
            return ss

        return State(frozenset(rename(ss) for ss in self.s), self.ctx)

    def apply(self, upd: Update) -> "State":
        return State(self.s, imdict(upd(self.ctx)))

    def __repr__(self) -> str:
        ctx = [f"{k}={v}" for k, v in self.ctx.items()]
        return "{" + ",".join(list(self.s) + ctx) + "}"

    def __str__(self) -> str:
        values = [_h[_h.state, ss] for ss in self.s]
        values += [_h[_h.variable, f"{k}={v}"] for k, v in self.ctx.items()]
        return (
            next(iter(values))
            if len(values) == 1
            else "{" + ",".join(values) + "}"
        )

    def __getitem__(self, index):
        return (self.s, self.ctx)[index]

    def __iter__(self) -> Iterator[str]:
        return iter(self.s)

    def __contains__(self, key: str) -> bool:
        return key in self.s

    def __len__(self) -> int:
        return len(self.s)

    def __add__(self, other: "State") -> "State":
        context = imdict({**self.ctx, **other.ctx})
        return State(self.s.union(other.s), context)

    def __sub__(self, other: "State") -> "State":
        return State(self.s.difference(other.s), self.ctx)


def state(*s: StateDescription, context: dict[str, int] = None) -> State:
    if context is None:
        context = {}
    context = imdict(context)
    if s[0] is None:
        return State(frozenset(), context)
    return State(frozenset(flatten(s)), context)


def state_update(s: StateDescription) -> tuple[State, Update]:
    if (
        isinstance(s, tuple)
        and len(s) == 2
        and isinstance(s[0], State)
        and isinstance(s[1], Update)
    ):
        s, upd = s
    else:
        s, update_str = partition(is_update, list(flatten(s)))
        upd = update(*update_str)
    return (state(s), upd)


def state_apply(s: StateDescription) -> State:
    s, upd = state_update(s)
    return s.apply(upd)
