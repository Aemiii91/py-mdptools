from mdptools import MarkovDecisionProcess as MDP
from helpers import at_root, display_graph
from mdptools.set_methods import stubborn_sets


# %%
N = 2
processes = [
    MDP([("alpha", "s0", "s1"), ("delta", "s1", "s2")]),
    MDP([("beta", "t0", "t1"), ("gamma", "t1", "t2")]),
]

# %%
display_graph(*processes, file_path="out/graphs/figure_3.gv")

# %%
system = MDP(*processes)
state_space = len(list(system.search()))

print("State space:", state_space)
print(system, "\n")

# %%
display_graph(system, file_path="out/graphs/figure_3_parallel.gv")

# %%
display_graph(
    system,
    file_path="out/graphs/figure_3_parallel.gv",
    set_method=stubborn_sets,
)

# %%
display_graph(
    system,
    MDP(
        *system.processes, set_method=stubborn_sets, goal_states={("s2", "t2")}
    ),
    MDP(
        *system.processes, set_method=stubborn_sets, goal_states={("s2", "t1")}
    ),
    MDP(
        *system.processes, set_method=stubborn_sets, goal_states={("s1", "t1")}
    ),
    file_path="out/graphs/figure_3_parallel_g.gv",
    highlight=True,
)
