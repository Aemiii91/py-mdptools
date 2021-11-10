from mdptools import MarkovDecisionProcess as MDP, graph


def test_simple_graph(stmdp: MDP):
    expected = 5
    actual = stmdp.to_graph().source.count("->")
    assert actual == expected


def test_graph_multiple():
    s = MDP([("a", "s0", {"s1": 0.3, "s2": 0.7}), ("b", "s0", "s3")], name="S")
    p = MDP([("a", "p0", "p1")], name="P")
    sp = MDP(s, p)

    dot = graph(s, p, sp)
    expected = 6
    actual = dot.source.count("{")

    assert actual == expected
