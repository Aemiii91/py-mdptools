from ..types import dataclass, field, StateDescription, Iterator, imdict
from ..utils import flatten, highlight as _h


@dataclass(eq=True, frozen=True)
class State:
    s: frozenset[str] = field(compare=True)
    context: imdict[str, int] = field(compare=True)

    def rename(self, states: dict[str, str]) -> "State":
        def rename(ss: str) -> str:
            if ss in states:
                return states[ss]
            return ss

        return State(frozenset(rename(ss) for ss in self.s), self.context)

    def __repr__(self) -> str:
        return f"State({','.join(self.s)})"

    def __str__(self) -> str:
        values = [_h[_h.state, ss] for ss in self.s]
        values += [
            _h[_h.variable, f"{k}={v}"] for k, v in self.context.items()
        ]
        return (
            next(iter(values))
            if len(values) == 1
            else "{" + ",".join(values) + "}"
        )

    def __getitem__(self, index):
        return self.s[index]

    def __iter__(self) -> Iterator[str]:
        return iter(self.s)

    def __contains__(self, key: str) -> bool:
        return key in self.s

    def __len__(self) -> int:
        return len(self.s)

    def __add__(self, other: "State") -> "State":
        s = self.s.union(other.s)
        context = imdict({**self.context, **other.context})
        return State(s, context)

    def __sub__(self, other: "State") -> "State":
        s = self.s.difference(other.s)
        return State(s, self.context)


def state(*s: StateDescription, context: dict[str, int] = None) -> State:
    if context is None:
        context = {}
    context = imdict(context)
    if s[0] is None:
        return State(frozenset(), context)
    return State(frozenset(flatten(s)), context)
