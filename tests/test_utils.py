from pytest_mock import MockerFixture

from mdptools import MarkovDecisionProcess as MDP, use_colors
from mdptools.utils import format_str


def test_stringify(stmdp: MDP):
    use_colors(False)
    expected = (
        "mdp M:\n  init := s0\n  [a] s0 -> .5:s0 + .5:s1\n  [tau] s1 -> s1\n"
    )
    actual = stmdp.__str__()
    assert actual == expected


def test_stringify_with_repr(stmdp: MDP):
    use_colors(False)
    expected = "MDP(M)"
    actual = stmdp.__repr__()
    assert actual == expected


def test_stringify_with_colors(stmdp: MDP):
    use_colors(True)
    s = stmdp.__str__()
    assert isinstance(s, str) and "\x1b[" in s


def test_literal_string():
    use_colors(True)

    test = {"s0": {"a": {"s0": 0.5, "s1": 0.5}}, "s1": {"tau": {"s1": 1}}}

    expected = "{s0: {a: {s0: .5, s1: .5}}, s1: {tau: {s1: 1}}}"
    actual = format_str(test, use_colors=False)

    assert actual == expected


def test_to_prism(mocker: MockerFixture, hansen_m1: MDP):
    mck = mocker.patch("builtins.open", mocker.mock_open())

    expected = "mdp\n\nmodule M1\n  s : [0..4] init 4;\n\n  [a] s=0 -> 0.2:(s'=1) + 0.8:(s'=2);\n  [b] s=0 -> 0.7:(s'=2) + 0.3:(s'=3);\n  [x] s=3 -> (s'=3);\n  [z] s=3 -> (s'=3);\n  [x] s=2 -> (s'=2);\n  [y] s=2 -> (s'=2);\n  [z] s=2 -> (s'=2);\n  [tau] s=1 -> (s'=1);\nendmodule"

    actual = hansen_m1.to_prism("some_file.prism")

    mck.assert_called_once_with("some_file.prism", "w+", encoding="utf-8")
    mck().write.assert_called_once_with(expected)
    assert actual == expected
