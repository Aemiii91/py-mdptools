from ..types import dataclass, field, Union, Callable, Iterable
from ..utils import re, reduce, highlight as _h, operator


@dataclass(eq=True, frozen=True)
class Op:
    obj: str = field(compare=True)
    op: str = field(compare=True)
    value: str
    _type: str
    _call: Callable[[dict[str, int]], any]

    def __repr__(self) -> str:
        return f"{self.obj}{self.op}{self.value}"

    def __call__(self, ctx: dict[str, int]) -> any:
        return self._call(ctx)


@dataclass(eq=True, frozen=True)
class Command:
    operations: frozenset[Op] = field(compare=True)

    @property
    def text(self) -> str:
        return ", ".join(map(str, self.operations))

    def used(self) -> set[str]:
        return set(reduce(operator.add, (op._type for op in self.operations)))

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.text})"

    def __str__(self) -> str:
        return _h[_h.variable, self.text] if self.text else ""

    def __add__(self, other: "Command") -> "Command":
        content = self.operations.union(other.operations)
        return self.__class__(content)

    def __bool__(self) -> bool:
        return bool(self.operations)


class Guard(Command):
    @property
    def text(self) -> str:
        return " & ".join(
            " | ".join(map(str, disj)) for disj in self.operations
        )

    def __repr__(self) -> str:
        return f"Guard({self.text or 'True'})"

    def __call__(self, ctx: dict[str, int]) -> bool:
        if not self.operations:
            return True
        return all(any(pred(ctx) for pred in disj) for disj in self.operations)


def guard(pred: Union[str, Iterable[str]]) -> Guard:
    if not isinstance(pred, str):
        pred = " & ".join(pred)
    return Guard(__compile_guard(pred))


def __compile_guard(text: str) -> frozenset[frozenset[Op]]:
    if not text:
        return frozenset()
    text = re.sub(r"\s*[\(\)]\s*", " ", text)
    conj = (
        re.split(r"\s*\|\s*", disj) for disj in re.split(r"\s*\&\s*", text)
    )
    return frozenset(
        frozenset(__simple_pred(expr) for expr in disj) for disj in conj
    )


_operations = {
    "=": lambda a, b: a == b,
    "!=": lambda a, b: a != b,
    ">": lambda a, b: a > b,
    "<": lambda a, b: a < b,
    ">=": lambda a, b: a >= b,
    "<=": lambda a, b: a <= b,
}


def __simple_pred(text: str) -> Callable[[dict], bool]:
    match = re.match(
        r"([a-zA-Z_]\w*)\s*(" + "|".join(_operations.keys()) + r")\s*(\d+)",
        text,
    )
    if match is None:
        raise ValueError
    obj, op, value = match.groups()
    _call = lambda ctx: _operations[op](
        ctx[obj] if obj in ctx else 0, int(value)
    )
    return Op(obj, op, value, "r", _call)


class Update(Command):
    def __call__(self, ctx: dict[str, int]) -> dict[str, int]:
        if not self.operations:
            return ctx

        # def reducer(curr: tuple[any, dict], op: Op) -> dict:
        #     value, ctx = curr
        #     out, ctx_ = op(ctx)
        #     if out is None:
        #         return {**ctx, **ctx_}
        #     return out

        return reduce(
            lambda ctx, assign: {**ctx, **assign(ctx)},
            self.operations,
            ctx,
        )


def update(*text: str) -> Update:
    text = ", ".join(list(text))
    return Update(__compile_update(text))


def __compile_update(text: str) -> set[Callable[[dict], dict]]:
    if not text:
        return frozenset()
    nodes = re.split(r"\s*,\s*", text)
    return frozenset(filter(None, map(__simple_assignment, nodes)))


def __simple_assignment(text: str) -> Callable[[dict], bool]:
    match = re.match(r"([a-zA-Z_]\w*)\s*(:=)\s*(\d+)", text)
    if match is None:
        raise ValueError
    obj, op, value = match.groups()
    if op == ":=":
        return Op(obj, op, value, "w", lambda _: {obj: int(value)})
    return None


def is_guard(s: str) -> bool:
    return any(c in s for c in "=<>")


def is_update(s: str) -> bool:
    return ":=" in s
