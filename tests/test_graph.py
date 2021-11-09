from mdptools import MarkovDecisionProcess as MDP, graph


def test_simple_graph(stmdp: MDP):
    expected = 'digraph {\n\tnode [fontsize=18]\n\tedge [fontsize=18]\n\tmargin=0.1 rankdir=TB ranksep=0.25 size=8.5\n\t{\n\t\tmdp_0_start [label=<<b>M</b>> fontsize=21.6 shape=none]\n\t\tmdp_0_start -> mdp_0_state_s0\n\t\tmdp_0_state_s0 [label=<<table cellpadding="2" border="0" cellborder="0"><tr><td><i>s</i><sub><font point-size="9.0">0</font></sub></td></tr></table>>]\n\t\tmdp_0_p_point_mdp_0_state_s0_a [label="" shape=point]\n\t\tmdp_0_state_s0 -> mdp_0_p_point_mdp_0_state_s0_a [label=<<table cellpadding="2" border="0" cellborder="0"><tr><td><i>a</i></td></tr></table>> arrowhead=none]\n\t\tmdp_0_p_point_mdp_0_state_s0_a -> mdp_0_state_s0 [label=<<table cellpadding="2" border="0" cellborder="0"><tr><td>.5</td></tr></table>>]\n\t\tmdp_0_state_s1 [label=<<table cellpadding="2" border="0" cellborder="0"><tr><td><i>s</i><sub><font point-size="9.0">1</font></sub></td></tr></table>>]\n\t\tmdp_0_p_point_mdp_0_state_s0_a -> mdp_0_state_s1 [label=<<table cellpadding="2" border="0" cellborder="0"><tr><td>.5</td></tr></table>>]\n\t\tmdp_0_state_s1 -> mdp_0_state_s1 [label=<<table cellpadding="2" border="0" cellborder="0"><tr><td>&tau;</td></tr></table>> minlen=2]\n\t}\n}'

    actual = stmdp.to_graph().source

    assert actual == expected


def test_graph_multiple():
    s = MDP([("a", "s0", {"s1": 0.3, "s2": 0.7}), ("b", "s0", "s3")], name="S")
    p = MDP([("a", "p0", "p1")], name="P")
    sp = MDP(s, p)

    dot = graph(s, p, sp)
    expected = 6
    actual = dot.source.count("{")

    assert actual == expected
