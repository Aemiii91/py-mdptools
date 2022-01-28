"""Parallel composition tests"""
from mdptools import MarkovDecisionProcess as MDP
from mdptools.types import State
from mdptools.utils import logger, logging
from mdptools.set_methods import (
    conflicting_transitions,
    overmans_algorithm,
    stubborn_sets,
    transition_bias,
)


def test_simple_composition():
    """Simple composition of two MDPs"""
    m1 = MDP(
        [("a", "s0", "s1"), ("b", "s1", {"s0": 0.5, "s2": 0.5}), ("c", "s2")],
        name="M1",
    )

    m2 = m1.rename(
        (r"[a-z]([0-9])", r"t\1"), {"a": "x", "b": "y", "c": "z"}, "M2"
    )

    m = MDP(m1, m2, name="M")

    assert m.name == "M"
    assert set(iter(m)) == {"s0", "s1", "s2", "t0", "t1", "t2"}
    assert m.actions == {"a", "b", "c", "x", "y", "z"}

    expected = [
        ("a", "s0", "s1"),
        ("b", "s1", {"s0": 0.5, "s2": 0.5}),
        ("c", "s2"),
        ("x", "t0", "t1"),
        ("y", "t1", {"t0": 0.5, "t2": 0.5}),
        ("z", "t2"),
    ]
    assert all(tr in expected for tr in m.transitions)


def test_example_kwiatkowska2013(
    kwiatkowska_ms: MDP, kwiatkowska_md: MDP, kwiatkowska_pc: MDP
):
    """Composition of the example from [kwiatkowska2013]"""
    expected = kwiatkowska_pc
    actual = MDP(kwiatkowska_ms, kwiatkowska_md, name="Ms||Md (Actual)")
    assert actual == expected


def test_complex_composition(
    hansen_m1: MDP, hansen_m2: MDP, hansen_m3: MDP, hansen_m4: MDP
):
    """Composition of the example from [hansen2011]"""
    m = MDP(hansen_m1, hansen_m2, hansen_m3, hansen_m4)

    assert m is not None


def test_custom_transition_function(
    baier_p1: MDP, baier_p2: MDP, baier_rm: MDP
):
    """Custom set method for choosing transitions"""

    def custom_transition_function(mdp: MDP, s: State):
        return [mdp.enabled_take_one(s, avoid_self_loops=False)]

    m = MDP(baier_p1, baier_p2, baier_rm)

    state_space = [
        s for s, _ in m.search(set_method=custom_transition_function)
    ]

    assert len(state_space) == 7


def test_classic_search(godefroid_4_11: MDP):
    """Conflicting transitions algorithm"""
    logger.setLevel(logging.INFO)
    m = godefroid_4_11
    state_space = list(m.search())
    assert len(state_space) == 7
    logger.setLevel(logging.NOTSET)


def test_conflicting_transitions(godefroid_4_11: MDP):
    """Conflicting transitions algorithm"""
    logger.setLevel(logging.INFO)
    m = godefroid_4_11
    state_space = list(m.search(set_method=conflicting_transitions))
    assert len(state_space) == 7
    logger.setLevel(logging.NOTSET)


# def test_overmans_algorithm(godefroid_4_11: MDP):
#     """Overman's algorithm"""
#     logger.setLevel(logging.INFO)
#     m = godefroid_4_11
#     state_space = list(m.search(set_method=overmans_algorithm))
#     assert len(state_space) == 6
#     logger.setLevel(logging.NOTSET)


# def test_overmans_algorithm_with_bias(godefroid_4_11: MDP):
#     """Overman's algorithm"""
#     logger.setLevel(logging.INFO)
#     m = godefroid_4_11
#     state_space = list(
#         m.search(set_method=transition_bias(overmans_algorithm, "t4"))
#     )
#     assert len(state_space) == 7
#     logger.setLevel(logging.NOTSET)


def test_stubborn_sets(godefroid_4_11: MDP):
    """Stubborn sets algorithm"""
    logger.setLevel(logging.INFO)
    m = godefroid_4_11
    state_space = list(m.search(set_method=stubborn_sets))
    assert len(state_space) == 6
    logger.setLevel(logging.NOTSET)


def test_stubborn_sets_with_baier(baier_p1: MDP, baier_p2: MDP, baier_rm: MDP):
    """Stubborn sets algorithm with probabilities"""
    logger.setLevel(logging.INFO)
    m = MDP(baier_p1, baier_p2, baier_rm)
    state_space = list(m.search(set_method=stubborn_sets))
    assert len(state_space) == 10
    logger.setLevel(logging.NOTSET)
