"""Unit-tests for the `parallel` module
"""
from mdptools import MarkovDecisionProcess, parallel
from mdptools.parallel import enabled


def test_simple_composition():
    m1 = MarkovDecisionProcess(
        {"s0": {"a": "s1"}, "s1": {"b": {"s0": 0.5, "s2": 0.5}}, "s2": "c"},
        A="a, b, c",
        name="M1",
    )

    m2 = m1.remake(
        (r"[a-z]([0-9])", r"t\1"), {"a": "x", "b": "y", "c": "z"}, "M2"
    )

    m = parallel(m1, m2, name="M")

    assert m.is_valid
    assert len(m.S) == 9
    assert m.name == "M"


def test_example_kwiatkowska2013():
    ms = MarkovDecisionProcess(
        {
            "s0": {"detect": {"s1": 0.8, "s2": 0.2}},
            "s1": {"warn": "s2"},
            "s2": {"shutdown": "s3"},
            "s3": {"off"},
        },
        name="Ms",
    )

    md = MarkovDecisionProcess(
        {
            "t0": {"warn": "t1", "shutdown": {"t2": 0.9, "t3": 0.1}},
            "t1": {"shutdown": "t2"},
            "t2": {"off"},
            "t3": {"fail"},
        },
        name="Md",
    )

    expected = MarkovDecisionProcess(
        {
            ("s0", "t0"): {"detect": {("s1", "t0"): 0.8, ("s2", "t0"): 0.2}},
            ("s1", "t0"): {"warn": ("s2", "t1")},
            ("s2", "t0"): {"shutdown": {("s3", "t2"): 0.9, ("s3", "t3"): 0.1}},
            ("s2", "t1"): {"shutdown": ("s3", "t2")},
            ("s3", "t2"): {"off"},
            ("s3", "t3"): {"fail"},
        },
        name="Ms||Md (Expected)",
    )

    actual = parallel(ms, md, name="Ms||Md (Actual)")

    assert actual == expected


def test_complex_composition():
    m1 = MarkovDecisionProcess(
        {
            "s0": {"a": {"s1": 0.2, "s2": 0.8}, "b": {"s2": 0.7, "s3": 0.3}},
            "s1": "tau_1",
            "s2": {"x", "y", "z"},
            "s3": {"x", "z"},
        },
        name="M1",
    )

    m2 = MarkovDecisionProcess(
        {"r0": {"x": "r1"}, "r1": {"y": "r0", "z": "r1"}}, name="M2"
    )

    m3 = MarkovDecisionProcess(
        {"w0": {"c": "w1", "y": "w0"}, "w1": "tau_2"}, name="M3"
    )

    m4 = MarkovDecisionProcess(
        {"v0": {"z": "v1", "y": "v0"}, "v1": "z"}, name="M4"
    )

    m = parallel(m1, m2, m3, m4)

    assert m.is_valid and len(m.S) == 16


def test_custom_transition_function():
    m1 = MarkovDecisionProcess(
        {
            "noncrit_1": {"demand_1": "wait_1"},
            "wait_1": {"request_1": "wait_1", "enter_1": "crit_1"},
            "crit_1": {"exit_1": "noncrit_1"},
        },
        name="M1",
    )
    m2 = m1.remake(("_1", "_2"), ("_1", "_2"), "M2")
    rm = MarkovDecisionProcess(
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

    count = 10

    def custom_transition_function(states, processes):
        nonlocal count
        if count > 0:
            count -= 1
            return enabled(states, processes)
        return []

    m = parallel(m1, m2, rm, callback=custom_transition_function)

    assert len(m) == 20
