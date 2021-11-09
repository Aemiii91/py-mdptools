from ..types import (
    dataclass,
    field,
    Action,
    Distribution,
    StateDescription,
    DistributionDescription,
    MarkovDecisionProcess as MDP,
    imdict,
    defaultdict,
)
from ..utils import (
    itertools,
    operator,
    np,
    partition,
    flatten,
    Counter,
    reduce,
    format_str,
    format_tup,
    highlight as _h,
)
from .commands import guard, Guard, is_guard
from .state import state, State, state_update


@dataclass(eq=True, frozen=True)
class Transition:
    action: Action
    pre: State = field(compare=True)
    guard: Guard = field(compare=True)
    post: Distribution = field(compare=True)
    active: set[MDP] = None

    def is_enabled(self, s: State) -> bool:
        return all(ss in s for ss in self.pre) and self.guard(s.ctx)

    def in_conflict(self, other: "Transition") -> bool:
        return any(ss in other.pre for ss in self.pre)

    def is_parallel(self, other: "Transition") -> bool:
        return len(self.active.intersection(other.active)) == 0

    def can_be_dependent(self, other: "Transition") -> bool:
        return bool(self.used().intersection(other.used()))

    def successors(self, s: State) -> dict[State, float]:
        if not self.is_enabled(s):
            raise ValueError
        return {
            (s - self.pre) + s_.apply(upd): p
            for (s_, upd), p in self.post.items()
        }

    def used(self) -> set[str]:
        return set(
            itertools.chain.from_iterable(
                upd({}).keys() for _, upd in self.post.keys()
            )
        )

    def rename(
        self, states: dict[str, str], actions: dict[str, str]
    ) -> "Transition":
        action = self.action
        if action in actions:
            action = actions[action]
        pre = self.pre.rename(states)
        guard = self.guard
        post = {
            (s_[0].rename(states), s_[1]): p for s_, p in self.post.items()
        }
        return Transition(action, pre, guard, post, self.active)

    def bind(self, processes: set[MDP]) -> "Transition":
        return Transition(*self, active=processes)

    def __repr__(self) -> str:
        guard = f", {self.guard.text}" if self.guard else ""
        return f"Transition({self.action}, {self.pre.__repr__()}{guard})"

    def __str__(self):
        pre = format_tup(self.pre, str(self.guard), sep=" & ")
        return f"[{_h[_h.action, self.action]}] {pre} -> " + " + ".join(
            f"{format_str(p)}:{format_tup(*s_, sep=', ', wrap=True)}"
            if p != 1.0
            else f"{format_tup(*s_, sep=', ')}"
            for s_, p in self.post.items()
        )

    def __eq__(self, other: "Transition") -> bool:
        if not isinstance(other, Transition):
            other = transition(*other)
        return (*self,) == (*other,)

    def __hash__(self) -> int:
        return hash((*self,))

    def __getitem__(self, index):
        return (self.action, self.pre, self.guard, self.post)[index]

    def __add__(self, other: "Transition") -> "Transition":
        action = self.action
        pre = self.pre + other.pre
        guard = self.guard + other.guard
        post = self.__dist_product(other)
        active = self.active.union(other.active)
        return Transition(action, pre, guard, post, active)

    def __dist_product(self, other: "Transition") -> Distribution:
        """Calculates the product of two distributions"""
        dist1, dist2 = self.post, other.post
        # Split the list of distributions into two generators
        s_primes = itertools.product(dist1.keys(), dist2.keys())
        p_values = itertools.product(dist1.values(), dist2.values())
        # Calculate the product of all permutations of the distributions
        return imdict(
            zip(
                (tuple(map(operator.add, *s_)) for s_ in s_primes),
                (np.prod(p) for p in p_values),
            )
        )


def transition(
    action: str,
    pre: StateDescription,
    post: DistributionDescription = None,
    active: set[MDP] = None,
):
    pre, guards = partition(is_guard, list(flatten(pre)))
    pre = state(pre)

    if post is None:
        post = state(pre)

    if isinstance(post, (str, set, tuple, State)):
        post = imdict({state_update(post): 1.0})
    else:
        post = imdict({state_update(s_): p for s_, p in post.items()})

    return Transition(action, pre, guard(guards), post, active)


def compose_transitions(processes: list[MDP]) -> list[Transition]:
    transitions = []

    # List all process transitions
    process_transitions = [
        (pid, tr) for pid, p in enumerate(processes) for tr in p.transitions
    ]
    # Count the number of processes for each action
    global_actions = Counter(
        itertools.chain.from_iterable(
            (tr.action for tr in p.transitions) for p in processes
        )
    )
    # Create a dict of actions that appear in more than one process
    synched_actions = {
        a: defaultdict(list)
        for a, count in global_actions.items()
        if count > 1 and not a.startswith("tau")
    }

    for pid, tr in process_transitions:
        if tr.action in synched_actions:
            # Collect all transitions belonging to a synched action
            synched_actions[tr.action][pid].append(tr)
        else:
            transitions.append(tr)

    # Generate all permutations of synched transitions
    transitions += [
        reduce(operator.add, trs)
        for queue in synched_actions.values()
        for trs in itertools.product(*queue.values())
    ]

    return transitions
