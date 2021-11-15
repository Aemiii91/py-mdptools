from ..types import MarkovDecisionProcess as MDP, State, Transition, Iterable
from ..utils import (
    highlight as _h,
    logger,
    log_info_enabled,
)


def overmans_algorithm(
    mdp: MDP, s: State, t: Transition = None
) -> list[Transition]:
    """Algorithm 2 from [godefroid1996]"""
    # 1. Take one transition t that is enabled in s
    if t is None or not t.is_enabled(s):
        t = mdp.enabled_take_one(s)
    if t is None:
        return []

    # Let P = active(t)
    P = list(t.active)

    _log_begin(mdp, s, t, P)

    # 2. For all processes Pi ∈ P
    for Pi in P:
        # for all transitions t such that s(i) ∈ pre(t)
        for t1 in _trs_local_state_in_pre(s, Pi, mdp):
            for Pj in mdp.processes:
                if Pj in P:
                    continue
                if Pj in t1.active or _active_in_dependent_tr(Pj, t1, mdp):
                    P.append(Pj)
                    _log_append(Pj, t1)

    _P = set(P)
    # Return all transitions t such that active(t) ⊆ P and t is enabled in s
    T = list(
        filter(lambda t: t.active <= _P and t.is_enabled(s), mdp.transitions)
    )

    _log_end(T)

    return T


def _trs_local_state_in_pre(
    s: State, p: MDP, mdp: MDP
) -> Iterable[Transition]:
    """Return transitions that can be accessed by process p from its current local state s(i)"""
    s_i = s(p)
    return filter(lambda t: s_i in t.pre, mdp.transitions)


def _active_in_dependent_tr(p: MDP, t1: Transition, mdp: MDP) -> bool:
    """p ∈ active(t') for some t' such that t and t' are parallel and can-be-dependent"""
    return any(
        p in t2.active
        for t2 in mdp.transitions
        if t1.is_parallel(t2) and t1.can_be_dependent(t2)
    )


def _log_begin(mdp: MDP, s: State, t: Transition, P: list[MDP]):
    if log_info_enabled():
        logger.info(
            "%s %s\n  s := {%s}\n  t := <%s>\n  P := {%s}",
            _h.comment("begin"),
            _h.function("overmans_algorithm"),
            s.to_str(mdp, colors=True, wrap=True),
            t,
            ", ".join(map(lambda p: _h.fail(p.name), P)),
        )


def _log_append(Pj: MDP, t1: Transition):
    if log_info_enabled():
        logger.info(
            "  P += %s [%s]",
            _h.fail(Pj.name),
            _h.error(
                f"in active({t1})" if Pj in t1.active else "in active(t')",
            ),
        )


def _log_end(T: list[Transition]):
    if log_info_enabled():
        logger.info(
            "\n  %s {<%s>}\n%s",
            _h.variable("return"),
            ">,\n          <".join(map(str, T)),
            _h.comment("end"),
        )
