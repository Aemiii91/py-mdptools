import itertools

from numpy.core.fromnumeric import prod

from .utils.types import (
    MarkovDecisionProcess as MDP,
    TransitionMap,
    Callable,
    Iterable,
    Union,
)
from .utils import (
    list_union,
    list_union_multi,
    intersect,
    reduce,
    PARALLEL_SEPARATOR,
)


def parallel_system(
    processes: list[MDP],
    callback: Callable[[list[str], list[MDP]], list[str]] = None,
) -> MDP:
    from .mdp import MarkovDecisionProcess as MDP

    if callback is None:
        callback = enabled

    transition_map: TransitionMap = {}
    s_init = tuple(p.init for p in processes)
    stack = [s_init]

    while len(stack) > 0:
        s = stack.pop()
        if s not in transition_map:
            transition_map[s] = {}
            transitions = callback(s, processes)
            for tr in transitions:
                _, action, post = tr
                succ = successor(s, tr)
                transition_map[s][action] = dict(zip(succ, post.values()))
                stack += succ

    return MDP(transition_map)


States = tuple[str]
Actions = dict[str, dict[str, float]]
Transition = tuple[States, str, list[States]]


def successor(states: States, transition: Transition) -> list[States]:
    succ = []
    pre, _, post = transition

    for post_states in post.keys():
        replace_map = dict(zip(pre, post_states))
        s_prime = tuple(replace_map[s] if s in pre else s for s in states)
        succ.append(s_prime)

    return succ


def enabled(states: States, processes: list[MDP]) -> list[Transition]:
    transitions = []
    enabled_actions = [processes[i].actions(s) for i, s in enumerate(states)]
    act_union = list_union_multi(enabled_actions)

    for action in act_union:
        should_sync, can_sync, sync_filter, filtered_actions = synchronized(
            action, enabled_actions, processes
        )
        if not should_sync or can_sync:
            tr = transition(
                tuple(apply_filter(states, sync_filter)),
                action,
                filtered_actions,
            )
            transitions.append(tr)

    return transitions


def transition(
    states: States,
    action: str,
    enabled_actions: list[list[str]],
) -> Transition:
    s_primes = (act[action].keys() for act in enabled_actions)
    p_values = (act[action].values() for act in enabled_actions)
    dist = dict(
        zip(
            itertools.product(*s_primes),
            (prod(p) for p in itertools.product(*p_values)),
        )
    )
    return (states, action, dist)


def synchronized(
    action: str, enabled_actions: list[list[str]], processes: list[MDP]
) -> tuple[bool, bool, list[int]]:
    sync_processes = [1 if action in p.A else 0 for p in processes]
    filtered_actions = apply_filter(enabled_actions, sync_processes)
    should_sync = sum(sync_processes) > 1
    can_sync = all(action in en for en in filtered_actions)
    return (
        should_sync,
        can_sync,
        sync_processes,
        filtered_actions,
    )


def apply_filter(l: Iterable, f: list[int]):
    return [x for i, x in enumerate(l) if f[i] == 1]


_ms: MDP = None
_mt: MDP = None
_transition_map: TransitionMap = {}
_actions_intersect: set[str] = set()


def parallel(ms: MDP, mt: MDP, name: str = None) -> MDP:
    """Performs parallel composition of two MDPs."""
    from .mdp import MarkovDecisionProcess as MDP

    global _transition_map, _actions_intersect, _ms, _mt

    _ms, _mt = ms, mt
    _transition_map = {}  # empty map for the new composed MDP
    _actions_intersect = intersect(_ms.A, _mt.A)  # synchronized actions

    # Start the parallel composition
    compose(_ms.init, _mt.init)
    actions_union = list_union(
        _ms.A, _mt.A
    )  # list union is used to preserve ordering
    init = combine_names(_ms.init, _mt.init)
    if name is None:
        name = f"{_ms.name}||{_mt.name}"
    return MDP(_transition_map, A=actions_union, init=init, name=name)


def compose(s, t, swap: bool = False):
    """Stands at state `(s,t)` and maps all enabled actions `en((s,t))`"""
    if swap:
        s, t = t, s
    s_name = combine_names(s, t)
    act_s, act_t = _ms.actions(s), _mt.actions(t)
    _transition_map[s_name] = None  # mark state `(s,t)` as visited
    _transition_map[s_name] = {
        # Map all actions possible from `s`
        **compose_actions(act_s, act_t, t),
        # Map all actions possible from `t`
        **compose_actions(act_t, act_s, s, True),
    }


def compose_actions(act_s, act_t, t, swap: bool = False):
    """Maps the possible actions of `s`, when standing at `(s,t)`"""
    action_map = {}
    for a in act_s:
        # If the `a` in `en(s)` does not exist in `mt.A` (No synchronization)
        if not a in _actions_intersect:
            # When no synchronization is required, we can take the action on `s`, while staying in `t`
            action_map[a] = compose_dist(act_s[a], {t: 1.0}, swap)
        # Check if synchronization can happen (`a` in `en(s)` and `en(t)`)
        # `not swap` ensures we only synchronize one way (avoid duplicates)
        elif a in act_t and not swap:
            # Synchronize the action, resulting in the product of two distributions
            action_map[a] = compose_dist(act_s[a], act_t[a], swap)
    return action_map


def compose_dist(dist_s, dist_t, swap):
    """Recursively runs `compose` on all possible next states `(s',t')`

    Returns the product of `dist(s)` and `dist(t)`
    """
    for s_prime in dist_s:
        for t_prime in dist_t:
            if not visited(s_prime, t_prime, swap):
                compose(s_prime, t_prime, swap)
    return dist_product(dist_s, dist_t, swap)


def visited(s, t, swap):
    """Checks whether the state `(s,t)` is visited"""
    return combine_names(s, t, swap=swap) in _transition_map


def dist_product(dist: dict, other_dist: dict, swap: bool = True) -> dict:
    return {
        combine_names(s_prime, t_prime, swap=swap): s_value * t_value
        for s_prime, s_value in dist.items()
        for t_prime, t_value in other_dist.items()
    }


def combine_names(
    n1: Union[tuple[str], str], n2: Union[tuple[str], str], swap: bool = False
) -> tuple[str]:
    if not isinstance(n1, tuple):
        n1 = (n1,)
    if not isinstance(n2, tuple):
        n2 = (n2,)
    return tuple(n2 + n1) if swap else tuple(n1 + n2)


def serialize(l: list[str], sep: str = None):
    return reduce(lambda a, b: combine_names(a, b, sep), l)
