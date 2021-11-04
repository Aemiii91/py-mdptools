"""Unit-tests for the main `mdp` module
"""
import pytest
from mdptools import MarkovDecisionProcess, parallel
from mdptools.types import State


def test_get_actions(stmdp: MarkovDecisionProcess):
    expected = {"a": {State("s0"): 0.5, State("s1"): 0.5}}
    assert stmdp.actions("s0") == expected
    assert stmdp["s0"] == expected


def test_get_distribution(stmdp: MarkovDecisionProcess):
    expected = {State("s0"): 0.5, State("s1"): 0.5}
    assert stmdp.dist("s0", "a") == expected
    assert stmdp["s0", "a"] == expected
    assert stmdp["s0->a"] == expected


def test_get_probability(stmdp: MarkovDecisionProcess):
    assert stmdp["s0", "a", "s0"] == 0.5
    assert stmdp["s0->a->s0"] == 0.5  # short version


def test_set_specific_p_value(stmdp: MarkovDecisionProcess):
    stmdp["s0->a->s0"] = 0.3
    stmdp["s0->a->s1"] = 0.7
    assert stmdp["s0->a->s0"] == 0.3 and stmdp["s0->a->s1"] == 0.7


def test_set_distribution(stmdp: MarkovDecisionProcess):
    stmdp["s0->a"] = {"s0": 0.3, "s1": 0.7}
    assert stmdp["s0->a->s0"] == 0.3 and stmdp["s0->a->s1"] == 0.7


def test_set_distribution_to_1(stmdp: MarkovDecisionProcess):
    stmdp["s0->a"] = 1.0
    assert not stmdp.is_valid


def test_set_distribution_to_set(stmdp: MarkovDecisionProcess):
    with pytest.raises(Exception):
        stmdp["s0->a"] = {"s0", "s1"}


def test_enabled_undefined_state(stmdp: MarkovDecisionProcess):
    en = stmdp.enabled("u0")
    assert en is None


def test_actions_undefined_state(stmdp: MarkovDecisionProcess):
    act = stmdp.actions("u0")
    assert act is None


def test_dist_undefined_state(stmdp: MarkovDecisionProcess):
    dist = stmdp.dist("u0", "a")
    assert dist is None


def test_add_state(stmdp: MarkovDecisionProcess):
    expected = len(stmdp) + 1
    stmdp["s2->x"] = 1.0
    actual = len(stmdp)
    assert actual == expected


def test_add_state_with_dict(stmdp: MarkovDecisionProcess):
    expected = len(stmdp) + 1
    stmdp["s2"] = {"x": "s2"}
    actual = len(stmdp)
    assert actual == expected


def test_add_state_with_str(stmdp: MarkovDecisionProcess):
    expected = len(stmdp) + 1
    stmdp["s2"] = "x"
    actual = len(stmdp)
    assert actual == expected


def test_add_new_s_prime(stmdp: MarkovDecisionProcess):
    expected = len(stmdp) + 1
    stmdp["s0->x->s2"] = 1.0
    actual = len(stmdp)
    assert actual == expected


def test_remake(stmdp: MarkovDecisionProcess):
    m2 = stmdp.remake(("s", "t"), (r"([a-z])", r"\1_2"))
    expected = {State("t0"), State("t1")}
    actual = set(m2.S)
    assert actual == expected


def test_remake_system(stmdp: MarkovDecisionProcess):
    m2 = stmdp.remake(("s", "t"), (r"([a-z])", r"\1_2"))

    system = parallel(stmdp, m2).remake([("s", "x"), ("t", "y")])

    expected = {
        State("x0", "y0"),
        State("x1", "y0"),
        State("x1", "y1"),
        State("x0", "y1"),
    }
    actual = set(system.S)
    assert actual == expected
