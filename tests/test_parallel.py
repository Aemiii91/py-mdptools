"""Unit-tests for the `parallel` module
"""
from mdptools import MarkovDecisionProcess as MDP, parallel
from mdptools.parallel import enabled


def test_simple_composition():
    m1 = MDP(
        {"s0": {"a": "s1"}, "s1": {"b": {"s0": 0.5, "s2": 0.5}}, "s2": "c"},
        A="a, b, c",
        name="M1",
    )

    m2 = m1.remake(
        (r"[a-z]([0-9])", r"t\1"), {"a": "x", "b": "y", "c": "z"}, "M2"
    )

    m = parallel(m1, m2, name="M")

    assert m.is_valid
    assert len(m.S) == 9
    assert m.name == "M"


def test_example_kwiatkowska2013(
    kwiatkowska_ms: MDP, kwiatkowska_md: MDP, kwiatkowska_pc: MDP
):
    expected = kwiatkowska_pc
    actual = parallel(kwiatkowska_ms, kwiatkowska_md, name="Ms||Md (Actual)")
    assert actual == expected


def test_complex_composition(
    hansen_m1: MDP, hansen_m2: MDP, hansen_m3: MDP, hansen_m4: MDP
):
    m = parallel(hansen_m1, hansen_m2, hansen_m3, hansen_m4)

    assert m.is_valid and len(m.S) == 16


def test_custom_transition_function(
    baier_p1: MDP, baier_p2: MDP, baier_rm: MDP
):
    count = 10

    def custom_transition_function(states, processes):
        nonlocal count
        if count > 0:
            count -= 1
            return enabled(states, processes)
        return []

    m = parallel(
        baier_p1, baier_p2, baier_rm, callback=custom_transition_function
    )

    assert len(m) == 20
