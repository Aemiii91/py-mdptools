from random import random

from mdptools import MarkovDecisionProcess as MDP, graph, stubborn_sets, pr_max
from mdptools.types import StateDescription


def make_system(n: int) -> tuple[MDP, set[StateDescription], str]:
    if n <= 1:
        return (None, None, None)
    rng = range(1, n + 1)
    coins = [make_coin(i, p_values(i - 1)) for i in rng]
    return (
        MDP(*coins),
        {f"h_{i}" for i in rng},
        f"Pmax=? [F {' & '.join(f'p{i-1}=1' for i in rng)}]",
    )


def make_coin(i: int, p: float) -> MDP:
    return MDP(
        [
            (
                f"flip_{i}",
                f"u_{i}",
                {f"h_{i}": round(p, 2), f"t_{i}": round(1 - p, 2)},
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


def main():
    # %%
    n = 3
    mdp, goal_states, pf = make_system(n)
    print(mdp)
    print(goal_states)
    print(pf)

    # %%
    graph(*mdp.processes)

    # %%
    mdp_g = mdp.rename(name="M_goal")
    mdp_g.set_method = stubborn_sets
    mdp_g.goal_states = goal_states
    mdp_r = mdp.rename(name="M_red")
    mdp_r.set_method = stubborn_sets
    print(mdp_g.goal_actions)

    # %%
    save_loc = f"out/graphs/coins_{n}_reduced"
    graph(mdp_g, highlight=True, file_path=save_loc)

    # %%
    save_loc = f"out/graphs/coins_{n}_with_goal"
    graph(mdp_r, highlight=True, file_path=save_loc)

    # %%
    output, state_space = mdp_g.to_prism()
    print(output)

    # %%
    original_size = len(list(mdp.search(silent=True)))
    print(len(state_space), "vs", original_size)

    # %%
    pr = pr_max(mdp, goal_states=goal_states, state_space=state_space)
    print(pr)


# %%
if __name__ == "__main__":
    main()
