import numpy as np
from scipy.optimize import fsolve

from ..types import (
    MarkovDecisionProcess as MDP,
    State,
    Callable,
    StateDescription,
    ActionMap,
)
from ..model import state


def equation_system(
    mdp: MDP,
    goal_states: frozenset[State],
    state_space: dict[State, ActionMap] = None,
) -> Callable[[list], list]:
    if state_space is None:
        state_space = dict(mdp.search())
    if isinstance(state_space, list):
        state_space = dict(state_space)

    act = {s: sum(act.values(), []) for s, act in state_space.items()}
    states: list[State] = list(act.keys())
    indices = {s: i for i, s in enumerate(states)}

    def prob_max(s: State):
        return lambda x: max(
            sum(
                p * x[indices[t]]
                for t, p in d.items()
                if not (t == s and p == 1.0)
            )
            for d in act[s]
        )

    value_functions = [
        (lambda _: 1.0)
        if s.is_goal(goal_states)
        else (lambda _: 0.0)
        if len(act[s]) == 0 or not can_reach(s, goal_states, act)
        else prob_max(s)
        for s in states
    ]

    value_iterator = lambda x: [
        x[i] - value_functions[i](x) for i, _ in enumerate(states)
    ]

    solve = lambda: {
        states[i]: p
        for i, p in enumerate(fsolve(value_iterator, [1.0] * len(indices)))
    }

    return (value_iterator, solve)


def validate(value_iterator, solution: dict[State, float]) -> bool:
    return all(
        np.isclose(
            value_iterator(list(solution.values())), [0.0] * len(solution)
        )
    )


can_reach_memo = {}


def can_reach(
    s: State,
    goal_states: frozenset[State],
    act: dict[State, list[dict[State, ActionMap]]],
    visited: set[State] = None,
) -> bool:
    if (s, goal_states) in can_reach_memo:
        return can_reach_memo[(s, goal_states)]

    result = False

    if not visited:
        visited = set()

    if s.is_goal(goal_states):
        result = True
    elif s in act and s not in visited:
        visited.add(s)
        next_states = [t for dist in act[s] for t in dist.keys() if t != s]
        result = any(
            can_reach(t, goal_states, act, visited) for t in next_states
        )

    can_reach_memo[(s, goal_states)] = result

    return result


memo = {}


def pr_max(
    mdp: MDP,
    s: State = None,
    goal_states: set[StateDescription] = None,
    state_space: list[tuple[State, ActionMap]] = None,
):
    goal_states = (
        frozenset(map(state, goal_states))
        if goal_states is not None
        else mdp.goal_states
    )

    if (mdp, goal_states) not in memo:
        _, solve = equation_system(mdp, goal_states, state_space)
        memo[(mdp, goal_states)] = solve()

    if s is None:
        s = mdp.init

    return memo[(mdp, goal_states)][s]
