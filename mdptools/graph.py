from .types import (
    Action,
    MarkovDecisionProcess as MDP,
    SetMethod,
    Digraph,
)
from .utils import re, format_str, tuple_str, id_register
from .model import State, state


def graph(
    *processes: MDP,
    file_path: str = None,
    file_format: str = "svg",
    engine: str = "dot",
    rankdir: str = "TB",
    size: float = 8.5,
    set_method: SetMethod = None,
    highlight: bool = None,
) -> Digraph:
    """Renders the graph of a given MDP and saves it to `file_path`."""
    from graphviz import Digraph

    set_fontsize = {"fontsize": f"{round(graph.point_size, 2)}"}
    dot = Digraph(
        filename=file_path,
        format=file_format,
        engine=engine,
        node_attr=set_fontsize,
        edge_attr=set_fontsize,
    )
    dot.attr(size=f"{size}", rankdir=rankdir, ranksep="0.25", margin="0.1")

    for process in processes:
        with dot.subgraph() as subgraph:
            _render_mdp(subgraph, process, set_method, highlight)

    if file_path is not None:
        dot.render()

    return dot


graph.point_size = 18
graph.p_color = None
graph.label_padding = 2
graph.shorten_state_labels = False


_node_map: dict[State, str] = {}
_node_ids = id_register()


def _render_mdp(
    dot: Digraph,
    mdp: MDP,
    set_method: SetMethod,
    highlight: bool,
):
    global _node_map, _node_ids
    _node_map = {}
    _node_ids = id_register()

    # Add arrow pointing to the start state
    init = mdp.init
    if mdp.is_process:
        init = state(init, ctx={})
    init_name = f"mdp_{id(mdp)}_start"
    init_label = f"<<b>{mdp.name}</b>>"
    dot.node(
        init_name,
        label=init_label,
        shape="none",
        fontsize=f"{round(graph.point_size * 1.2, 2)}",
    )
    dot.edge(init_name, _serialize(mdp, init, prefix="node_"))

    if mdp.is_process:
        _render_process(dot, mdp)
    else:
        _render_system(dot, mdp, set_method, highlight)


def _render_process(dot: Digraph, mdp: MDP):
    for a, s, guard, dist in mdp.transitions:
        # Add a state node to the graph
        s_name = _add_node(dot, s, mdp)
        _add_edge(dot, s_name, a, dist, mdp, second_line=guard.text)


def _render_system(
    dot: Digraph, mdp: MDP, set_method: SetMethod, highlight: bool
):
    from graphviz import Digraph

    same_rank = [[]]
    curr_level = 0

    if highlight:
        search = mdp.bfs(set_method=False, silent=True)
    else:
        search = mdp.bfs(set_method=set_method)

    for s, act, level in search:
        if level > curr_level:
            same_rank.append([])
            curr_level = level
        # Add a state node to the graph
        s_name = _add_node(dot, s, mdp)
        same_rank[-1].append(s_name)

        for a, distributions in act.items():
            for dist in distributions:
                _add_edge(dot, s_name, a, dist, mdp)

    if highlight:
        for s, act, _ in mdp.bfs(set_method=set_method):
            for node in [s] + list(
                t
                for distributions in act.values()
                for dist in distributions
                for t in dist.keys()
            ):
                if node not in _node_map:
                    _add_node(dot, node, mdp)
                dot.node(_node_map[node], style="filled")

    for nodes in same_rank:
        sg = Digraph(graph_attr={"rank": "same"})
        for node in nodes:
            sg.node(node)
        dot.subgraph(sg)


def _add_node(dot: Digraph, s: State, mdp: MDP) -> str:
    if s in _node_map:
        return _node_map[s]
    s_label = s.to_str(mdp, sep="&nbsp;", include_objects=False)
    sid = _serialize(mdp, s, prefix="node_")
    s_ctx_label = ", ".join(f"{k}={v}" for k, v in sorted(s.ctx.items()))
    label = _label_html(
        s_label,
        second_line=s_ctx_label or None,
        sid=None if mdp.is_process else sid,
    )
    dot.node(sid, label)
    _node_map[s] = sid
    return sid


def _serialize(*args, prefix: str = "") -> str:
    return prefix + str(hash(tuple(args))).replace("-", "_")


def _add_edge(
    dot: Digraph,
    s_id: str,
    action: str,
    dist: dict[State, float],
    mdp: MDP,
    second_line: str = None,
):
    # p_point is used to create a shared point for probabilistic actions
    p_point = None
    for s_prime, p in dist.items():
        cmd_text = None
        if not isinstance(s_prime, State):
            s_prime, upd = s_prime
            cmd_text = upd.text or None
        dest_id = _add_node(dot, s_prime, mdp)

        if p == 1:
            second_line = (
                "\n".join(filter(None, [second_line, cmd_text])) or None
            )
            label = _label_html(action, second_line=second_line)
            # Add a transition arrow between two states (non-deterministic)
            dot.edge(s_id, dest_id, label, minlen="2")
        else:
            if p_point is None:
                p_label = _label_html(f"{action}", second_line=second_line)
                # Create a shared point for the probabilistic outcome of action `a`
                p_point = _create_p_point(dot, s_id, action, dest_id, p_label)
            label = _label_html(p, color=graph.p_color, second_line=cmd_text)
            # Add a transition arrow between the shared point and the next state
            dot.edge(p_point, dest_id, label)


def _create_p_point(
    dot: Digraph,
    s_id: str,
    action: Action,
    dest_id: str,
    label: str,
) -> str:
    point_id = _serialize(s_id, action, dest_id, prefix="point_")
    dot.node(point_id, "", shape="point")
    dot.edge(s_id, point_id, label, arrowhead="none")
    return point_id


def _label_html(
    label: str, color: str = None, second_line: str = None, sid: str = None
) -> str:
    if isinstance(label, float):
        label = format_str(label, use_colors=False)
    if not isinstance(label, str):
        label = tuple_str(label, sep="&nbsp;")
    label = _greek_letters(label)
    label = _italicize_words(label)
    label = _subscript_numerals(label, graph.point_size * 0.5)
    if color is not None:
        label = f'<font color="{color}">{label}</font>'
    if second_line:
        label = f"{label}<br/>{_format_command(second_line)}"
    if sid is not None and graph.shorten_state_labels:
        label = f's<sub><font point-size="{round(graph.point_size * 0.5, 2)}">{_node_ids(sid)}</font></sub>'
    label = _html_padding(label, graph.label_padding)
    return f"<{label}>"


def _html_padding(label: str, padding: int):
    if padding == 0:
        return label
    return (
        f'<table cellpadding="{padding}" border="0" cellborder="0">'
        f"<tr><td>{label}</td></tr></table>"
    )


_greek_letters = [
    "alpha",
    "beta",
    "gamma",
    "delta",
    "epsilon",
    "zeta",
    "eta",
    "theta",
    "iota",
    "kappa",
    "lambda",
    "mu",
    "nu",
    "xi",
    "omicron",
    "pi",
    "rho",
    "sigma",
    "tau",
    "upsilon",
    "phi",
    "chi",
    "psi",
    "omega",
]
_re_greek = re.compile(
    r"(^|[\b_])(" + "|".join(_greek_letters) + r")([\b_]|$)",
    re.IGNORECASE,
)


def _greek_letters(label: str) -> str:
    return re.sub(_re_greek, r"\1&\2;\3", label)


_re_words = re.compile(r"(&.*?;)|([a-z]+)", re.IGNORECASE)


def _italicize_words(label: str) -> str:
    def repl(m: re.Match) -> str:
        g1, g2 = m.groups()
        return g1 if g1 is not None else f"<i>{g2}</i>"

    return re.sub(_re_words, repl, label)


def _subscript_numerals(label: str, size: int) -> str:
    return re.sub(
        r"((?!^|[.0-9])|[a-z]|<\/i>)_?([0-9]+)(?![0-9])",
        r"\1"
        f'<sub><font point-size="{round(size, 2)}">'
        r"\2"
        "</font></sub>",
        label,
    )


_re_operator = re.compile(
    r"\s*(" + "|".join(["!=", "=", ">", "<", "≔", "≤", "≥"]) + r")\s*"
)


def _format_command(label: str) -> str:
    label = label.replace("&", "&amp;")
    label = label.replace(":=", "≔")
    label = label.replace("<=", "≤")
    label = label.replace(">=", "≥")
    label = re.sub(_re_operator, r"&#8202;\1&#8202;", label)
    label = label.replace("<", "&lt;")
    label = label.replace(">", "&gt;")
    label = label.replace(" ", "&nbsp;")
    label = _italicize_words(label)
    label = _subscript_numerals(label, graph.point_size * 0.5)
    label = label.replace("\n", "<br/>")
    return label
