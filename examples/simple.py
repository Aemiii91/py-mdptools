from mdptools import MarkovDecisionProcess as MDP
from helpers import display_graph

# %%
ms = MDP(
    [("a", "s0", "s1"), ("b", "s1", {"s0": 0.5, "s2": 0.5}), ("c", "s2")],
    name="Ms",
)

mt = ms.remake((r"[a-z]([0-9])", r"t\1"), ["x", "y", "z"], "Mt")

display_graph(
    ms, mt, MDP(ms, mt), file_path="out/graphs/graph_simple_composition.gv"
)

# %%
s = MDP([("a", "s0", {"s1": 0.3, "s2": 0.7}), ("b", "s0", "s3")], name="S")
p = MDP([("a", "p0", "p1")], name="P")
sp = MDP(s, p)

display_graph(s, p, sp, file_path="out/graphs/graph_example_sp1.gv")

# %%
s = MDP([("a", "s0", {"s1": 0.3, "s2": 0.7}), ("b", "s0", "s3")], name="S")
p = MDP([("a", "p0", "p1"), ("b", "p1", "p0")], name="P")
sp = MDP(s, p)

display_graph(s, p, sp, file_path="out/graphs/graph_example_sp2.gv")
