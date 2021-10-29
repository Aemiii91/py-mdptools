"""Unit-tests for the main `mdp` module
"""
import pytest
from mdptools import MarkovDecisionProcess


@pytest.mark.usefixtures("stmdp")
def test_indexing_one(stmdp: MarkovDecisionProcess):
    assert stmdp["s0"] == {"a": {"s0": 0.5, "s1": 0.5}}


@pytest.mark.usefixtures("stmdp")
def test_indexing_two(stmdp: MarkovDecisionProcess):
    assert stmdp["s0", "a"] == {"s0": 0.5, "s1": 0.5}
    assert stmdp["s0->a"] == {"s0": 0.5, "s1": 0.5}  # short version


@pytest.mark.usefixtures("stmdp")
def test_indexing_three(stmdp: MarkovDecisionProcess):
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
