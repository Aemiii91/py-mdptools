from mdptools import MarkovDecisionProcess, parallel
from helpers import display_graph

# %%
ms = MarkovDecisionProcess(
    {"s0": {"a": "s1"}, "s1": {"b": {"s0": 0.5, "s2": 0.5}}, "s2": "c"},
    A="a, b, c",
    name="Ms",
)

mt = ms.remake((r"[a-z]([0-9])", r"t\1"), ["x", "y", "z"], "Mt")

display_graph(
    [ms, mt, parallel(ms, mt)], "out/graphs/graph_simple_composition.gv"
)

# %%
s = MarkovDecisionProcess(
    {"s0": {"a": {"s1": 0.3, "s2": 0.7}, "b": "s3"}}, name="S"
)

p = MarkovDecisionProcess({"p0": {"a": "p1"}}, name="P")

sp = parallel(s, p)

display_graph([s, p, sp], "out/graphs/graph_example_sp1.gv")

# %%
s = MarkovDecisionProcess(
    {"s0": {"a": {"s1": 0.3, "s2": 0.7}, "b": "s3"}}, name="S"
)

p = MarkovDecisionProcess({"p0": {"a": "p1"}, "p1": {"b": "p0"}}, name="P")

sp = parallel(s, p)

display_graph([s, p, sp], "out/graphs/graph_example_sp2.gv")
