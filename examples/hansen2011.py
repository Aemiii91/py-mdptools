from mdptools import MarkovDecisionProcess

M1 = MarkovDecisionProcess(
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

M1["s0->a"] = {"s1": 0.8, "s2": 0.2}

print(M1, "\n")

M2 = MarkovDecisionProcess(
    {"r0": {"x": "r1"}, "r1": {"y": "r0", "z": "r1"}}, name="M2"
)
print(M2, "\n")

M3 = MarkovDecisionProcess(
    {"w0": {"c": "w1", "y": "w0"}, "w1": "tau_2"}, name="M3"
)
print(M3, "\n")

M4 = MarkovDecisionProcess(
    {"v0": {"z": "v1", "y": "v0"}, "v1": "z"}, name="M4"
)
print(M4, "\n")

M = M1 + M2 + M3 + M4

print(M)