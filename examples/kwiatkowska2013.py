from mdptools import MarkovDecisionProcess as MDP
from mdptools.set_methods import stubborn_sets
from helpers import display_graph


def make_sensor(i: int) -> MDP:
    s = [f"active_{i}", f"detected_{i}", f"alert_{i}", f"inactive_{i}"]
    return MDP(
        [
            (f"detect_{i}", s[0], {s[1]: 0.8, s[2]: 0.2}),
            (f"warn_{i}", s[1], s[2]),
            (f"shutdown_{i}", s[2], s[3]),
            (f"off_{i}", s[3]),
        ],
        init=s[0],
        name=f"S{i}",
    )


def make_device(n: int) -> MDP:
    s = ["running", "stopping", "off", "failing"]
    trs = [
        ("fail", s[3]),
    ]
    for i in range(n):
        trs += [
            (f"warn_{i}", s[0], s[1]),
            (f"shutdown_{i}", s[0], {s[2]: 0.9, s[3]: 0.1}),
            (f"shutdown_{i}", s[1], s[2]),
            (f"off_{i}", s[2]),
        ]
    return MDP(trs, init=s[0], name="D")


def make_system(n: int):
    processes = [make_sensor(i + 1) for i in range(n)]
    processes += [make_device(n)]
    processes += [MDP(*processes).rename((r"^([a-z])[a-z]+", r"\1"))]
    return processes


# %%
processes = make_system(2)

for p in processes:
    print(p)

# %%
display_graph(*processes[:-1], file_path="out/graphs/graph_kwiatkowska.gv")

# %%
display_graph(
    processes[-1],
    file_path="out/graphs/graph_kwiatkowska_composed.gv",
    set_method=stubborn_sets,
    highlight=True,
)
