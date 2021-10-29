"""Unit-tests for the `validate` module
"""
import pytest
from mdptools import MarkovDecisionProcess, validate

from .helpers import error_code


@pytest.mark.usefixtures("stmdp")
def test_valid_mdp(stmdp: MarkovDecisionProcess):
    assert stmdp.shape == (2, 2)
    assert list(stmdp.S) == ["s0", "s1"]
    assert list(stmdp.A) == ["a", "tau"]
    assert stmdp.is_valid


def test_invalid_req1():
    M = MarkovDecisionProcess({"s0": {"a": {"s1": 1}}})
    is_valid = validate(M, raise_exception=False)
    assert not is_valid
    assert len(M.errors) == 1
    assert error_code(M) == 0


def test_distribution_with_sum_not_1():
    M = MarkovDecisionProcess(
        {"s0": {"a": {"s0": 1, "s1": 0.5}}, "s1": {"tau": {"s1": 1}}}
    )
    is_valid = validate(M, raise_exception=False)
    assert not is_valid
    assert len(M.errors) == 1
    assert error_code(M) == 1
