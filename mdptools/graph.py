from .utils import re, format_str
from .types import (
    Action,
    MarkovDecisionProcess as MDP,
    Union,
    Digraph,
    Callable,
    Transition,
)
from .model import State, state


def graph(
    *processes: MDP,
    file_path: str = None,
    file_format: str = "svg",
    engine: str = "dot",
    rankdir: str = "TB",
    size: float = 8.5,
    set_method: Callable[[MDP, State], list[Transition]] = None,
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

    if len(processes) > 1:
        for pid, process in enumerate(processes):
            with dot.subgraph() as subgraph:
                __render_mdp(subgraph, process, pid, set_method)
    else:
        __render_mdp(dot, processes[0], 0, set_method)

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
    set_method: Callable[[MDP, State], list[Transition]],
):
    if m.is_process:
        __render_process(dot, m, pid)
    else:
        __render_system(dot, m, pid, set_method)


def __render_process(dot: Digraph, m: MDP, pid: int):
    # Add arrow pointing to the start state
    init = state(m.init, context={})
    init_name = f"mdp_{pid}_start"
    init_label = f"<<b>{m.name}</b>>"
    dot.node(
        init_name,
        label=init_label,
        shape="none",
        fontsize=f"{round(graph.point_size * 1.2, 2)}",
    )
    dot.edge(init_name, __pf_s(init, pid, m))

    for a, s, guard, dist in m.transitions:
        # Add a state node to the graph
        s_name = __add_node(dot, s, pid, m)
        __add_edges(dot, s_name, a, dist, pid, m, second_line=guard.text)


def __render_system(
    dot: Digraph,
    m: MDP,
    pid: int,
    set_method: Callable[[MDP, State], list[Transition]],
):
    from graphviz import Digraph

    global _node_map

    # Add arrow pointing to the start state
    init_name = f"mdp_{pid}_start"
    init_label = f"<<b>{m.name}</b>>"
    dot.node(
        init_name,
        label=init_label,
        shape="none",
        fontsize=f"{round(graph.point_size * 1.2, 2)}",
    )
    dot.edge(init_name, __pf_s(m.init, pid, m))

    same_rank = [[]]
    curr_level = 0
    _node_map = {}

    for s, act, level in m.bfs(set_method=set_method):
        if level > curr_level:
            same_rank.append([])
            curr_level = level
        # Add a state node to the graph
        s_name = __add_node(dot, s, pid, m)
        same_rank[-1].append(s_name)

        for a, dist in act.items():
            __add_edges(dot, s_name, a, dist, pid, m)

    for nodes in same_rank:
        sg = Digraph(graph_attr={"rank": "same"})
        for node in nodes:
            sg.node(node)
        dot.subgraph(sg)


_node_map: dict[State, str] = {}


def __add_node(dot: Digraph, s: State, pid: int, m: MDP) -> str:
    if s in _node_map:
        return _node_map[s]
    s_label = __ordered_state_str(s, m)
    s_name = __pf_s(s, pid, m)
    s_ctx_label = ",".join(f"{k}={v}" for k, v in s.context.items())
    dot.node(s_name, __label_html(s_label, second_line=s_ctx_label or None))
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
        update = None
        if not isinstance(s_prime, State):
            s_prime, upd = s_prime
            update = upd._repr or None
        s_prime_name = __add_node(dot, s_prime, pid, m)

        if p == 1:
            second_line = (
                ", ".join(filter(None, [second_line, update])) or None
            )
            label = __label_html(a, second_line=second_line)
            # Add a transition arrow between two states (non-deterministic)
            dot.edge(s_name, s_prime_name, label, minlen="2")
        else:
            if p_point is None:
                p_label = __label_html(f"{a}", second_line=second_line)
                # Create a shared point for the probabilistic outcome of action `a`
                p_point = __create_p_point(dot, s_name, a, p_label, pid)
            label = __label_html(p, color=graph.p_color, second_line=update)
            # Add a transition arrow between the shared point and the next state
            dot.edge(p_point, s_prime_name, label)


def __ordered_state_str(s: State, m: MDP) -> str:
    if m.is_process:
        return __str_tuple(s)
    return "_".join(ss for p in m.processes for ss in s.s if ss in p.states)


def __pf_s(s: State, pid: int, m: MDP) -> str:
    s_label = __ordered_state_str(s, m)
    return f"mdp_{pid}_state_{s_label}_ctx_{__str_context(s.context)}"


def __str_tuple(s: Union[tuple, str]) -> str:
    if isinstance(s, str):
        return s
    return "_".join(__str_tuple(sb) for sb in s)


def __str_context(ctx: dict[str, int]) -> str:
    return "_".join(f"{k}{v}" for k, v in ctx.items())


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
        label = format_str(label, colors=False)
    label = __str_tuple(label)
    label = __greek_letters(label)
    label = __italicize_words(label)
    label = __subscript_numerals(label, graph.point_size * 0.5)
    label = label.replace("_", "&nbsp;")
    if color is not None:
        label = f'<font color="{color}">{label}</font>'
    if second_line:
        second_line = __format_command(second_line)
        second_line = __italicize_words(second_line)
        label = f"{label}<br/>{second_line}"
    label = __html_padding(label, graph.label_padding)
    return f"<{label}>"


def __html_padding(label: str, padding: int):
    if padding == 0:
        return label
    return (
        f'<table cellpadding="{padding}" border="0" cellborder="0">'
        f"<tr><td>{label}</td></tr></table>"
    )


# pylint: disable=line-too-long
_re_greek = re.compile(
    r"(^|[\b_])(alpha|beta|gamma|delta|epsilon|zeta|eta|theta|iota|kappa|lambda|mu|nu|xi|omicron|pi|rho|sigma|tau|upsilon|phi|chi|psi|omegamxsm)([\b_]|$)",
    re.IGNORECASE,
)


def __greek_letters(label: str) -> str:
    return re.sub(_re_greek, r"\1&\2;\3", label)


def __italicize_words(label: str) -> str:
    def repl(m: re.Match) -> str:
        g1, g2 = m.groups()
        return g1 if g1 is not None else f"<i>{g2}</i>"

    return re.sub(r"(&.*?;)|([a-z]+)", repl, label)


def __subscript_numerals(label: str, size: int) -> str:
    return re.sub(
        r"(?!^|[.0-9])_?([0-9]+)(?![0-9])",
        f'<sub><font point-size="{round(size, 2)}">' r"\1" "</font></sub>",
        label,
    )


_re_operator = re.compile(
    r"\s*(" + "|".join([">=", "<=", "!=", "=", ">", "<", "≔"]) + r")\s*"
)


def __format_command(text: str) -> str:
    text = text.replace(":=", "≔")
    text = re.sub(_re_operator, r"&#8202;\1&#8202;", text)
    return text
