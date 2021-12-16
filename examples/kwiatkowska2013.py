from mdptools import MarkovDecisionProcess as MDP, graph, pr_max
from mdptools.set_methods import stubborn_sets

from sensor_system import make_system, make_anon_device, make_anon_sensor


# %%
m = MDP(make_anon_sensor(), make_anon_device()).rename(
    (r"^([a-z])[a-z]*", r"\1")
)

# %%
graph(
    *m.processes,
    file_path="out/graphs/example_processes",
    file_format="pdf",
)

# %%
graph(m, file_path="out/graphs/example_system", file_format="pdf")

# %%
goal_states = {"f"}
m = make_system(2).rename(
    (r"^([a-z])[a-z]*", r"\1")
    # (r"^([a-z]{1,2}[aeiouy][^aeiouy]?|[a-z]{1,2}[^aeiouy])[a-z]*", r"\1")
)
m.goal_states = goal_states

print(m)

print(
    "Goal states:",
    ", ".join(map(lambda s: s.to_str(m, wrap=True), m.goal_states)),
)
print("Goal actions:", ", ".join(map(str, m.goal_actions)))

# %%
graph(
    m,
    file_path="out/graphs/example_2_composed",
    file_format="pdf",
    set_method=stubborn_sets,
    highlight=True,
)

# %%
p = pr_max(m, goal_states=goal_states)
print(p)

# %%
m_red = MDP(*m.processes, set_method=stubborn_sets)
graph(
    m_red,
    file_path="out/graphs/example_2_reduced",
    file_format="pdf",
    set_method=stubborn_sets,
)

# %%
p_red = pr_max(m_red, goal_states=goal_states)
print(p_red)

# %%
