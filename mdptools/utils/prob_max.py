import numpy as np
from scipy.optimize import fsolve

from ..types import (
    MarkovDecisionProcess as MDP,
    State,
    Callable,
    StateDescription,
)
from ..model import state


def equation_system(
    mdp: MDP, goal_states: frozenset[State]
) -> Callable[[list], list]:
    act = {
        s: [dist for distributions in act.values() for dist in distributions]
        for s, act in mdp.search()
    }
    states: list[State] = list(act.keys())
    indices = {s: i for i, s in enumerate(states)}

    def prob_max(s: State, act: list[dict[State, float]]):
        return lambda x: max(
            sum(
                p * x[indices[t]]
                for t, p in dist.items()
                if not (t == s and p == 1.0)
            )
            for dist in act
        )

    value_functions = [
        (lambda _: 1.0)
        if s.is_goal(goal_states)
        else (lambda _: 0.0)
        if len(act[s]) == 0 or not mdp.can_reach(s, goal_states)
        else prob_max(s, act[s])
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


memo = {}


def pr_max(
    mdp: MDP, s: State = None, goal_states: set[StateDescription] = None
):
    goal_states = (
        frozenset(map(state, goal_states))
        if goal_states is not None
        else mdp.goal_states
    )
    if (mdp, goal_states) not in memo:
        _, solve = equation_system(mdp, goal_states)
        memo[(mdp, goal_states)] = solve()
    if s is None:
        s = mdp.init
    return memo[(mdp, goal_states)][s]
