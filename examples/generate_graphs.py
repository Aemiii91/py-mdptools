# %%
from IPython.display import Image, SVG, display

from mdptools import MarkovDecisionProcess, graph, use_colors

# use_colors()


def root_path(filename: str) -> str:
    from os.path import join, dirname

    return join(dirname(__file__), "..", filename)


def display_graph(dot):
    image_path = f"{dot.filename}.{dot.format}"
    if dot.format == "pdf":
        print(image_path)
    elif dot.format == "svg":
        display(SVG(filename=image_path))
    else:
        display(Image(filename=image_path))


# %%
Ms = MarkovDecisionProcess(
    {"s0": {"a": "s1"}, "s1": {"b": {"s0": 0.5, "s2": 0.5}}, "s2": "c"},
    A="a, b, c",
    name="Ms",
)

Mt = Ms.remake((r"[a-z]([0-9])", r"t\1"), ["x", "y", "z"], "Mt")

(M_collection := [Ms + Mt, Mt, Ms])

# %%
display_graph(
    graph(
        M_collection,
        root_path("graphs/graph_simple_composition.gv"),
        rankdir="LR",
    )
)

# %%
# The 4 MDPs from fig 1 in Hansen2011
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
M2 = MarkovDecisionProcess(
    {"r0": {"x": "r1"}, "r1": {"y": "r0", "z": "r1"}}, name="M2"
)
M3 = MarkovDecisionProcess(
    {"w0": {"c": "w1", "y": "w0"}, "w1": "tau_2"}, name="M3"
)
M4 = MarkovDecisionProcess(
    {"v0": {"z": "v1", "y": "v0"}, "v1": "z"}, name="M4"
)

display_graph(
    graph([M1, M2, M3, M4], root_path("graphs/multiple_graphs_test.gv"))
)

# %%
# Parallel composition of 4 MDPs
display_graph(graph(M1 + M2 + M3 + M4, root_path("graphs/graph_test.gv")))

# %%
m1 = MarkovDecisionProcess(
    {
        "noncrit_1": {"demand_1": "wait_1"},
        "wait_1": {"req_1": "wait_1", "enter_1": "crit_1"},
        "crit_1": {"exit_1": "noncrit_1"},
    },
    name="M1",
)

m2 = m1.remake(("_1", "_2"), ("_1", "_2"), "M2")

rm = MarkovDecisionProcess(
    {
        "idle": {
            "req_1": {"idle": 0.1, "p_1": 0.9},
            "req_2": {"idle": 0.1, "p_2": 0.9},
        },
        "p_1": {"enter_1": "idle"},
        "p_2": {"enter_2": "idle"},
    },
    name="RM",
)

display_graph(
    graph([m1, m2, rm, m1 + m2 + rm], root_path("graphs/graph_mutex.gv"))
)

# %%
