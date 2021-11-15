from mdptools import MarkovDecisionProcess as MDP
from mdptools.set_methods import stubborn_sets
from helpers import at_root, display_graph


def make_sensor(i: int) -> MDP:
    s = [f"active_{i}", f"prepare_{i}", f"detected_{i}", f"inactive_{i}"]
    return MDP(
        [
            (f"detect_{i}", s[0], {s[1]: 0.8, s[2]: 0.2}),
            ("warn!", s[1], s[2]),
            ("shutdown!", s[2], s[3]),
            ("tau", s[3]),
        ],
        init=s[0],
        name=f"S{i}",
    )


def make_device() -> MDP:
    s = ["running", "stopping", "off", "failed"]
    return MDP(
        [
            ("warn?", s[0], s[1]),
            ("shutdown?", s[0], {s[2]: 0.9, s[3]: 0.1}),
            ("shutdown?", s[1], s[2]),
            ("tau", s[2]),
            ("tau", s[3]),
        ],
        init=s[0],
        name="D",
    )


def make_system(n: int) -> MDP:
    processes = [make_sensor(i + 1) for i in range(n)]
    processes += [make_device()]
    return MDP(*processes)


# %%
system = make_system(2)

for p in system.processes:
    print(p)

# %%
display_graph(*system.processes, file_path="out/graphs/graph_kwiatkowska.gv")

# %%
print(system)

# %%
display_graph(
    system.rename(
        (r"^([a-z]{1,2}[aeiouy][^aeiouy]?|[a-z]{1,2}[^aeiouy])[a-z]*", r"\1")
    ),
    file_path="out/graphs/graph_kwiatkowska_composed.gv",
    set_method=stubborn_sets,
    highlight=True,
)

# %%
print(
    system.to_prism(
        at_root("out/prism/kwiatkowska_composed.prism"),
        set_method=stubborn_sets,
    )
)

# %%
for n in range(1, 6):
    test_system = make_system(n)
    state_space = list(test_system.search(silent=True))
    state_space_ps = list(
        test_system.search(set_method=stubborn_sets, silent=True)
    )
    t = len(state_space)
    r = len(state_space_ps)
    p = round(abs(t - r) / t * 100)
    print(f"{n} sensors: {t} ({r} reduced, {p}% reduction)")
