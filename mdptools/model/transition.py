from ..types import (
    dataclass,
    field,
    Action,
    Distribution,
    StateDescription,
    DistributionDescription,
    MarkovDecisionProcess as MDP,
    imdict,
)
from ..utils import (
    itertools,
    operator,
    prod,
    partition,
    flatten,
    format_str,
    highlight as _h,
)
from .commands import guard, Guard, update, Update, is_guard, is_update
from .state import state, State


@dataclass(eq=True, frozen=True)
class Transition:
    action: Action
    pre: State = field(compare=True)
    guard: Guard = field(compare=True)
    post: Distribution = field(compare=True)
    active: set[MDP] = None

    def enabled(self, s: State) -> bool:
        return all(ss in s for ss in self.pre) and self.guard(s.context)

    def successors(self, s: State) -> dict[State, float]:
        if not self.enabled(s):
            raise ValueError
        return {
            (s - self.pre) + apply_update(s_): p for s_, p in self.post.items()
        }

    def rename(
        self, states: dict[str, str], actions: dict[str, str]
    ) -> "Transition":
        action = self.action
        if action in actions:
            action = actions[action]
        pre = self.pre.rename(states)
        guard = self.guard
        post = rename_post(self.post, states)
        return Transition(action, pre, guard, post, self.active)

    def bind(self, process: MDP) -> "Transition":
        return Transition(*self, active={process})

    def __repr__(self) -> str:
        return f"Transition({self.action}, {self.pre.__repr__()})"

    def __str__(self):
        pre = format_tup(self.pre, self.guard._repr, sep=" & ")
        return f"[{_h[_h.action, self.action]}] {pre} -> " + " + ".join(
            f"{format_str(p)}:{format_tup(*s_, sep=', ', wrap=True)}"
            if p != 1.0
            else f"{format_tup(*s_, sep=', ')}"
            for s_, p in self.post.items()
        )

    def __getitem__(self, index):
        return (self.action, self.pre, self.guard, self.post)[index]

    def __add__(self, other: "Transition") -> "Transition":
        action = self.action
        pre = self.pre + other.pre
        guard = self.guard + other.guard
        post = dist_product(self.post, other.post)
        active = self.active.union(other.active)
        return Transition(action, pre, guard, post, active)


def transition(
    action: str,
    pre: StateDescription,
    post: DistributionDescription,
    active: set[MDP] = None,
):
    pre, guards = partition(is_guard, list(flatten(pre)))
    pre = state(pre)
    if post is None:
        post = state(pre)
    post = structure_post(post)
    return Transition(action, pre, guard(guards), post, active)


def structure_post(post) -> Distribution:
    if isinstance(post, (str, set, tuple, State)):
        return {post_state(post): 1.0}
    return {post_state(s_): p for s_, p in post.items()}


def post_state(s_) -> tuple[State, Update]:
    if (
        isinstance(s_, tuple)
        and len(s_) == 2
        and isinstance(s_[0], State)
        and isinstance(s_[1], Update)
    ):
        s_, upd = s_
    else:
        s_, update_str = partition(is_update, list(flatten(s_)))
        upd = update(*update_str)
    return (state(s_), upd)


def rename_post(post: Distribution, states: dict[str, str]) -> Distribution:
    return {(s_[0].rename(states), s_[1]): p for s_, p in post.items()}


def apply_update(
    s_: tuple[State, Update], context: dict[str, int] = None
) -> State:
    if context is None:
        context = {}
    s_, upd = s_
    return state(s_, context=upd(context))


def format_tup(f, s, sep: str, wrap: bool = False) -> str:
    ss = f"{f}{sep}{s}" if s else f"{f}"
    return f"({ss})" if s and wrap else ss


def dist_product(dist1: Distribution, dist2: Distribution) -> Distribution:
    """Calculates the product of two distributions"""
    # Split the list of distributions into two generators
    s_primes = itertools.product(dist1.keys(), dist2.keys())
    p_values = itertools.product(dist1.values(), dist2.values())
    # Calculate the product of all permutations of the distributions
    return imdict(
        zip(
            (tuple(map(operator.add, *s_)) for s_ in s_primes),
            (prod(p) for p in p_values),
        )
    )
