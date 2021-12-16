from mdptools import MarkovDecisionProcess as MDP, state, graph, pr_max
from mdptools.set_methods import stubborn_sets

# %%
m1 = MDP(
    [
        ("a", "s0", {"s1": 0.2, "s2": 0.8}),
        ("b", "s0", {"s2": 0.7, "s3": 0.3}),
        ("tau_1", "s1"),
        ("x", "s2"),
        ("y", "s2"),
        ("z", "s2"),
        ("x", "s3"),
        ("z", "s3"),
    ],
    name="M1",
)
m2 = MDP([("x", "r0", "r1"), ("y", "r1", "r0"), ("z", "r1")], name="M2")
m3 = MDP([("c", "w0", "w1"), ("y", "w0"), ("tau_2", "w1")], name="M3")
m4 = MDP([("z", "v0", "v1"), ("y", "v0"), ("z", "v1")], name="M4")
m = MDP(m1, m2, m3, m4)

# %%
goal_states = {
    state("s0", "r0", "w1", "v0"),
    state("s2", "r0", "w1", "v0"),
    state("s3", "r0", "w1", "v0"),
}
m_red = MDP(*m.processes, set_method=stubborn_sets, goal_states=goal_states)

print(
    "Goal states:",
    ", ".join(map(lambda s: s.to_str(m_red, wrap=True), goal_states)),
)
print("Goal actions:", ", ".join(map(str, m_red.goal_actions)))

# %%
graph(*m.processes, m, m_red)

# %%
graph(m_red, highlight=True)

# %%
p = pr_max(m, goal_states)
p_red = pr_max(m_red, goal_states)
print(p, p_red)
