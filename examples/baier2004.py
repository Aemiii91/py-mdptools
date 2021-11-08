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
m1 = make_process(1)
print(m1, "\n")

m2 = make_process(2)
print(m2, "\n")

rm = make_resource_manager(2)
print(rm, "\n")

# %%
display_graph(m1, m2, rm, file_path="out/graphs/graph_baier2004.gv")

# %%
m = MDP(m1, m2, rm)
print(m, "\n")

# %%
display_graph(m, file_path="out/graphs/graph_baier2004_parallel.gv")

# %%
# print(to_prism(m, at_root("out/prism/baier2004.prism")), "\n")

# %%
m_ps = MDP(m1, m2, rm)

# %%
display_graph(m_ps, file_path="out/graphs/graph_baier2004_persistent_set.gv")
