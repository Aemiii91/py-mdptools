from mdptools.utils.utils import items_union
from ..types import (
    dataclass,
    field,
    Union,
    Callable,
    Iterable,
    imdict,
    defaultdict,
)
from ..utils import re, reduce, highlight as _h


@dataclass(eq=True, frozen=True)
class Op:
    left: str = field(compare=True)
    op: str = field(compare=True)
    right: str
    rw: frozenset[str]
    call: Callable[[dict[str, int]], tuple[bool, dict[str, int]]]

    def __repr__(self) -> str:
        return f"{self.left}{self.op}{self.right}"

    def __call__(self, ctx: dict[str, int]) -> tuple[bool, dict[str, int]]:
        return self.call(ctx)


@dataclass(eq=True, frozen=True)
class Command:
    expr: frozenset[Op] = field(compare=True)
    used: imdict[str, frozenset[str]]

    @property
    def text(self) -> str:
        return " & ".join(map(str, self.expr))

    def __call__(
        self, old_ctx: dict[str, int]
    ) -> Union[bool, imdict[str, int]]:
        new_ctx = old_ctx

        def apply(expr: Op) -> dict:
            nonlocal new_ctx
            out, ctx = expr(old_ctx)
            new_ctx = {**new_ctx, **ctx}
            return out

        return all(apply(expr) for expr in self.expr) and imdict(new_ctx)

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.text})"

    def __str__(self) -> str:
        return _h(_h.variable, self.text) if self.text else ""

    def __add__(self, other: "Command") -> "Command":
        expr = self.expr.union(other.expr)
        used = items_union((e.left, e.rw) for e in expr)
        return self.__class__(expr, used)

    def __bool__(self) -> bool:
        return bool(self.expr)


def command(text: Union[str, Iterable[str]]) -> Command:
    text = " & ".join(list(text))
    expr = __compile_update(text)
    used = items_union((e.left, e.rw) for e in expr)
    return Command(expr, used)


class Guard(Command):
    expr: frozenset[frozenset[Op]] = field(compare=True)

    @property
    def text(self) -> str:
        return " & ".join(" | ".join(map(str, disj)) for disj in self.expr)

    def __repr__(self) -> str:
        return f"Guard({self.text or 'True'})"

    def __call__(self, ctx: dict[str, int]) -> bool:
        if not self.expr:
            return True
        return all(any(pred(ctx) for pred in disj) for disj in self.expr)

    def __add__(self, other: "Guard") -> "Guard":
        expr = self.expr.union(other.expr)
        used = items_union((e.left, e.rw) for c in expr for e in c)
        return Guard(expr, used)


def guard(pred: Union[str, Iterable[str]]) -> Guard:
    if not isinstance(pred, str):
        pred = " & ".join(pred)
    expr = __compile_guard(pred)
    used = items_union((e.left, e.rw) for c in expr for e in c)
    return Guard(expr, used)


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
    "!=": lambda a, b: a != b,
    ">=": lambda a, b: a >= b,
    "<=": lambda a, b: a <= b,
    "=": lambda a, b: a == b,
    ">": lambda a, b: a > b,
    "<": lambda a, b: a < b,
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
    return Op(obj, op, value, frozenset("r"), _call)


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
        return Op(
            obj, op, value, frozenset("w"), lambda _: (True, {obj: int(value)})
        )
    return None


def is_guard(s: str) -> bool:
    return any(c in s for c in "=<>")


def is_update(s: str) -> bool:
    return ":=" in s
