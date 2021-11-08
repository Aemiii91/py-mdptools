from ..types import dataclass, field, Union, Callable, Iterable
from ..utils import re, reduce, highlight as _h


@dataclass(eq=True, frozen=True)
class Guard:
    _repr: str = field(compare=True)
    conj: frozenset[Callable[[dict], bool]]

    def __repr__(self) -> str:
        return f"Guard({self._repr or 'True'})"

    def __str__(self) -> str:
        return _h[_h.variable, self._repr] if self._repr else ""

    def __call__(self, context: dict[str, int]) -> bool:
        return all(p(context) for p in self.conj)

    def __add__(self, other: "Guard") -> "Guard":
        _repr = " & ".join(filter(None, [self._repr, other._repr]))
        conj = self.conj.union(other.conj)
        return Guard(_repr, conj)

    def __bool__(self) -> bool:
        return bool(self._repr)


def guard(pred: Union[str, Iterable[str]]) -> Guard:
    if not isinstance(pred, str):
        pred = " & ".join(pred)
    return Guard(pred, compile_guard(pred))


operations = {
    "=": lambda a, b: a == b,
    "!=": lambda a, b: a != b,
    ">": lambda a, b: a > b,
    "<": lambda a, b: a < b,
    ">=": lambda a, b: a >= b,
    "<=": lambda a, b: a <= b,
}


def compile_guard(text: str) -> frozenset[Callable[[dict], bool]]:
    if not text:
        return frozenset([lambda _: True])
    nodes = (
        re.split(r"\s*\|\s*", disj) for disj in re.split(r"\s*\&\s*", text)
    )
    return frozenset(map(map_disjunction, nodes))


def map_disjunction(disj: list[str]) -> Callable[[dict], bool]:
    disj = frozenset(map(simple_pred, disj))
    return lambda context: any(p(context) for p in disj)


def simple_pred(text: str) -> Callable[[dict], bool]:
    match = re.match(
        r"([a-zA-Z_]\w*)\s*(" + "|".join(operations.keys()) + r")\s*(\d+)",
        text,
    )
    if match is None:
        raise ValueError
    obj, op, value = match.groups()
    value = int(value)
    return lambda context: operations[op](
        context[obj] if obj in context else 0, value
    )


@dataclass(eq=True, frozen=True)
class Update:
    _repr: str = field(compare=True)
    assignments: frozenset[Callable[[dict], dict]]

    def __repr__(self) -> str:
        return f"Update({self._repr})"

    def __str__(self) -> str:
        return _h[_h.variable, self._repr]

    def __call__(self, context: dict[str, int]) -> dict[str, int]:
        if not self.assignments:
            return context
        return reduce(
            lambda ctx, assign: {**ctx, **assign(ctx)},
            self.assignments,
            context,
        )

    def __add__(self, other: "Update") -> "Update":
        _repr = ", ".join(filter(None, [self._repr, other._repr]))
        assignments = self.assignments.union(other.assignments)
        return Update(_repr, assignments)

    def __bool__(self) -> bool:
        return bool(self._repr)


def update(*text: str) -> Update:
    text = ", ".join(list(text))
    return Update(text, compile_update(text))


def compile_update(text: str) -> set[Callable[[dict], dict]]:
    if not text:
        return frozenset()
    nodes = re.split(r"\s*,\s*", text)
    return frozenset(map(simple_assignment, nodes))


def simple_assignment(text: str) -> Callable[[dict], bool]:
    match = re.match(r"([a-zA-Z_]\w*)\s*(:=)\s*(\d+)", text)
    if match is None:
        raise ValueError
    obj, op, value = match.groups()
    value = int(value)
    if op == ":=":
        return lambda _: {obj: value}
    return lambda _: None


def is_guard(s: str) -> bool:
    return any(c in s for c in "=<>")


def is_update(s: str) -> bool:
    return ":=" in s
