from ..types import MarkovDecisionProcess as MDP, State, Transition
from ..utils import (
    highlight as _h,
    logger,
    log_info_enabled,
)
from .set_utils import init_transition_set


def conflicting_transitions(
    mdp: MDP, s: State, bias: list[Transition] = None
) -> list[Transition]:
    """Algorithm 1 from [godefroid1996]"""
    # Let T = {t}.
    T: list[Transition] = list(
        filter(
            lambda t: t.is_enabled(s),
            init_transition_set(mdp, s, bias),
        )
    )

    _log_begin(mdp, s, T)

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


def _log_begin(mdp: MDP, s: State, T: list[Transition]):
    if log_info_enabled():
        logger.info(
            "%s %s\n  s := {%s}\n  T := {<%s>}",
            _h.comment("begin"),
            _h.function("conflicting_transitions"),
            s.to_str(mdp, colors=True, wrap=True),
            ">,\n          <".join(map(str, T)),
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
