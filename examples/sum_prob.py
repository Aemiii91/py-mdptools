from typing import Iterable
from mdptools import MarkovDecisionProcess as MDP
from mdptools.model import state
from mdptools.types import State, Action, StateDescription
from helpers import display_graph


class prob_max:
    def __init__(self, mdp: MDP, goal_states: Iterable[StateDescription]):
        self.mdp = mdp
        self.B = set(map(state, goal_states))
        self.S = set(map(state, mdp.states))

    def __call__(self, s: State) -> float:
        if isinstance(s, str):
            s = state(s)
        if s in self.B:
            return 1.0

        ret = max(self.sum_prob(s, a) for a in self.Act(s))
        return ret

    def Act(self, s: State) -> list[Action]:
        return [tr.action for tr in self.mdp.enabled(s)]

    def sum_prob(self, s: State, a: Action) -> float:
        return sum(self.mdp.P(s, a, t) * self(t) for t in self.S)


# %%
m = MDP(
    [
        ("beta", "s0", {"s1": 0.5, "s2": 0.5}),
        ("alpha", "s0", {"s2": 0.75, "s3": 0.25}),
        ("alpha", "s1", {"s0": 0.5, "s3": 0.5}),
        ("alpha", "s2", "s2"),
        ("alpha", "s3", "s3"),
    ]
)
display_graph(m, file_path="out/graphs/pmc_example_10.20.gv")

# %%
x = prob_max(m, {"s2"})
# p = x("s0")
# print(p)


# %%
import numpy as np
from scipy.optimize import fsolve


def func(x):
    return [
        x[0]
        - max(
            0.75 * x[2] + 0.25 * x[3],
            0.5 * x[2] + 0.5 * x[1],
        ),
        x[1] - 0.5 * x[0] + 0.5 * x[3],
        x[2] - 1.0,
        x[3] - 0.0,
    ]


n = 4
root = fsolve(func, [0.0] * n)
print([round(n, 3) for n in root])
print(
    all(np.isclose(func(root), [0.0] * n))
)  # func(root) should be almost 0.0.
