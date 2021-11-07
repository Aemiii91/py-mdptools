import itertools
from collections import Counter, defaultdict
from numpy.core.fromnumeric import prod

from .types import (
    State,
    Action,
    Distribution,
    MarkovDecisionProcess as MDP,
    TransitionMap,
    Transition,
    Callable,
    Union,
)


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

    return MDP(
        transition_map, init=s_init, name=name, global_transitions=transitions
    )


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

    for pid, (action, pre, guard, post) in process_transitions:
        if action in synched_actions:
            # Create placeholder for adding in synched transitions
            if action not in placeholders:
                placeholders[action] = len(transitions)
            # Collect all transitions belonging to a synched action
            synched_actions[action][pid].append((pre, post))
        else:
            transitions.append(Transition(action, pre, None, post))

    # Generate all permutations of synched transitions
    synched_transitions = (
        (a, (zip(*c) for c in itertools.product(*queue.values())))
        for a, queue in synched_actions.items()
    )
    offset = 0

    for a, combinable in synched_transitions:
        # Combine all combinable transitions
        trs = [
            Transition(a, State(pre), None, dist_product(post))
            for pre, post in combinable
        ]
        # Insert the transitions at the placeholder
        idx = placeholders[a] + offset
        offset += len(trs) - 1
        transitions[idx:idx] = trs

    return transitions


def dist_product(distributions: list[Distribution]) -> Distribution:
    """Calculates the product of multiple distributions"""
    # Split the list of distributions into two generators
    s_primes = itertools.product(*(dist.keys() for dist in distributions))
    p_values = itertools.product(*(dist.values() for dist in distributions))
    # Calculate the product of all permutations of the distributions
    return dict(
        zip((State(s_) for s_ in s_primes), (prod(p) for p in p_values))
    )


def enabled(
    s: State, transitions: Union[list[Transition], Transition]
) -> list[Transition]:
    """Returns all enabled transitions in a state"""
    if isinstance(transitions, Transition):
        return list(enabled(s, [transitions]))
    return filter(lambda tr: all(ls in s for ls in tr.pre), transitions)


def enabled_take_one(s: State, transitions: list[Transition]) -> Transition:
    """Return the first enabled transition in a state"""
    return next(enabled(s, transitions), None)


def disabled(s: State, transitions: list[Transition]) -> list[Transition]:
    """Returns all disabled transitions in a state"""
    return filter(lambda tr: any(sb not in s for sb in tr.pre), transitions)


def successor(s: State, transition: Transition) -> tuple[Action, Distribution]:
    """Generates a map of successor states and their probabilities"""
    action, pre, guard, post = transition

    if any(ls not in s for ls in pre):
        raise Exception("Transition can not be taken on s")

    succ = {}

    for (s_, update), value in post.items():
        # Replace the states that are in the preset with the corresponding states in the postset
        replace_map = dict(zip(pre, s_))
        s_ = State(replace_map[ss] if ss in pre else ss for ss in s)
        succ[s_] = value

    return (action, succ)


def conflict(t1: Transition, t2: Transition) -> bool:
    return any(t1_ls in t2.pre for t1_ls in t1.pre)


def persistent_set(
    s: State, global_transitions: list[Transition]
) -> list[Transition]:
    transitions = [enabled_take_one(s, global_transitions)]

    if transitions[0] is None:
        return []

    for t in transitions:
        for t_ in global_transitions:
            if t_ in transitions:
                continue
            if conflict(t, t_):
                if enabled(s, t_):
                    transitions.append(t_)
                else:
                    return transitions

    return transitions
