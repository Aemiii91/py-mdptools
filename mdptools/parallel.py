import itertools
from numpy.core.fromnumeric import prod

from .types import (
    Action,
    DistributionMap,
    MarkovDecisionProcess as MDP,
    TransitionMap,
    States,
    Transition,
    Callable,
)
from .utils import apply_filter


def parallel(
    *processes: MDP,
    callback: Callable[[list[str], list[MDP]], list[str]] = None,
    name: str = None,
) -> MDP:
    """Performs parallel composition of two MDPs."""
    from .mdp import MarkovDecisionProcess as MDP

    if callback is None:
        callback = enabled

    transition_map: TransitionMap = {}
    s_init: States = tuple(p.init for p in processes)

    stack = [s_init]

    while len(stack) > 0:
        states = stack.pop()
        if states not in transition_map:
            # Register the global state
            transition_map[states] = {}
            # Generate transitions via callback
            transitions = callback(states, processes)
            for tr in transitions:
                # Get the successor states for the transition
                action, succ = successor(states, tr)
                transition_map[states][action] = succ
                # Add the discovered states to the stack
                stack += succ.keys()

    if name is None:
        name = "||".join(p.name for p in processes)

    return MDP(transition_map, init=s_init, name=name)


def successor(
    states: States, transition: Transition
) -> tuple[Action, DistributionMap]:
    """Generates a map of successor states and their probabilities"""
    pre, action, post = transition

    succ = {}

    for post_states, p_value in post.items():
        # Replace the states that are in the preset with the corresponding states in the postset
        replace_map = dict(zip(pre, post_states))
        s_prime = tuple(replace_map[s] if s in pre else s for s in states)
        succ[s_prime] = p_value

    return (action, succ)


def enabled(states: States, processes: list[MDP]) -> list[Transition]:
    """Returns all enabled transitions in a global state"""
    transitions = []
    # Get the actions from every process that are enabled in s(i)
    enabled_actions = [processes[i].actions(s) for i, s in enumerate(states)]
    # Get the union of all enabled actions, `list` gives more deterministic results
    act_union = list(
        dict.fromkeys(itertools.chain.from_iterable(enabled_actions))
    )

    for action in act_union:
        # Boolean mapping of processes which contain `action`
        sync_filter = [action in p.A for p in processes]
        # A list of the action's distributions from each process
        distributions = [
            act[action] if action in act else None
            for act in apply_filter(enabled_actions, sync_filter)
        ]
        # Check if more than one process contains the `action`
        sync_required = sum(sync_filter) > 1
        # Check that all processes containing `action` also have it enabled in s(i)
        sync_enabled = all(dist is not None for dist in distributions)

        if not sync_required or sync_enabled:
            transitions.append(
                (
                    tuple(apply_filter(states, sync_filter)),  # preset
                    action,  # transition label
                    dist_product(distributions),  # postset distribution
                )
            )

    return transitions


def dist_product(distributions: list[DistributionMap]) -> DistributionMap:
    """Calculates the product of multiple distributions"""
    # Split the list of distributions into two generators
    s_primes = (dist.keys() for dist in distributions)
    p_values = (dist.values() for dist in distributions)
    # Calculate the product of all permutations of the distributions
    return dict(
        zip(
            itertools.product(*s_primes),
            (prod(p) for p in itertools.product(*p_values)),
        )
    )
