from random import random

from mdptools import MarkovDecisionProcess as MDP, graph, stubborn_sets, pr_max
from mdptools.types import StateDescription


def make_system(n: int) -> tuple[MDP, set[StateDescription], str]:
    rng = range(1, n + 1)
    coins = [make_coin(i, p_values(i - 1)) for i in rng]
    return (
        MDP(*coins) if n > 1 else coins[0],
        {f"heads_{i}" for i in rng},
        f"Pmax=? [F {' & '.join(f'p{i-1}=1' for i in rng)}]",
    )


def make_coin(i: int, p: float) -> MDP:
    return MDP(
        [
            (
                f"flip_{i}",
                f"unknown_{i}",
                {f"heads_{i}": round(p, 2), f"tails_{i}": round(1 - p, 2)},
            )
        ],
        name=f"C{i}",
    )


_p_values = []


def p_values(i: int) -> float:
    global _p_values

    if i > len(_p_values) - 1:
        _p_values += [
            random() * 0.8 + 0.1 for _ in range(i - len(_p_values) + 1)
        ]

    return _p_values[i]


if __name__ == "__main__":
    # %%
    mdp, goal_states, pf = make_system(3)
    print(mdp)
    print(goal_states)
    print(pf)

    # %%
    graph(*mdp.processes)

    # %%
    mdp.goal_states = goal_states
    print(mdp.goal_actions)
    graph(mdp, set_method=stubborn_sets, highlight=True)

    # %%
    output, state_space = mdp.to_prism()
    print(output)
    print(len(state_space))

    # %%
    pr = pr_max(mdp, goal_states=goal_states, state_space=state_space)
    print(pr)
