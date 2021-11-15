from mdptools.mdp import MarkovDecisionProcess
from ..types import MarkovDecisionProcess as MDP, State, Transition
from ..utils import (
    highlight as _h,
    logger,
    log_info_enabled,
    ordered_state_str,
)


def conflicting_transitions(
    mdp: MDP, s: State, t: Transition = None
) -> list[Transition]:
    """Algorithm 1 from [godefroid1996]"""
    # 1. Take one transition t that is enabled in s.
    if t is None or not t.is_enabled(s):
        t = mdp.enabled_take_one(s)
    if t is None:
        return []

    # Let T = {t}.
    T = [t]

    _log_begin(mdp, s, t)

    # 2. For all transitions t in T
    for t1 in T:
        # add to T all transitions t' such that
        for t2 in mdp.transitions:
            if t2 in T:
                continue
            # t and t' are in conflict; or
            if t1.in_conflict(t2) or (
                # t and t' are parallel and can-be-dependent
                t1.is_parallel(t2)
                and t1.can_be_dependent(t2)
            ):
                _log_append(t1, t2, s)
                # If a disabled transition is introduced,
                if not t2.is_enabled(s):
                    # return all enabled transitions
                    T = mdp.enabled(s)
                    break
                T.append(t2)

    _log_end(T)

    return T


def _log_begin(mdp: MDP, s: State, t: Transition):
    if log_info_enabled():
        logger.info(
            "%s %s\n  s := {%s}\n  T := {<%s>}",
            _h.comment("begin"),
            _h.function("conflicting_transitions"),
            ordered_state_str(s, mdp, ",", lambda st: _h.state(st)),
            t,
        )


def _log_append(t1: Transition, t2: Transition, s: State):
    if log_info_enabled():
        logger.info(
            "    + <%s> [%s%s]",
            t2,
            _h.error(
                "conflict"
                if t1.in_conflict(t2)
                else "parallel + can-be-dependent",
            ),
            "" if t2.is_enabled(s) else ", " + _h.fail("disabled"),
        )


def _log_end(T: list[Transition]):
    if log_info_enabled():
        logger.info(
            "\n  %s {<%s>}\n%s",
            _h.variable("return"),
            ">,\n          <".join(map(str, T)),
            _h.comment("end"),
        )
