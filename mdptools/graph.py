from mdptools.utils.utils import ordered_state_str
from .types import (
    Action,
    MarkovDecisionProcess as MDP,
    SetMethod,
    Union,
    Digraph,
)
from .utils import re, format_str, ordered_state_str, tuple_str
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

    for pid, process in enumerate(processes):
        with dot.subgraph() as subgraph:
            __render_mdp(subgraph, process, pid, set_method, highlight)

    if file_path is not None:
        dot.render()

    return dot


graph.point_size = 18
graph.p_color = None
graph.label_padding = 2


def __render_mdp(
    dot: Digraph,
    m: MDP,
    pid: int,
    set_method: SetMethod,
    highlight: bool,
):
    global _node_map
    _node_map = {}

    # Add arrow pointing to the start state
    init = m.init
    if m.is_process:
        init = state(init, ctx={})
    init_name = f"mdp_{pid}_start"
    init_label = f"<<b>{m.name}</b>>"
    dot.node(
        init_name,
        label=init_label,
        shape="none",
        fontsize=f"{round(graph.point_size * 1.2, 2)}",
    )
    dot.edge(init_name, __pf_s(init, pid, m))

    if m.is_process:
        __render_process(dot, m, pid)
    else:
        __render_system(dot, m, pid, set_method, highlight)


def __render_process(dot: Digraph, m: MDP, pid: int):
    for a, s, guard, dist in m.transitions:
        # Add a state node to the graph
        s_name = __add_node(dot, s, pid, m)
        __add_edges(dot, s_name, a, dist, pid, m, second_line=guard.text)


def __render_system(
    dot: Digraph, m: MDP, pid: int, set_method: SetMethod, highlight: bool
):
    from graphviz import Digraph

    same_rank = [[]]
    curr_level = 0

    if highlight:
        search = m.bfs(set_method=False, logging_enabled=False)
    else:
        search = m.bfs(set_method=set_method)

    for s, act, level in search:
        if level > curr_level:
            same_rank.append([])
            curr_level = level
        # Add a state node to the graph
        s_name = __add_node(dot, s, pid, m)
        same_rank[-1].append(s_name)

        for a, dist in act.items():
            __add_edges(dot, s_name, a, dist, pid, m)

    if highlight:
        for s, act, level in m.bfs(set_method=set_method):
            if s in _node_map:
                dot.node(_node_map[s], style="filled")

    for nodes in same_rank:
        sg = Digraph(graph_attr={"rank": "same"})
        for node in nodes:
            sg.node(node)
        dot.subgraph(sg)


_node_map: dict[State, str] = {}


def __add_node(dot: Digraph, s: State, pid: int, m: MDP) -> str:
    if s in _node_map:
        return _node_map[s]
    s_label = ordered_state_str(s, m)
    s_name = __pf_s(s, pid, m)
    s_ctx_label = ",&nbsp;".join(f"{k}={v}" for k, v in s.ctx.items())
    label = __label_html(s_label, second_line=s_ctx_label or None)
    dot.node(s_name, label)
    _node_map[s] = s_name
    return s_name


def __add_edges(
    dot: Digraph,
    s_name: str,
    a: str,
    dist: dict[State, float],
    pid: int,
    m: MDP,
    second_line: str = None,
):
    # p_point is used to create a shared point for probabilistic actions
    p_point = None
    for s_prime, p in dist.items():
        cmd_text = None
        if not isinstance(s_prime, State):
            s_prime, upd = s_prime
            cmd_text = upd.text or None
        s_prime_name = __add_node(dot, s_prime, pid, m)

        if p == 1:
            second_line = (
                ",&nbsp;".join(filter(None, [second_line, cmd_text])) or None
            )
            label = __label_html(a, second_line=second_line)
            # Add a transition arrow between two states (non-deterministic)
            dot.edge(s_name, s_prime_name, label, minlen="2")
        else:
            if p_point is None:
                p_label = __label_html(f"{a}", second_line=second_line)
                # Create a shared point for the probabilistic outcome of action `a`
                p_point = __create_p_point(dot, s_name, a, p_label, pid)
            label = __label_html(p, color=graph.p_color, second_line=cmd_text)
            # Add a transition arrow between the shared point and the next state
            dot.edge(p_point, s_prime_name, label)


def __pf_s(s: State, pid: int, m: MDP) -> str:
    s_label = ordered_state_str(s, m)
    return f"mdp_{pid}_state_{s_label}{__str_context(s.ctx)}"


def __str_context(ctx: dict[str, int]) -> str:
    text = "_".join(f"{k}_{v}" for k, v in ctx.items())
    return f"_ctx_{text}" if text else ""


def __create_p_point(
    dot: Digraph,
    s_name: str,
    a: Action,
    label: str,
    pid: int,
) -> str:
    p_point = f"mdp_{pid}_p_point_{s_name}_{a}"
    dot.node(p_point, "", shape="point")
    dot.edge(s_name, p_point, label, arrowhead="none")
    return p_point


def __label_html(
    label: str, color: str = None, second_line: str = None
) -> str:
    if isinstance(label, float):
        label = format_str(label, use_colors=False)
    label = tuple_str(label)
    label = __greek_letters(label)
    label = __italicize_words(label)
    label = __subscript_numerals(label, graph.point_size * 0.5)
    label = label.replace("_", "&nbsp;")
    if color is not None:
        label = f'<font color="{color}">{label}</font>'
    if second_line:
        label = f"{label}<br/>{__format_command(second_line)}"
    label = __html_padding(label, graph.label_padding)
    return f"<{label}>"


def __html_padding(label: str, padding: int):
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


def __greek_letters(label: str) -> str:
    return re.sub(_re_greek, r"\1&\2;\3", label)


_re_words = re.compile(r"(&.*?;)|([a-z]+)", re.IGNORECASE)


def __italicize_words(label: str) -> str:
    def repl(m: re.Match) -> str:
        g1, g2 = m.groups()
        return g1 if g1 is not None else f"<i>{g2}</i>"

    return re.sub(_re_words, repl, label)


def __subscript_numerals(label: str, size: int) -> str:
    return re.sub(
        r"((?!^|[.0-9])|[a-z]|<\/i>)_?([0-9]+)(?![0-9])",
        r"\1"
        f'<sub><font point-size="{round(size, 2)}">'
        r"\2"
        "</font></sub>",
        label,
    )


_re_operator = re.compile(
    r"\s*(" + "|".join([">=", "<=", "!=", "=", ">", "<", "≔"]) + r")\s*"
)


def __format_command(text: str) -> str:
    text = text.replace(":=", "≔")
    text = re.sub(_re_operator, r"&#8202;\1&#8202;", text)
    text = __italicize_words(text)
    text = __subscript_numerals(text, graph.point_size * 0.5)
    return text
