from .utils.types import MarkovDecisionProcess as MDP, TransitionMap, Callable
from .utils import list_union, intersect, reduce, PARALLEL_SEPARATOR


def parallel_system(
    processes: list[MDP],
    callback: Callable[[list[str], list[MDP]], list[str]] = None,
) -> MDP:
    if callback is None:
        callback = enabled

    transition_map: TransitionMap = {}
    s_init = [p.init for p in processes]
    stack = [s_init]

    while len(stack) > 0:
        states = stack.pop()
        states_name = serialize(states, ",")
        if states_name not in transition_map:
            transition_map[states_name] = {}
            transitions = callback(states, processes)
            for t in transitions:
                stack += successor(states, t, processes)

    return MDP(transition_map)


def successor(
    states: list[str], transition: str, processes: list[MDP]
) -> list[list[str]]:
    succ = [
        processes[i][s, transition]
        for i, s in enumerate(states)
        if processes[i].enabled(s)
    ]

    return [succ]


def enabled(states: list[str], processes: list[MDP]) -> list[str]:
    actions = [processes[i].actions(s) for i, s in enumerate(states)]
    transitions = []
    return transitions


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
        name = combine_names(_ms.name, _mt.name, "||")
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
    n1: str, n2: str, sep: str = None, swap: bool = False
) -> str:
    if sep is None:
        sep = PARALLEL_SEPARATOR
    return n2 + sep + n1 if swap else n1 + sep + n2


def serialize(l: list[str], sep: str = None):
    return reduce(lambda a, b: combine_names(a, b, sep), l)
