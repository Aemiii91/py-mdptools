from mdptools.utils.utils import ordered_state_str
from ..types import MarkovDecisionProcess as MDP, State, Transition, Iterable
from ..utils import (
    highlight as _h,
    logger,
    log_info_enabled,
    ordered_state_str,
)


def overmans_algorithm(
    mdp: MDP, s: State, t: Transition = None
) -> list[Transition]:
    """Algorithm 2 from [godefroid1996]"""
    # 1. Take one transition t that is enabled in s
    if t is None or not t.is_enabled(s):
        t = mdp.enabled_take_one(s)

    # Let P = active(t)
    P = list(t.active)

    if log_info_enabled():
        logger.info(
            "[Overman's algorithm]\n  s = %s\n  t = <%s>\n  P = {%s}",
            ordered_state_str(s, mdp, ",", lambda st: _h(_h.state, st)),
            t,
            ", ".join(map(lambda p: _h(_h.fail, p.name), P)),
        )

    # 2. For all processes Pi ∈ P
    for Pi in P:
        # for all transitions t such that s(i) ∈ pre(t)
        for t1 in __trs_local_state_in_pre(s, Pi, mdp):
            for Pj in mdp.processes:
                if Pj in P:
                    continue
                if Pj in t1.active or __active_in_dependent_tr(Pj, t1, mdp):
                    if log_info_enabled():
                        logger.info(
                            "  P += %s %s",
                            _h(_h.fail, Pj.name),
                            f"[in active({t1})]"
                            if Pj in t1.active
                            else "[in active(t')]",
                        )
                    P.append(Pj)

    _P = set(P)
    # Return all transitions t such that active(t) ⊆ P and t is enabled in s
    T = list(
        filter(lambda t: t.active <= _P and t.is_enabled(s), mdp.transitions)
    )

    if log_info_enabled():
        logger.info("  T = {<%s>}", ">,\n       <".join(map(str, T)))

    return T


def __trs_local_state_in_pre(
    s: State, p: MDP, mdp: MDP
) -> Iterable[Transition]:
    """Return transitions that can be accessed by process p from its current local state s(i)"""
    s_i = s(p)
    return filter(lambda t: s_i in t.pre, mdp.transitions)


def __active_in_dependent_tr(p: MDP, t1: Transition, mdp: MDP) -> bool:
    """p ∈ active(t') for some t' such that t and t' are parallel and can-be-dependent"""
    return any(
        p in t2.active
        for t2 in mdp.transitions
        if t1.is_parallel(t2) and t1.can_be_dependent(t2)
    )
