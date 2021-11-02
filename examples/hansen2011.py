from mdptools import MarkovDecisionProcess
from helpers import display_graph, prism_file

# %%
m1 = MarkovDecisionProcess(
    {
        "s0": {"a": {"s1": 0.2, "s2": 0.8}, "b": {"s2": 0.7, "s3": 0.3}},
        "s1": "tau_1",
        "s2": {"x", "y", "z"},
        "s3": {"x", "z"},
    },
    S="s0,s1,s2,s3",
    A="a,b,x,y,z,tau_1",
    name="M1",
)
print(m1, "\n")

m2 = MarkovDecisionProcess(
    {"r0": {"x": "r1"}, "r1": {"y": "r0", "z": "r1"}}, name="M2"
)
print(m2, "\n")

m3 = MarkovDecisionProcess(
    {"w0": {"c": "w1", "y": "w0"}, "w1": "tau_2"}, name="M3"
)
print(m3, "\n")

m4 = MarkovDecisionProcess(
    {"v0": {"z": "v1", "y": "v0"}, "v1": "z"}, name="M4"
)
print(m4, "\n")

m = m1 | m2 | m3 | m4

print(m)

# %%
display_graph([m1, m2, m3, m4], "graphs/hansen2011_mdps.gv")

# %%
display_graph((m1 | m2 | m3 | m4), "graphs/hansen2011_combined.gv")

# %%
prism_file(m1, "generated.prism")

# %%
