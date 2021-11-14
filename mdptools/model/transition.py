from ..types import (
    Command,
    dataclass,
    field,
    Action,
    Distribution,
    StateDescription,
    DistributionDescription,
    MarkovDecisionProcess as MDP,
    imdict,
    defaultdict,
    Iterable,
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
    remove_direction,
)
from .commands import Op, guard, Guard, is_guard
from .state import state, State, state_update


@dataclass(eq=True, frozen=True)
class Transition:
    """The data class used for Transitions, please use the `transition` function to
    create new instances
    """

    action: Action
    pre: State = field(compare=True)
    guard: Guard = field(compare=True)
    post: Distribution = field(compare=True)
    active: set[MDP] = None

    def is_enabled(self, s: State) -> bool:
        return all(ss in s for ss in self.pre) and self.guard(s.ctx)

    def in_conflict(self, other: "Transition") -> bool:
        """pre(t1) ∩ pre(t2) != Ø"""
        return any(ss in other.pre for ss in self.pre)

    def is_parallel(self, other: "Transition") -> bool:
        """active(t1) ∩ active(t2) == Ø"""
        return len(self.active.intersection(other.active)) == 0

    def can_be_dependent(self, other: "Transition") -> bool:
        """For all op1 in used(t1) and for all op2 in used(t2),
        there exists a pair op1, op2 that can-be-dependent
        """
        used, other_used = self.used(), other.used()
        # Check if one operation has a write while the other is nonempty
        return any(
            op1.can_be_dependent(op2) for op1 in used for op2 in other_used
        )

    def successors(self, s: State) -> dict[State, float]:
        """Return the possible successors after taking the transition in state `s`"""
        if not self.is_enabled(s):
            return {}
        return {
            (s - self.pre) + s_.apply(upd): p
            for (s_, upd), p in self.post.items()
        }

    def used(self) -> frozenset[Op]:
        """Returns a dict mapping used objects with r/w operations"""
        commands: list[Command] = [self.guard] + [
            upd for _, upd in self.post.keys()
        ]
        operations = itertools.chain.from_iterable(
            cmd.used() for cmd in commands
        )
        return frozenset(operations)

    def rename(
        self, states: dict[str, str], actions: dict[str, str]
    ) -> "Transition":
        """Renames the action label and states in the transition"""
        action = self.action
        if action in actions:
            action = actions[action]
        pre = self.pre.rename(states)
        guard = self.guard
        post = imdict(
            {(s_.rename(states), upd): p for (s_, upd), p in self.post.items()}
        )
        return Transition(action, pre, guard, post, self.active)

    def bind(self, processes: set[MDP]) -> "Transition":
        """Binds the transition to another set of processes"""
        return Transition(*self, active=processes)

    def __repr__(self) -> str:
        guard = f" & {self.guard.text}" if self.guard else ""
        return f"[{self.action}] {self.pre.__repr__()}{guard}"

    def __str__(self):
        pre = format_tup(self.pre, str(self.guard), sep=" & ")
        return f"[{_h.action(self.action)}] {pre} -> " + " + ".join(
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
        action = remove_direction(self.action)
        pre = self.pre + other.pre
        guard = self.guard + other.guard
        post = dist_product(self.post, other.post)
        active = self.active.union(other.active)
        return Transition(action, pre, guard, post, active)


def transition(
    action: str,
    pre: StateDescription,
    post: DistributionDescription = None,
    active: set[MDP] = None,
) -> Transition:
    """Create an instance of a Transition object

    Args:
        action (str): action label
        pre (StateDescription): the preset and optionally guards
        post (DistributionDescription, optional): a dict describing the probability distribution, in the form `{(s', [update]): p}`. If not supplied the postset will be the same as the preset. Defaults to None.
        active (set[MDP], optional): a set of processes which are active in the transition. Defaults to None.

    Returns:
        [Transition]: an instance of Transition
    """
    pre, guards = partition(is_guard, list(flatten(pre)))
    pre = state(pre)

    if post is None:
        post = state(pre)

    if isinstance(post, (str, set, tuple, State)):
        post = {state_update(post): 1.0}
    else:
        post = {state_update(s_): p for s_, p in post.items()}

    return Transition(action, pre, guard(guards), imdict(post), active)


def dist_product(dist1: Distribution, dist2: Distribution) -> Distribution:
    """Calculates the product of two distributions"""
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


def compose_transitions(processes: list[MDP]) -> list[Transition]:
    """Composes the transitions of multiple processes,
    merging transitions that needs to be synchronized
    """
    transitions = []

    # List all process transitions
    process_transitions = [
        (pid, tr) for pid, p in enumerate(processes) for tr in p.transitions
    ]
    # Count the number of processes for each action
    global_actions = Counter(
        itertools.chain.from_iterable(
            (remove_direction(tr.action) for tr in p.transitions)
            for p in processes
        )
    )
    # Create a dict of actions that appear in more than one process
    synched_actions = {
        a: defaultdict(list)
        for a, count in global_actions.items()
        if count > 1 and not a.startswith("tau")
    }

    for pid, tr in process_transitions:
        action = remove_direction(tr.action)
        if action in synched_actions:
            # Collect all transitions belonging to a synched action
            synched_actions[action][pid].append(tr)
        else:
            transitions.append(tr)

    # Generate all permutations of synched transitions
    for queue in synched_actions.values():
        for trs in itertools.product(*queue.values()):
            transitions += _merge_transitions(trs)

    return transitions


def _merge_transitions(trs: Iterable[Transition]) -> Transition:
    ingoing, outgoing = partition(lambda tr: tr.action.endswith("!"), trs)
    outgoing = list(outgoing)
    if not outgoing:
        return [reduce(operator.add, trs)]
    ingoing = reduce(operator.add, ingoing)
    return [tr + ingoing for tr in outgoing]
