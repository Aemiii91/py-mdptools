from mdptools import MarkovDecisionProcess as MDP
from helpers import at_root, display_graph


def make_process(i: int):
    s = [f"noncrit_{i}", f"wait_{i}", f"crit_{i}"]
    return MDP(
        [
            (f"demand_{i}", s[0], s[1]),
            ("request!", (s[1], "x=0"), (s[1], f"y:={i}")),
            (f"enter_{i}", (s[1], f"x={i}"), s[2]),
            (f"exit_{i}", s[2], (s[0], "x:=0")),
        ],
        init=s[0],
        name=f"P{i}",
    )


def make_resource_manager():
    s = ["idle", "prepare", "reset"]
    return MDP(
        [
            ("request?", s[0], {s[2]: 0.1, s[1]: 0.9}),
            ("grant", s[1], (s[2], "x:=y")),
            ("reset", s[2], (s[0], "y:=0")),
        ],
        init=(s[0], "x:=0"),
        name="RM",
    )


# %%
N = 3
processes = [make_process(i) for i in range(1, N + 1)] + [
    make_resource_manager()
]

# %%
display_graph(*processes, file_path="out/graphs/graph_baier2004.gv")

# %%
system = MDP(*processes)
state_space = len(list(system.search()))

system.to_prism(at_root("out/prism/baier2004.prism"))

print("State space:", state_space)
print(system, "\n")

# %%
display_graph(system, file_path="out/graphs/graph_baier2004_parallel.gv")

# %%
