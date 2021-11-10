from mdptools import MarkovDecisionProcess as MDP
from mdptools.set_methods import persistent_set
from helpers import at_root, display_dot

system = MDP(
    [
        ("Take-L_1", ("a0", "f1=0"), ("a1", "f1:=1")),
        ("Take-R_1", ("a1", "f2=0"), ("a2", "f2:=1")),
        ("Release-L_1", "a2", ("a3", "f1:=0")),
        ("Release-R_1", "a3", ("a0", "f2:=0")),
        ("Take-L_2", ("b0", "f2=0"), ("b1", "f2:=1")),
        ("Take-R_2", ("b1", "f1=0"), ("b2", "f1:=1")),
        ("Release-L_2", "b2", ("b3", "f2:=0")),
        ("Release-R_2", "b3", ("b0", "f1:=0")),
    ],
    processes={"A": ("a0", "a1", "a2", "a3"), "B": ("b0", "b1", "b2", "b3")},
    init=("a0", "b0", "f1:=0, f2:=0"),
    name="TwoDiningPhilosophers",
)

# %%
display_dot(
    system.to_graph(
        at_root("out/graphs/baier2004_persistent.gv"),
        set_method=persistent_set,
        highlight=True,
    )
)
