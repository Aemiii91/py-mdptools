from mdptools import MarkovDecisionProcess as MDP
from mdptools.set_methods import conflicting_transitions

from helpers import at_root, display_graph, display_dot
from mdptools.set_methods.algorithm3_stubborn_sets import stubborn_sets

# %%
m1 = MDP(
    [
        ("a", "s0", {"s1": 0.2, "s2": 0.8}),
        ("b", "s0", {"s2": 0.7, "s3": 0.3}),
        ("tau", "s1"),
        ("x", "s2"),
        ("y", "s2"),
        ("z", "s2"),
        ("x", "s3"),
        ("z", "s3"),
    ],
    name="M1",
)
print(m1, "\n")

m2 = MDP([("x", "r0", "r1"), ("y", "r1", "r0"), ("z", "r1")], name="M2")
print(m2, "\n")

m3 = MDP([("c", "w0", "w1"), ("y", "w0"), ("tau", "w1")], name="M3")
print(m3, "\n")

m4 = MDP([("z", "v0", "v1"), ("y", "v0"), ("z", "v1")], name="M4")
print(m4, "\n")

system = MDP(m1, m2, m3, m4)
print(system, "\n")

# %%
display_graph(m1, m2, m3, m4, file_path="out/graphs/hansen2011_mdps.gv")
display_dot(
    system.to_graph(
        at_root("out/graphs/hansen2011_combined.gv"),
        set_method=conflicting_transitions,
        highlight=True,
    )
)

# %%
print(m1.to_prism(at_root("out/prism/generated.prism")), "\n")
print(
    system.to_prism(
        at_root("out/prism/testing.prism"), set_method=stubborn_sets
    ),
    "\n",
)

# %%
