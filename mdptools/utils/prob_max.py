from collections import defaultdict
import numpy as np
from scipy.optimize import fsolve

from ..types import (
    MarkovDecisionProcess as MDP,
    State,
    StateDescription,
    Callable,
)
from ..model import state


memo = {}


def can_reach(mdp: MDP, s: State, goal_states: set[State]):
    return any(t in goal_states for t, _ in mdp.search(s))


def equation_system(
    mdp: MDP, goal_states: frozenset[State]
) -> Callable[[list], list]:
    act = {
        s: [dist for act_ in act.values() for dist in act_]
        for s, act in mdp.search()
    }
    states = list(act.keys())
    indices = {s: i for i, s in enumerate(states)}

    def prob_max(act: list[dict[State, float]]):
        return lambda x: max(
            sum(p * x[indices[t]] for t, p in dist.items()) for dist in act
        )

    value_functions = [
        (lambda _: 1.0)
        if s in goal_states
        else (lambda _: 0.0)
        if not can_reach(mdp, s, goal_states)
        else prob_max(act[s])
        for s in states
    ]

    value_iterator = lambda x: [
        x[i] - value_functions[i](x) for i, _ in enumerate(states)
    ]

    solve = lambda: {
        states[i]: round(p, 8)
        for i, p in enumerate(fsolve(value_iterator, [1.0] * len(indices)))
    }

    return (value_iterator, solve)


def validate(value_iterator, solution: dict[State, float]) -> bool:
    return all(
        np.isclose(
            value_iterator(list(solution.values())), [0.0] * len(solution)
        )
    )


def pr_max(mdp: MDP, goal_states: set[StateDescription], s: State = None):
    goal_states = frozenset(state(s) for s in goal_states)
    if (mdp, goal_states) not in memo:
        _, solve = equation_system(mdp, goal_states)
        memo[(mdp, goal_states)] = solve()
    if s is None:
        s = mdp.init
    return memo[(mdp, goal_states)][s]
