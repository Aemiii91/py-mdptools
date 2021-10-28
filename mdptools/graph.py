import re
from .utils.types import MarkovDecisionProcess, Union, Digraph


def graph(
    m: MarkovDecisionProcess,
    file_path: str,
    file_format: str = "svg",
    engine: str = "dot",
    rankdir: str = "TB",
    size: float = 8.5,
) -> Digraph:
    """Renders the graph of a given MDP and saves it to `file_path`."""
    # pylint: disable=redefined-outer-name
    from graphviz import Digraph

    set_fontsize = {"fontsize": f"{graph.point_size}"}
    dot = Digraph(
        filename=file_path,
        format=file_format,
        engine=engine,
        node_attr=set_fontsize,
        edge_attr=set_fontsize,
    )
    dot.attr(size=f"{size}", rankdir=rankdir, ranksep="0.25", margin="0.1")

    if isinstance(m, list):
        for idx, M in enumerate(m):
            with dot.subgraph() as subgraph:
                __render_mdp(subgraph, M, idx)
    else:
        __render_mdp(dot, m, m.name)

    dot.render()
    return dot


graph.re_sep = "|"
graph.point_size = 18
graph.p_color = None
graph.label_padding = 2


def __render_mdp(
    dot: Digraph, m: MarkovDecisionProcess, name: Union[str, int]
):
    # Add arrow pointing to the start state
    init_name = f"mdp_{name}_start"
    init_label = f"<<b>{m.name}</b>>"
    dot.node(
        init_name,
        label=init_label,
        shape="none",
        fontsize=f"{graph.point_size * 1.2}",
    )
    dot.edge(init_name, __pf_s(m.s_init))

    for s, act in m.transition_map.items():
        # Add a state node to the graph
        dot.node(__pf_s(s), __label_html(s))
        for a, dist in act.items():
            # p_point is used to create a common point for probabilistic actions
            p_point = None
            for s_prime, p in dist.items():
                if p == 1:
                    # Add a transition arrow between two states (non-deterministic)
                    dot.edge(
                        __pf_s(s), __pf_s(s_prime), __label_html(a), minlen="2"
                    )
                else:
                    if p_point is None:
                        # Create a common point for the probabilistic outcome of action `a`
                        p_point = __create_p_point(dot, s, a)
                    # Add a transition arrow between the common point and the next state
                    dot.edge(
                        p_point,
                        __pf_s(s_prime),
                        __label_html(p, color=graph.p_color),
                    )


def __pf_s(s: str) -> str:
    return f"state_{s}"


def __create_p_point(dot: Digraph, s: str, a: str) -> str:
    p_point = f"p_point_{s}_{a}"
    dot.node(p_point, "", shape="point")
    dot.edge(__pf_s(s), p_point, __label_html(a), arrowhead="none")
    return p_point


def __label_html(label: str, color: str = None) -> str:
    if isinstance(label, float):
        label = __float_str(label)
    label = __subscript_numerals(label, graph.point_size * 0.5)
    label = __greek_letters(label)
    label = __remove_separators(label, graph.re_sep)
    if color is not None:
        label = f'<font color="{color}">{label}</font>'
    label = __html_padding(label, graph.label_padding)
    return f"<<i>{label}</i>>"


def __html_padding(label: str, padding: int):
    if padding == 0:
        return label
    return (
        f'<table cellpadding="{padding}" border="0" cellborder="0">'
        f"<tr><td>{label}</td></tr></table>"
    )


def __float_str(n: float) -> str:
    return re.sub(r"^0+(\.[0-9]+)$", r"\1", f"{n}")


# pylint: disable=line-too-long
_re_greek = r"\b(alpha|beta|gamma|delta|epsilon|zeta|eta|theta|iota|kappa|lambda|mu|nu|xi|omicron|pi|rho|sigma|tau|upsilon|phi|chi|psi|omega)(?![a-z])"


def __greek_letters(label: str) -> str:
    return re.sub(_re_greek, r"&\1;", label)


def __subscript_numerals(label: str, size: int) -> str:
    return re.sub(
        r"\B_?([0-9]+)",
        f'<sub><font point-size="{size}">' r"\1" "</font></sub>",
        label,
    )


def __remove_separators(label: str, sep: str) -> str:
    return label.replace(sep, "&#8201;")