"""Unit-tests for the `validate` module
"""
import pytest
from mdptools import MarkovDecisionProcess as MDP, validate

from .helpers import error_code


def test_valid_mdp(stmdp: MDP):
    assert stmdp.states == {"s0", "s1"}
    assert stmdp.actions == {"a", "tau"}


def test_invalid_raise_exception():
    m = MDP([("a", "s0", "s1")])
    with pytest.raises(Exception):
        validate(m, raise_exception=True)


def test_invalid_req1():
    m = MDP([("a", "s0", "s1")])
    is_valid, errors = validate(m)
    assert not is_valid
    assert len(errors) == 1
    assert error_code(errors) == 0


def test_distribution_with_sum_not_1():
    m = MDP([("a", "s0", {"s0": 1, "s1": 0.5}), ("tau", "s1")])
    is_valid, errors = validate(m)
    assert not is_valid
    assert len(errors) == 1
    assert error_code(errors) == 1
