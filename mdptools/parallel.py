import itertools
from numpy.core.fromnumeric import prod

from .utils.types import (
    MarkovDecisionProcess as MDP,
    TransitionMap,
    Callable,
    Iterable,
)
from .utils import list_union_multi


def parallel(
    *processes: list[MDP],
    callback: Callable[[list[str], list[MDP]], list[str]] = None,
    name: str = None,
) -> MDP:
    """Performs parallel composition of two MDPs."""
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

    if name is None:
        name = "||".join(p.name for p in processes)

    return MDP(transition_map, name=name)


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
