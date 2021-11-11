from mdptools import MarkovDecisionProcess as MDP
from mdptools.set_methods import (
    transition_bias,
    conflicting_transitions,
    overmans_algorithm,
    stubborn_sets,
)
from mdptools.types import SetMethod
from helpers import display_graph


def make_example(set_method: SetMethod = None, name: str = None) -> MDP:
    return MDP(
        [
            ("t1", "a0", ("a1", "x:=1")),
            ("t2", ("a0", "x=1"), ("a3", "x:=0")),
            ("t3", "a1", ("a2", "y:=0")),
            ("t4", "b0", ("b1", "y:=1")),
        ],
        processes={"A": ("a0", "a1", "a2", "a4"), "B": ("b0", "b1")},
        init=("a0", "b0", "x:=0, y:=0"),
        name=name,
        set_method=set_method,
    )


# %%
display_graph(
    make_example(conflicting_transitions, "Conflicting transitions"),
    make_example(overmans_algorithm, "Overman's algorithm"),
    make_example(
        transition_bias(overmans_algorithm, "t4"), "Overman's algorithm (t4)"
    ),
    make_example(stubborn_sets, "Stubborn sets"),
    file_path="out/graphs/graph_example_godefroid-4.11.gv",
    highlight=True,
)

# %%
