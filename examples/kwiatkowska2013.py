from mdptools import MarkovDecisionProcess
from mdptools.parallel import parallel, persistent_set
from helpers import display_graph

# %%
ms = MarkovDecisionProcess(
    {
        "s0": {"detect": {"s1": 0.8, "s2": 0.2}},
        "s1": {"warn": "s2"},
        "s2": {"shutdown": "s3"},
        "s3": {"off"},
    },
    name="Ms",
)
print(ms, "\n")

md = MarkovDecisionProcess(
    {
        "t0": {"warn": "t1", "shutdown": {"t2": 0.9, "t3": 0.1}},
        "t1": {"shutdown": "t2"},
        "t2": {"off"},
        "t3": {"fail"},
    },
    name="Md",
)
print(md, "\n")

m = parallel(ms, md)
print(m)
print("\n".join(f"{tr.__repr__()}" for tr in m.global_transitions), "\n")

# %%
display_graph([ms, md, m], "out/graphs/graph_kwiatkowska.gv")

# %%
ms = MarkovDecisionProcess(
    {
        "s0": {"detect": {"s1": 0.8, "s2": 0.2}},
        "s1": {"warn": "s2"},
        "s2": {"shutdown": "s3"},
        "s3": {"off"},
    },
    name="Ms",
)
print(ms, "\n")

mt = ms.remake((r"s([0-9])", r"t\1"), name="Mt")
print(mt, "\n")

m = parallel(ms, mt)
print(m)
print("\n".join(f"{tr.__repr__()}" for tr in m.global_transitions), "\n")

# %%
display_graph([ms, mt, m], "out/graphs/graph_kwiatkowska_2.gv")
