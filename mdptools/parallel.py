import itertools
from collections import Counter, defaultdict
from operator import itemgetter
from numpy.core.fromnumeric import prod

from .types import (
    State,
    Action,
    DistributionMap,
    MarkovDecisionProcess as MDP,
    TransitionMap,
    Transition,
    Callable,
)
from .utils import apply_filter


def parallel(
    *processes: MDP,
    callback: Callable[[State, list[Transition]], list[Transition]] = None,
    name: str = None,
) -> MDP:
    """Performs parallel composition of two MDPs."""
    from .mdp import MarkovDecisionProcess as MDP

    if callback is None:
        callback = enabled

    if name is None:
        name = "||".join(p.name for p in processes)

    transition_map: TransitionMap = {}
    transitions = global_transitions(processes)
    s_init: State = State(p.init for p in processes)

    stack = [s_init]

    while len(stack) > 0:
        s = stack.pop()
        if s not in transition_map:
            # Register the global state
            transition_map[s] = {}
            # Iterate transitions returned by callback
            for tr in callback(s, transitions):
                # Get the successor states for the transition
                action, succ = successor(s, tr)
                transition_map[s][action] = succ
                # Add the discovered states to the stack
                stack += succ.keys()

    return MDP(transition_map, init=s_init, name=name)


def global_transitions(processes: list[MDP]) -> list[Transition]:
    """Generates a list of global transitions"""
    transitions = []
    placeholders = {}

    # List all process transitions
    process_transitions = [
        (pid, tr) for pid, p in enumerate(processes) for tr in p.transitions
    ]
    # Count the number of processes for each action
    global_actions = Counter(
        itertools.chain.from_iterable(p.A for p in processes)
    )
    # Create a dict of actions that appear in more than one process
    synched_actions = {
        a: defaultdict(list)
        for a, count in global_actions.items()
        if count > 1
    }

    for pid, (pre, action, post) in process_transitions:
        if action in synched_actions:
            # Create placeholder for adding in synched transitions
            if action not in placeholders:
                placeholders[action] = len(transitions)
            # Collect all transitions belonging to a synched action
            synched_actions[action][pid].append((pre, post))
        else:
            transitions.append(Transition(pre, action, post))

    # Generate all permutations of synched transitions
    synched_transitions = (
        (a, (zip(*c) for c in itertools.product(*queue.values())))
        for a, queue in synched_actions.items()
    )
    offset = 0

    for a, combinable in synched_transitions:
        # Combine all combinable transitions
        trs = [
            Transition(State(pre), a, dist_product(post))
            for pre, post in combinable
        ]
        # Insert the transitions at the placeholder
        idx = placeholders[a] + offset
        offset += len(trs) - 1
        transitions[idx:idx] = trs

    return transitions


def dist_product(distributions: list[DistributionMap]) -> DistributionMap:
    """Calculates the product of multiple distributions"""
    # Split the list of distributions into two generators
    s_primes = itertools.product(*(dist.keys() for dist in distributions))
    p_values = itertools.product(*(dist.values() for dist in distributions))
    # Calculate the product of all permutations of the distributions
    return dict(
        zip((State(s_) for s_ in s_primes), (prod(p) for p in p_values))
    )


def enabled(s: State, transitions: list[Transition]) -> list[Transition]:
    """Returns all enabled transitions in a global state"""
    return filter(lambda tr: all(sb in s for sb in tr.pre), transitions)


def disabled(s: State, transitions: list[Transition]) -> list[Transition]:
    """Returns all enabled transitions in a global state"""
    return filter(lambda tr: any(sb not in s for sb in tr.pre), transitions)


def successor(
    s: State, transition: Transition
) -> tuple[Action, DistributionMap]:
    """Generates a map of successor states and their probabilities"""
    pre, action, post = transition

    if any(sb not in s for sb in pre):
        raise Exception("Transition can not be taken on s")

    succ = {}

    for post_states, p_value in post.items():
        # Replace the states that are in the preset with the corresponding states in the postset
        replace_map = dict(zip(pre, post_states))
        s_prime = State(replace_map[s] if s in pre else s for s in s)
        succ[s_prime] = p_value

    return (action, succ)


def persistent_set(
    s: State, global_transitions: list[Transition]
) -> list[Transition]:
    transitions = []
    enabled_trs = list(enabled(s, global_transitions))
    disabled_trs = list(disabled(s, global_transitions))

    for tr in enabled_trs:
        if tr in global_transitions:
            transitions.append(tr)

    return transitions
