from mdptools.mdp2 import MarkovDecisionProcess2 as MDP


def make_process(i: int):
    return MDP(
        {
            "name": f"P{i}",
            "init": (f"noncrit_{i}", "x:=0"),
            "transitions": [
                # format: (action, pre, post)
                (f"demand_{i}", f"noncrit_{i}", f"wait_{i}"),
                (f"request_{i}", (f"wait_{i}", "x=0"), f"wait_{i}"),
                (f"enter_{i}", (f"wait_{i}", f"x={i}"), f"crit_{i}"),
                (f"exit_{i}", f"crit_{i}", (f"noncrit_{i}", "x:=0")),
            ],
        }
    )


def make_resource_manager(n: int):
    trs = []
    for i in range(1, n + 1):
        trs += [
            (f"request_{i}", "idle", {f"prepare_{i}": 0.9, "idle": 0.1}),
            (f"grant_{i}", f"prepare_{i}", ("idle", f"x:={i}")),
        ]
    return MDP({"name": "RM", "init": ("idle", "x:=0"), "transitions": trs})


n = 3
processes = [make_process(i) for i in range(1, n + 1)]
processes += [make_resource_manager(n)]

for process in processes:
    print(process, "\n")
