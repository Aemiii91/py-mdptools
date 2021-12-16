from mdptools import MarkovDecisionProcess as MDP, graph
from mdptools.model import state
from mdptools.utils.prob_max import pr_max

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
goal_states = {state("s2")}
graph(m)

# %%
goal_actions = m.goal_actions(goal_states)
print(goal_actions)

# %%
p = pr_max(m, goal_states)
print(p)
