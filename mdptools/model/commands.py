import operator
from ..types import (
    dataclass,
    field,
    Union,
    Callable,
    Iterable,
    imdict,
    defaultdict,
)
from ..utils import re, highlight as _h, itertools


@dataclass(eq=True, frozen=True)
class Op:
    left: str = field(compare=True)
    op: str = field(compare=True)
    right: str
    rw: frozenset[str]
    call: Callable[[dict[str, int]], tuple[bool, dict[str, int]]]

    def can_be_dependent(self, other: "Op") -> bool:
        if self.left != other.left:
            return False
        # Check if one operation has a write while the other is nonempty
        return ("w" in self.rw and other.rw) or ("w" in other.rw and self.rw)

    def __repr__(self) -> str:
        return f"{self.left}{self.op}{self.right}"

    def __call__(self, ctx: dict[str, int]) -> tuple[bool, dict[str, int]]:
        return self.call(ctx)


@dataclass(eq=True, frozen=True)
class Command:
    expr: frozenset[Op] = field(compare=True)

    def used(self) -> frozenset[Op]:
        return self.expr

    @property
    def text(self) -> str:
        return ", ".join(map(str, self.expr))

    def __call__(self, ctx: dict[str, int]) -> Union[bool, imdict[str, int]]:
        old_ctx = defaultdict(lambda: 0, ctx)
        new_ctx = {}

        def apply(expr: Op) -> dict:
            nonlocal new_ctx
            out, ctx = expr(old_ctx)
            new_ctx = {**new_ctx, **ctx}
            return out

        ret = all(apply(expr) for expr in self.expr) and imdict(
            {**old_ctx, **new_ctx}
        )
        return ret

    def __eq__(self, other: "Command") -> bool:
        return set(map(str, self.expr)) == set(map(str, other.expr))

    def __hash__(self) -> int:
        return hash(frozenset(map(str, self.expr)))

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.text})"

    def __str__(self) -> str:
        return _h.variable(self.text) if self.text else ""

    def __add__(self, other: "Command") -> "Command":
        return self.__class__(self.expr.union(other.expr))

    def __bool__(self) -> bool:
        return bool(self.expr)


def command(text: Union[str, Iterable[str]]) -> Command:
    text = " & ".join(list(text))
    return Command(_compile_update(text))


class Guard(Command):
    expr: frozenset[frozenset[Op]] = field(compare=True)

    def used(self) -> frozenset[Op]:
        return frozenset(itertools.chain.from_iterable(self.expr))

    @property
    def text(self) -> str:
        return " & ".join(" | ".join(map(str, disj)) for disj in self.expr)

    def __repr__(self) -> str:
        return f"Guard({self.text or 'True'})"

    def __call__(self, ctx: dict[str, int]) -> bool:
        ctx = defaultdict(lambda: 0, ctx)
        if not self.expr:
            return True
        return all(any(pred(ctx) for pred in disj) for disj in self.expr)

    def __add__(self, other: "Guard") -> "Guard":
        return Guard(self.expr.union(other.expr))


def guard(pred: Union[str, Iterable[str]]) -> Guard:
    if not isinstance(pred, str):
        pred = " & ".join(pred)
    return Guard(_compile_guard(pred))


def _compile_guard(text: str) -> frozenset[frozenset[Op]]:
    if not text:
        return frozenset()
    text = re.sub(r"\s*[\(\)]\s*", " ", text)
    conj = (
        re.split(r"\s*\|\s*", disj) for disj in re.split(r"\s*\&\s*", text)
    )
    return frozenset(
        frozenset(_simple_pred(expr) for expr in disj) for disj in conj
    )


_comparisons = {
    "!=": lambda a, b: a != b,
    ">=": lambda a, b: a >= b,
    "<=": lambda a, b: a <= b,
    "=": lambda a, b: a == b,
    ">": lambda a, b: a > b,
    "<": lambda a, b: a < b,
}


_re_comparison = re.compile(
    r"([a-zA-Z_]\w*)\s*(" + "|".join(_comparisons.keys()) + r")\s*(\d+)",
    re.IGNORECASE,
)


def _simple_pred(text: str) -> Callable[[dict], bool]:
    match = re.match(_re_comparison, text)
    if match is None:
        raise ValueError
    obj, op, value = match.groups()
    _call = lambda ctx: _comparisons[op](ctx[obj], int(value))
    return Op(obj, op, value, frozenset("r"), _call)


def _compile_update(text: str) -> set[Callable[[dict], dict]]:
    if not text:
        return frozenset()
    nodes = re.split(r"\s*,\s*", text)
    return frozenset(filter(None, map(_simple_assignment, nodes)))


_operations = {
    "+": operator.add,
    "-": operator.sub,
}

_re_assign = re.compile(
    r"\s*([a-z_]\w*)\s*(:=)\s*(?:([a-z_]\w*)\s*([+-])\s*)?(\d+)",
    re.IGNORECASE,
)


def _simple_assignment(text: str) -> Callable[[dict], bool]:
    match = re.match(_re_assign, text)
    if match is None:
        raise ValueError
    obj, op, obj_read, expr_op, value = match.groups()
    if op == ":=":
        if obj_read:
            return Op(
                obj,
                op,
                f"{obj_read}{expr_op}{value}",
                frozenset("rw"),
                lambda ctx: (
                    True,
                    {obj: _operations[expr_op](ctx[obj_read], int(value))},
                ),
            )
        return Op(
            obj, op, value, frozenset("w"), lambda _: (True, {obj: int(value)})
        )
    return None


def is_guard(s: str) -> bool:
    return re.match(_re_comparison, s) is not None


def is_update(s: str) -> bool:
    return re.match(_re_assign, s) is not None
