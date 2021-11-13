from mdptools import MarkovDecisionProcess as MDP
from helpers import display_graph

# %%
ms = MDP(
    [
        ("detect", "s0", {"s1": 0.8, "s2": 0.2}),
        ("warn", "s1", "s2"),
        ("shutdown", "s2", "s3"),
        ("off", "s3"),
    ],
    name="Ms",
)
print(ms, "\n")

md = MDP(
    [
        ("warn", "t0", "t1"),
        ("shutdown", "t0", {"t2": 0.9, "t3": 0.1}),
        ("shutdown", "t1", "t2"),
        ("off", "t2"),
        ("fail", "t3"),
    ],
    name="Md",
)
print(md, "\n")

m = MDP(ms, md)
print(m)

# %%
display_graph(ms, md, m, file_path="out/graphs/graph_kwiatkowska.gv")

# %%
mt = ms.rename((r"s([0-9])", r"t\1"), name="Mt")
print(mt, "\n")

m = MDP(ms, mt)
print(m)

# %%
display_graph(ms, mt, m, file_path="out/graphs/graph_kwiatkowska_2.gv")
