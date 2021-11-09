from mdptools import MarkovDecisionProcess as MDP
from helpers import at_root, display_graph


def make_process(i: int):
    return MDP(
        [
            # format: (action, pre, post)
            (f"demand_{i}", f"noncrit_{i}", f"wait_{i}"),
            (f"request_{i}", (f"wait_{i}", "x=0"), f"wait_{i}"),
            (f"enter_{i}", (f"wait_{i}", f"x={i}"), f"crit_{i}"),
            (f"exit_{i}", f"crit_{i}", (f"noncrit_{i}", "x:=0")),
        ],
        init=f"noncrit_{i}",
        name=f"P{i}",
    )


def make_resource_manager(n: int):
    trs = []
    for i in range(1, n + 1):
        trs += [
            (f"request_{i}", "idle", {f"prepare_{i}": 0.9, "idle": 0.1}),
            (f"grant_{i}", f"prepare_{i}", ("idle", f"x:={i}")),
        ]
    return MDP(trs, init=("idle", "x:=0"), name="RM")


# %%
n = 2
processes = [make_process(i + 1) for i in range(n)]
processes += [make_resource_manager(n)]

# %%
display_graph(*processes, file_path="out/graphs/graph_baier2004.gv")

# %%
m = MDP(*processes)

m.to_prism(at_root("out/prism/baier2004.prism"))

print(m, "\n")

# %%
display_graph(m, file_path="out/graphs/graph_baier2004_parallel.gv")

# %%
