from mdptools import MarkovDecisionProcess, use_colors
from mdptools.utils import stringify, literal_string


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
