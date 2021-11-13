"""Unit-tests for the main `mdp` module
"""
from mdptools import MarkovDecisionProcess as MDP


def test_enabled(stmdp: MDP):
    expected = ("a", "s0", {"s0": 0.5, "s1": 0.5})
    enabled = stmdp.enabled()
    assert stmdp.is_valid
    assert len(enabled) == 1
    assert enabled[0] == expected


def test_transitions(stmdp: MDP):
    expected = [("a", "s0", {"s0": 0.5, "s1": 0.5}), ("tau", "s1")]
    assert stmdp.transitions == expected


def test_remake(stmdp: MDP):
    m2 = stmdp.rename(("s", "t"), (r"([a-z]+)", r"\1_2"))
    assert m2.states == {"t0", "t1"}
    assert m2.actions == {"a_2", "tau_2"}


def test_remake_system(stmdp: MDP):
    m2 = stmdp.rename(("s", "t"), (r"([a-z]+)", r"\1_2"))

    system = MDP(stmdp, m2).rename([("s", "x"), ("t", "y")])

    expected = {"x0", "x1", "y0", "y1"}
    actual = system.states
    assert actual == expected


def test_instantiate_system():
    m = MDP(
        [
            ("t1", "a0", ("a1", "x:=1")),
            ("t2", ("a0", "x=1"), ("a3", "x:=0")),
            ("t3", "a1", ("a2", "y:=0")),
            ("t4", "b0", ("b1", "y:=1")),
        ],
        processes={"A": ("a0", "a1", "a2", "a4"), "B": ("b0", "b1")},
        init=("a0", "b0", "x:=0, y:=0"),
    )

    assert not m.is_process
