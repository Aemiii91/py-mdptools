import pytest

from mdptools import MarkovDecisionProcess
from mdptools.types import State


@pytest.fixture
def stmdp():
    return MarkovDecisionProcess(
        {"s0": {"a": {"s0": 0.5, "s1": 0.5}}, "s1": {"tau": {"s1": 1}}}
    )


@pytest.fixture
def hansen_m1():
    return MarkovDecisionProcess(
        {
            "s0": {"a": {"s1": 0.2, "s2": 0.8}, "b": {"s2": 0.7, "s3": 0.3}},
            "s1": "tau_1",
            "s2": {"x", "y", "z"},
            "s3": {"x", "z"},
        },
        S="s0,s1,s2,s3",
        A="a,b,x,y,z,tau_1",
        name="M1",
    )


@pytest.fixture
def hansen_m2():
    return MarkovDecisionProcess(
        {"r0": {"x": "r1"}, "r1": {"y": "r0", "z": "r1"}}, name="M2"
    )


@pytest.fixture
def hansen_m3():
    return MarkovDecisionProcess(
        {"w0": {"c": "w1", "y": "w0"}, "w1": "tau_2"}, name="M3"
    )


@pytest.fixture
def hansen_m4():
    return MarkovDecisionProcess(
        {"v0": {"z": "v1", "y": "v0"}, "v1": "z"}, name="M4"
    )


@pytest.fixture
def baier_p1():
    return MarkovDecisionProcess(
        {
            "noncrit_1": {"demand_1": "wait_1"},
            "wait_1": {"request_1": "wait_1", "enter_1": "crit_1"},
            "crit_1": {"exit_1": "noncrit_1"},
        },
        name="P1",
    )


@pytest.fixture
def baier_p2():
    return MarkovDecisionProcess(
        {
            "noncrit_2": {"demand_2": "wait_2"},
            "wait_2": {"request_2": "wait_2", "enter_2": "crit_2"},
            "crit_2": {"exit_2": "noncrit_2"},
        },
        name="P2",
    )


@pytest.fixture
def baier_rm():
    return MarkovDecisionProcess(
        {
            "idle": {
                "request_1": {"idle": 0.1, "prepare_1": 0.9},
                "request_2": {"idle": 0.1, "prepare_2": 0.9},
            },
            "prepare_1": {"grant_1": "idle"},
            "prepare_2": {"grant_2": "idle"},
        },
        name="RM",
    )


@pytest.fixture
def kwiatkowska_ms():
    return MarkovDecisionProcess(
        {
            "s0": {"detect": {"s1": 0.8, "s2": 0.2}},
            "s1": {"warn": "s2"},
            "s2": {"shutdown": "s3"},
            "s3": {"off"},
        },
        name="Ms",
    )


@pytest.fixture
def kwiatkowska_md():
    return MarkovDecisionProcess(
        {
            "t0": {"warn": "t1", "shutdown": {"t2": 0.9, "t3": 0.1}},
            "t1": {"shutdown": "t2"},
            "t2": {"off"},
            "t3": {"fail"},
        },
        name="Md",
    )


@pytest.fixture
def kwiatkowska_pc():
    return MarkovDecisionProcess(
        {
            state("s0", "t0"): {
                "detect": {state("s1", "t0"): 0.8, state("s2", "t0"): 0.2}
            },
            state("s1", "t0"): {"warn": state("s2", "t1")},
            state("s2", "t0"): {
                "shutdown": {state("s3", "t2"): 0.9, state("s3", "t3"): 0.1}
            },
            state("s2", "t1"): {"shutdown": state("s3", "t2")},
            state("s3", "t2"): {"off"},
            state("s3", "t3"): {"fail"},
        },
        name="Ms||Md (Expected)",
    )
