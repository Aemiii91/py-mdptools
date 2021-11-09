"""Unit-tests for the `parallel` module
"""
from mdptools import MarkovDecisionProcess as MDP
from mdptools.types import State
from mdptools.set_methods import persistent_set


def test_simple_composition():
    m1 = MDP(
        [("a", "s0", "s1"), ("b", "s1", {"s0": 0.5, "s2": 0.5}), ("c", "s2")],
        name="M1",
    )

    m2 = m1.remake(
        (r"[a-z]([0-9])", r"t\1"), {"a": "x", "b": "y", "c": "z"}, "M2"
    )

    m = MDP(m1, m2, name="M")

    assert m.states == {"s0", "s1", "s2", "t0", "t1", "t2"}
    assert m.actions == {"a", "b", "c", "x", "y", "z"}
    assert m.transitions == [
        ("a", "s0", "s1"),
        ("b", "s1", {"s0": 0.5, "s2": 0.5}),
        ("c", "s2"),
        ("x", "t0", "t1"),
        ("y", "t1", {"t0": 0.5, "t2": 0.5}),
        ("z", "t2"),
    ]
    assert m.name == "M"


def test_example_kwiatkowska2013(
    kwiatkowska_ms: MDP, kwiatkowska_md: MDP, kwiatkowska_pc: MDP
):
    expected = kwiatkowska_pc
    actual = MDP(kwiatkowska_ms, kwiatkowska_md, name="Ms||Md (Actual)")
    assert actual == expected


def test_complex_composition(
    hansen_m1: MDP, hansen_m2: MDP, hansen_m3: MDP, hansen_m4: MDP
):
    m = MDP(hansen_m1, hansen_m2, hansen_m3, hansen_m4)

    assert m is not None


def test_custom_transition_function(
    baier_p1: MDP, baier_p2: MDP, baier_rm: MDP
):
    count = 10

    def custom_transition_function(mdp: MDP, s: State):
        nonlocal count
        if count > 0:
            count -= 1
            return mdp.enabled(s)
        return []

    m = MDP(baier_p1, baier_p2, baier_rm)

    state_space = [
        s for s, _ in m.search(set_method=custom_transition_function)
    ]

    assert len(state_space) == 8


def test_persistent_set(baier_p1: MDP, baier_p2: MDP, baier_rm: MDP):
    m = MDP(baier_p1, baier_p2, baier_rm)
    state_space_ps = [s for s, _ in m.search(set_method=persistent_set)]
    assert len(state_space_ps) == 5
