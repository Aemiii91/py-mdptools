from mdptools import MarkovDecisionProcess as MDP, graph, pr_max, stubborn_sets
from mdptools.types import StateDescription


def make_system(n: int) -> tuple[MDP, set[StateDescription], str]:
    rng = range(1, n + 1)
    forks = list(range(1, max(n, 2) + 1))
    left = lambda i: forks[(i - 1) % len(forks)]
    right = lambda i: forks[i % len(forks)]
    philosophers = [make_philosopher(i, left(i), right(i)) for i in rng]
    return (
        MDP(*philosophers, name="DiningPhilosophers")
        if len(philosophers) > 1
        else philosophers[0],
        {f"done_{i}" for i in rng},
        f"Pmax=? [F {' & '.join(f'p{i-1}=6' for i in rng)}]",
    )


def make_philosopher(i: int, l: int, r: int) -> MDP:
    s = [
        f"{label}_{i}"
        for label in [
            "thinking",  # 0
            "try_left",  #  1
            "try_right",  #  2
            "got_left",  # 3
            "got_right",  # 4
            "eating",  # 5
            "done",  # 6
        ]
    ]

    label = lambda t: f"{t}_{i}"
    is_free = lambda f: f"f{f}=0"
    not_free = lambda f: f"f{f}=1"
    fork_take = lambda f: f"f{f}:=1"
    fork_release = lambda f: f"f{f}:=0"
    release_both = f"f{l}:=0, f{r}:=0"

    return MDP(
        [
            (label("draw_random"), s[0], {s[1]: 0.5, s[2]: 0.5}),
            (label("take_l"), (s[1], is_free(l)), (s[3], fork_take(l))),
            (label("take_r"), (s[2], is_free(r)), (s[4], fork_take(r))),
            (label("take_r"), (s[3], is_free(r)), (s[5], fork_take(r))),
            (label("release_l"), (s[3], not_free(r)), (s[0], fork_release(l))),
            (label("take_l"), (s[4], is_free(l)), (s[5], fork_take(l))),
            (label("release_r"), (s[4], not_free(l)), (s[0], fork_release(r))),
            (label("finish"), s[5], (s[6], release_both)),
            ("tau", s[6]),
        ],
        name=f"P{i}",
        init=(s[0], f"f{l}:=0, f{r}:=0"),
    )


if __name__ == "__main__":
    # %%
    mdp, goal_states, pf = make_system(2)
    print(mdp)
    print(goal_states)
    print(pf)

    # %%
    graph(mdp, set_method=stubborn_sets, highlight=True)

    # %%
    output, state_space = mdp.to_prism()
    print(output)
    print(len(state_space))

    # %%
    pr = pr_max(mdp, goal_states=goal_states, state_space=state_space)
    print(pr)
