import pytest

from mdptools import MarkovDecisionProcess


@pytest.fixture
def stmdp():
    return MarkovDecisionProcess(
        {"s0": {"a": {"s0": 0.5, "s1": 0.5}}, "s1": {"tau": {"s1": 1}}}
    )
