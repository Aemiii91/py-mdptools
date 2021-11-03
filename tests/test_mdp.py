"""Unit-tests for the main `mdp` module
"""
import pytest
from mdptools import MarkovDecisionProcess, parallel


@pytest.mark.usefixtures("stmdp")
def test_get_actions(stmdp: MarkovDecisionProcess):
    expected = {"a": {"s0": 0.5, "s1": 0.5}}
    assert stmdp.actions("s0") == expected
    assert stmdp["s0"] == expected


@pytest.mark.usefixtures("stmdp")
def test_get_distribution(stmdp: MarkovDecisionProcess):
    expected = {"s0": 0.5, "s1": 0.5}
    assert stmdp.dist("s0", "a") == expected
    assert stmdp["s0", "a"] == expected
    assert stmdp["s0->a"] == expected


@pytest.mark.usefixtures("stmdp")
def test_get_probability(stmdp: MarkovDecisionProcess):
    assert stmdp["s0", "a", "s0"] == 0.5
    assert stmdp["s0->a->s0"] == 0.5  # short version


@pytest.mark.usefixtures("stmdp")
def test_set_specific_p_value(stmdp: MarkovDecisionProcess):
    stmdp["s0->a->s0"] = 0.3
    stmdp["s0->a->s1"] = 0.7
    assert stmdp["s0->a->s0"] == 0.3 and stmdp["s0->a->s1"] == 0.7


@pytest.mark.usefixtures("stmdp")
def test_set_distribution(stmdp: MarkovDecisionProcess):
    stmdp["s0->a"] = {"s0": 0.3, "s1": 0.7}
    assert stmdp["s0->a->s0"] == 0.3 and stmdp["s0->a->s1"] == 0.7


@pytest.mark.usefixtures("stmdp")
def test_set_distribution_to_1(stmdp: MarkovDecisionProcess):
    stmdp["s0->a"] = 1.0
    assert not stmdp.is_valid


@pytest.mark.usefixtures("stmdp")
def test_set_distribution_to_set(stmdp: MarkovDecisionProcess):
    with pytest.raises(Exception):
        stmdp["s0->a"] = {"s0", "s1"}


@pytest.mark.usefixtures("stmdp")
def test_enabled_undefined_state(stmdp: MarkovDecisionProcess):
    en = stmdp.enabled("u0")
    assert en is None


@pytest.mark.usefixtures("stmdp")
def test_actions_undefined_state(stmdp: MarkovDecisionProcess):
    act = stmdp.actions("u0")
    assert act is None


@pytest.mark.usefixtures("stmdp")
def test_dist_undefined_state(stmdp: MarkovDecisionProcess):
    dist = stmdp.dist("u0", "a")
    assert dist is None


@pytest.mark.usefixtures("stmdp")
def test_add_state(stmdp: MarkovDecisionProcess):
    expected = len(stmdp) + 1
    stmdp["s2->x"] = 1.0
    actual = len(stmdp)
    assert actual == expected


@pytest.mark.usefixtures("stmdp")
def test_add_state_with_dict(stmdp: MarkovDecisionProcess):
    expected = len(stmdp) + 1
    stmdp["s2"] = {"x": "s2"}
    actual = len(stmdp)
    assert actual == expected


@pytest.mark.usefixtures("stmdp")
def test_add_state_with_str(stmdp: MarkovDecisionProcess):
    expected = len(stmdp) + 1
    stmdp["s2"] = "x"
    actual = len(stmdp)
    assert actual == expected


@pytest.mark.usefixtures("stmdp")
def test_add_new_s_prime(stmdp: MarkovDecisionProcess):
    expected = len(stmdp) + 1
    stmdp["s0->x->s2"] = 1.0
    actual = len(stmdp)
    assert actual == expected


@pytest.mark.usefixtures("stmdp")
def test_remake(stmdp: MarkovDecisionProcess):
    m2 = stmdp.remake(("s", "t"), (r"([a-z])", r"\1_2"))
    expected = {"t0", "t1"}
    actual = set(m2.S)
    assert actual == expected


@pytest.mark.usefixtures("stmdp")
def test_remake_system(stmdp: MarkovDecisionProcess):
    m2 = stmdp.remake(("s", "t"), (r"([a-z])", r"\1_2"))

    system = parallel(stmdp, m2).remake([("s", "x"), ("t", "y")])

    expected = {("x0", "y0"), ("x1", "y0"), ("x1", "y1"), ("x0", "y1")}
    actual = set(system.S)
    assert actual == expected
