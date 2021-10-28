"""Unit-tests for the main `mdp` module
"""
import pytest
from mdptools import MarkovDecisionProcess
from .utils import error_code

# pylint: disable=redefined-outer-name
@pytest.fixture
def M():
    return MarkovDecisionProcess(
        {"s0": {"a": {"s0": 0.5, "s1": 0.5}}, "s1": {"tau": {"s1": 1}}}
    )


def test_valid_mdp(M):
    assert M.shape == (2, 2)
    assert list(M.S) == ["s0", "s1"]
    assert list(M.A) == ["a", "tau"]
    assert M.is_valid


def test_invalid_req1():
    M = MarkovDecisionProcess({"s0": {"a": {"s1": 1}}})
    assert not M.is_valid
    assert len(M.errors) == 1
    assert error_code(M) == 0


def test_indexing_one(M):
    assert M["s0"] == {"a": {"s0": 0.5, "s1": 0.5}}


def test_indexing_two(M):
    assert M["s0", "a"] == {"s0": 0.5, "s1": 0.5}
    assert M["s0->a"] == {"s0": 0.5, "s1": 0.5}  # short version


def test_indexing_three(M):
    assert M["s0", "a", "s0"] == 0.5
    assert M["s0->a->s0"] == 0.5  # short version


def test_set_s_a_to_float():
    expected = MarkovDecisionProcess(
        {
            "s0_t0": {"detect": {"s1_t0": 0.8, "s2_t0": 0.2}},
            "s1_t0": {"warn": "s2_t1"},
            "s2_t0": {"shutdown": {"s3_t2": 0.9, "s3_t3": 0.1}},
            "s2_t1": {"shutdown": "s3_t2"},
            "s3_t2": {"off": 1},
            "s3_t3": {"fail"},
        },
        name="Ms||Md (Expected)",
    )

    assert expected.is_valid
