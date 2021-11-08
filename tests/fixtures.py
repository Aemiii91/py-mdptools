import pytest

from mdptools import MarkovDecisionProcess as MDP
from mdptools.types import State


@pytest.fixture
def stmdp():
    return MDP([("a", "s0", {"s0": 0.5, "s1": 0.5}), ("tau", "s1")])


@pytest.fixture
def hansen_m1():
    return MDP(
        [
            ("a", "s0", {"s1": 0.2, "s2": 0.8}),
            ("b", "s0", {"s2": 0.7, "s3": 0.3}),
            ("tau", "s1"),
            ("x", "s2"),
            ("y", "s2"),
            ("z", "s2"),
            ("x", "s3"),
            ("z", "s3"),
        ],
        name="M1",
    )


@pytest.fixture
def hansen_m2():
    return MDP([("x", "r0", "r1"), ("y", "r1", "r0"), ("z", "r1")], name="M2")


@pytest.fixture
def hansen_m3():
    return MDP([("c", "w0", "w1"), ("y", "w0"), ("tau", "w1")], name="M3")


@pytest.fixture
def hansen_m4():
    return MDP([("z", "v0", "v1"), ("y", "v0"), ("z", "v1")], name="M4")


@pytest.fixture
def baier_p1():
    return MDP(
        [
            ("demand_1", "noncrit_1", "wait_1"),
            ("request_1", ("wait_1", "x=0"), "wait_1"),
            ("enter_1", ("wait_1", "x=1"), "crit_1"),
            ("exit_1", "crit_1", ("noncrit_1", "x:=0")),
        ],
        init="noncrit_1",
        name="P1",
    )


@pytest.fixture
def baier_p2():
    return MDP(
        [
            # format: (action, pre, post)
            ("demand_2", "noncrit_2", "wait_2"),
            ("request_2", ("wait_2", "x=0"), "wait_2"),
            ("enter_2", ("wait_2", "x=2"), "crit_2"),
            ("exit_2", "crit_2", ("noncrit_2", "x:=0")),
        ],
        init="noncrit_2",
        name="P2",
    )


@pytest.fixture
def baier_rm():
    return MDP(
        [
            ("request_1", "idle", {"prepare_1": 0.9, "idle": 0.1}),
            ("request_2", "idle", {"prepare_2": 0.9, "idle": 0.1}),
            ("grant_1", "prepare_1", "idle"),
            ("grant_2", "prepare_2", "idle"),
        ],
        init=("idle", "x:=0"),
        name="RM",
    )


@pytest.fixture
def kwiatkowska_ms():
    return MDP(
        [
            ("detect", "s0", {"s1": 0.8, "s2": 0.2}),
            ("warn", "s1", "s2"),
            ("shutdown", "s2", "s3"),
            ("off", "s3"),
        ],
        name="Ms",
    )


@pytest.fixture
def kwiatkowska_md():
    return MDP(
        [
            ("warn", "t0", "t1"),
            ("shutdown", "t0", {"t2": 0.9, "t3": 0.1}),
            ("shutdown", "t1", "t2"),
            ("off", "t2"),
            ("fail", "t3"),
        ],
        name="Md",
    )


@pytest.fixture
def kwiatkowska_pc():
    return MDP(
        [
            ("detect", "s0", {"s1": 0.8, "s2": 0.2}),
            ("warn", ("s1", "t0"), ("s2", "t1")),
            ("shutdown", ("s2", "t0"), {("s3", "t2"): 0.9, ("s3", "t3"): 0.1}),
            ("shutdown", ("s2", "t1"), ("s3", "t2")),
            ("off", ("s3", "t2")),
            ("fail", "t3"),
        ],
        init=("s0", "t0"),
        name="Ms||Md (Expected)",
    )
