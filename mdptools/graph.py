from .utils import re, format_str
from .types import Action, MarkovDecisionProcess as MDP, Union, Digraph
from .model import State, state


def graph(
    *processes: MDP,
    file_path: str = None,
    file_format: str = "svg",
    engine: str = "dot",
    rankdir: str = "TB",
    size: float = 8.5,
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
                __render_mdp(subgraph, process, pid)
    else:
        __render_mdp(dot, processes[0], 0)

    if file_path is not None:
        dot.render()

    return dot


graph.re_sep = "_"
graph.point_size = 18
graph.p_color = None
graph.label_padding = 2


def __render_mdp(dot: Digraph, m: MDP, pid: int):
    if m.is_single:
        __render_process(dot, m, pid)
    else:
        __render_system(dot, m, pid)


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
        s_label = __ordered_state_str(s, m)
        s_name = __pf_s(s, pid, m)
        dot.node(s_name, __label_html(s_label))
        __add_edges(dot, s_name, a, dist, pid, m, second_line=f"{guard}")


def __render_system(dot: Digraph, m: MDP, pid: int):
    from graphviz import Digraph

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

    for s, act, level in m.bfs():
        if level > curr_level:
            same_rank.append([])
            curr_level = level
        # Add a state node to the graph
        s_label = __ordered_state_str(s, m)
        s_name = __pf_s(s, pid, m)
        same_rank[-1].append(s_name)
        s_ctx_label = ",".join(f"{k}={v}" for k, v in s.context.items())

        dot.node(
            s_name, __label_html(s_label, second_line=s_ctx_label or None)
        )

        for a, dist in act.items():
            __add_edges(dot, s_name, a, dist, pid, m)

    for nodes in same_rank:
        sg = Digraph(graph_attr={"rank": "same"})
        for node in nodes:
            sg.node(node)
        dot.subgraph(sg)


def __ordered_state_str(s: State, m: MDP) -> str:
    if m.is_single:
        return __str_tuple(s)
    return "_".join(ss for p in m.processes for ss in s.s if ss in p.states)


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
            update = f"{upd}" or None
        s_prime_name = __pf_s(s_prime, pid, m)

        if p == 1:
            second_line = (
                ", ".join(filter(None, [second_line, update])) or None
            )
            # Add a transition arrow between two states (non-deterministic)
            dot.edge(
                s_name,
                s_prime_name,
                __label_html(a, second_line=second_line),
                minlen="2",
            )
        else:
            if p_point is None:
                p_label = __label_html(f"{a}", second_line=second_line)
                # Create a shared point for the probabilistic outcome of action `a`
                p_point = __create_p_point(dot, s_name, a, p_label, pid)
            # Add a transition arrow between the shared point and the next state
            dot.edge(
                p_point,
                s_prime_name,
                __label_html(p, color=graph.p_color, second_line=update),
            )


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
    label = __subscript_numerals(label, graph.point_size * 0.5)
    label = __greek_letters(label)
    label = __remove_separators(label, graph.re_sep)
    if color is not None:
        label = f'<font color="{color}">{label}</font>'
    if second_line is not None:
        second_line = second_line.replace(":=", "≔")
        label = f"{label}<br/>{second_line}"
    label = __html_padding(label, graph.label_padding)
    return f"<<i>{label}</i>>"


def __html_padding(label: str, padding: int):
    if padding == 0:
        return label
    return (
        f'<table cellpadding="{padding}" border="0" cellborder="0">'
        f"<tr><td>{label}</td></tr></table>"
    )


# pylint: disable=line-too-long
_re_greek = r"\b(alpha|beta|gamma|delta|epsilon|zeta|eta|theta|iota|kappa|lambda|mu|nu|xi|omicron|pi|rho|sigma|tau|upsilon|phi|chi|psi|omega)(?![a-z])"


def __greek_letters(label: str) -> str:
    return re.sub(_re_greek, r"&\1;", label)


def __subscript_numerals(label: str, size: int) -> str:
    return re.sub(
        r"([a-z])_?([0-9]+)(?![0-9])",
        r"\1"
        f'<sub><font point-size="{round(size, 2)}">'
        r"\2"
        "</font></sub>",
        label,
    )


def __remove_separators(label: str, sep: str) -> str:
    return label.replace(sep, "&#8201;")
