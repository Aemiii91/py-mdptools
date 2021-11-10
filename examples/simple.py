from mdptools import MarkovDecisionProcess as MDP
from mdptools.set_methods import persistent_set
from helpers import display_graph
from mdptools.utils.highlight import Highlight

# %%
ms = MDP(
    [("a", "s0", "s1"), ("b", "s1", {"s0": 0.5, "s2": 0.5}), ("tau", "s2")],
    name="Ms",
)

mt = ms.remake((r"[a-z]([0-9])", r"t\1"), {"a": "x", "b": "y"}, "Mt")

display_graph(
    ms, mt, MDP(ms, mt), file_path="out/graphs/graph_simple_composition.gv"
)

# %%
s = MDP([("a", "s0", {"s1": 0.3, "s2": 0.7}), ("b", "s0", "s3")], name="S")
p = MDP([("x", "p0", "p1")], name="P")
sp = MDP(s, p)

display_graph(s, p, sp, file_path="out/graphs/graph_example_sp1.gv")

# %%
s = MDP([("a", "s0", {"s1": 0.3, "s2": 0.7}), ("b", "s0", "s3")], name="S")
p = MDP([("x", "p0", "p1"), ("y", "p1", "p0")], name="P")
sp = MDP(s, p)

display_graph(s, p, sp, file_path="out/graphs/graph_example_sp2.gv")

# %%
m = MDP(
    [
        ("t1", "a0", ("a1", "x:=1")),
        ("t2", ("a0", "x=1"), ("a3", "x:=0")),
        ("t3", "a1", ("a2", "y:=0")),
        ("t4", "b0", ("b1", "y:=1")),
    ],
    processes={"A": ("a0", "a1", "a2", "a4"), "B": ("b0", "b1")},
    init=("a0", "b0", "x:=0, y:=0"),
)

display_graph(m, file_path="out/graphs/graph_example_godefroid-4.11.gv")

# %%
display_graph(
    m,
    file_path="out/graphs/graph_example_godefroid-4.11_persistent.gv",
    set_method=persistent_set,
)
