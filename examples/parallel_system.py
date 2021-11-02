from mdptools import MarkovDecisionProcess
from mdptools.parallel import parallel_system

# %%
m1 = MarkovDecisionProcess(
    {
        "noncrit_1": {"demand_1": "wait_1"},
        "wait_1": {"request_1": "wait_1", "enter_1": "crit_1"},
        "crit_1": {"exit_1": "noncrit_1"},
    },
    name="M1",
)

mi = lambda i: m1.remake(("_1", f"_{i}"), ("_1", f"_{i}"), f"M{i}")

m2 = mi(2)

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


parallel_system([m1, m2, rm])
