from mdptools import MarkovDecisionProcess, parallel
from mdptools.utils.prism import to_prism

from helpers import at_root, display_graph

# %%
m1 = MarkovDecisionProcess(
    {
        "noncrit_1": {"demand_1": "wait_1"},
        "wait_1": {"request_1": "wait_1", "enter_1": "crit_1"},
        "crit_1": {"exit_1": "noncrit_1"},
    },
    name="M1",
)
print(m1, "\n")

mi = lambda i: m1.remake(("_1", f"_{i}"), ("_1", f"_{i}"), f"M{i}")

m2 = mi(2)
print(m2, "\n")

rm = MarkovDecisionProcess(
    {
        "idle": {
            "request_1": {"idle": 0.1, "prepare_1": 0.9},
            "request_2": {"idle": 0.1, "prepare_2": 0.9},
        },
        "prepare_1": {"grant_1": "idle"},
        "prepare_2": {"grant_2": "idle"},
    },
    name="RM",
)
print(rm, "\n")

m = parallel(m1, m2, rm)
print(m, "\n")

# %%
display_graph([m1, m2, rm, m], "out/graphs/graph_baier2004.gv")

to_prism(m, at_root("out/prism/baier2004.prism"))
