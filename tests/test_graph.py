from mdptools import MarkovDecisionProcess, graph, parallel


def test_simple_graph(stmdp: MarkovDecisionProcess):
    expected = 'digraph {\n\tnode [fontsize=18]\n\tedge [fontsize=18]\n\tmargin=0.1 rankdir=TB ranksep=0.25 size=8.5\n\tmdp_M_start [label=<<b>M</b>> fontsize=21.6 shape=none]\n\tmdp_M_start -> mdp_M_state_s0\n\tmdp_M_state_s0 [label=<<i><table cellpadding="2" border="0" cellborder="0"><tr><td>s<sub><font point-size="9.0">0</font></sub></td></tr></table></i>>]\n\tmdp_M_p_point_s0_a [label="" shape=point]\n\tmdp_M_state_s0 -> mdp_M_p_point_s0_a [label=<<i><table cellpadding="2" border="0" cellborder="0"><tr><td>a</td></tr></table></i>> arrowhead=none]\n\tmdp_M_p_point_s0_a -> mdp_M_state_s0 [label=<<i><table cellpadding="2" border="0" cellborder="0"><tr><td>.5</td></tr></table></i>>]\n\tmdp_M_p_point_s0_a -> mdp_M_state_s1 [label=<<i><table cellpadding="2" border="0" cellborder="0"><tr><td>.5</td></tr></table></i>>]\n\tmdp_M_state_s1 [label=<<i><table cellpadding="2" border="0" cellborder="0"><tr><td>s<sub><font point-size="9.0">1</font></sub></td></tr></table></i>>]\n\tmdp_M_state_s1 -> mdp_M_state_s1 [label=<<i><table cellpadding="2" border="0" cellborder="0"><tr><td>&tau;</td></tr></table></i>> minlen=2]\n}'

    actual = graph(stmdp).source

    assert actual == expected


def test_graph_multiple():
    s = MarkovDecisionProcess(
        {"s0": {"a": {"s1": 0.3, "s2": 0.7}, "b": "s3"}}, name="S"
    )
    p = MarkovDecisionProcess({"p0": {"a": "p1"}}, name="P")
    sp = parallel(s, p)

    dot = graph([s, p, sp])
    expected = 4
    actual = dot.source.count("{")

    assert actual == expected
