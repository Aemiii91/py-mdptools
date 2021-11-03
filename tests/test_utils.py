from mdptools import MarkovDecisionProcess, use_colors
from mdptools.utils import stringify, literal_string, to_prism


def test_stringify():
    use_colors(False)

    m = MarkovDecisionProcess(
        {"s0": {"a": {"s0": 0.5, "s1": 0.5}}, "s1": {"tau": {"s1": 1}}}
    )

    expected = "M -> MDP [Valid]:\n  S := (s0, s1), init := s0 // 2\n  A := (a, tau) // 2\n  en(s0) -> {a: {s0: .5, s1: .5}} // 1\n  en(s1) -> {tau: {s1: 1}} // 1"
    actual = stringify(m)

    assert actual == expected


def test_stringify_with_repr():
    use_colors(False)

    m = MarkovDecisionProcess(
        {"s0": {"a": {"s0": 0.5, "s1": 0.5}}, "s1": {"tau": {"s1": 1}}}
    )

    expected = "M -> MDP [Valid]:\n  S := (s0, s1), init := s0 // 2\n  A := (a, tau) // 2\n  en(s0) -> {a: {s0: .5, s1: .5}} // 1\n  en(s1) -> {tau: {s1: 1}} // 1"
    actual = m.__repr__()

    assert actual == expected


def test_stringify_with_colors():
    use_colors(True)

    m = MarkovDecisionProcess(
        {"s0": {"a": {"s0": 0.5, "s1": 0.5}}, "s1": {"tau": {"s1": 1}}}
    )

    s = stringify(m)

    assert isinstance(s, str) and "\x1b[" in s


def test_literal_string():
    use_colors(True)

    m = MarkovDecisionProcess(
        {"s0": {"a": {"s0": 0.5, "s1": 0.5}}, "s1": {"tau": {"s1": 1}}}
    )

    expected = "{s0: {a: {s0: .5, s1: .5}}, s1: {tau: {s1: 1}}}"
    actual = literal_string(m.transition_map, colors=False)

    assert actual == expected


def test_to_prism():
    m1 = MarkovDecisionProcess(
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

    expected = """mdp\nmodule M1\n\ts : [0..4] init 0;\n\n\t[a] s=0 -> 0.2:(s'=1) + 0.8:(s'=2);\n\t[b] s=0 -> 0.7:(s'=2) + 0.3:(s'=3);\n\t[tau_1] s=1 -> 1.0:(s'=1);\n\t[x] s=2 -> 1.0:(s'=2);\n\t[y] s=2 -> 1.0:(s'=2);\n\t[z] s=2 -> 1.0:(s'=2);\n\t[x] s=3 -> 1.0:(s'=3);\n\t[z] s=3 -> 1.0:(s'=3);\nendmodule"""

    actual = to_prism(m1)

    assert actual == expected
