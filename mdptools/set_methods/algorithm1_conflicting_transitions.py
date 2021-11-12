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

    # Let T = {t}.
    T = [t]

    if log_info_enabled():
        logger.info(
            "[Conflicting transitions]\n  s = %s\n  T = {<%s>}",
            ordered_state_str(s, mdp, ",", lambda st: _h(_h.state, st)),
            t,
        )

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
                if log_info_enabled():
                    logger.info(
                        "    + <%s> [%s]",
                        t2,
                        _h(
                            _h.fail,
                            "conflict"
                            if t1.in_conflict(t2)
                            else "parallel + can-be-dependent",
                        ),
                    )
                # If a disabled transition is introduced,
                if not t2.is_enabled(s):
                    en = mdp.enabled(s)
                    if log_info_enabled():
                        logger.info(
                            "    ! [%s] %s\n  return {<%s>}",
                            _h(_h.fail, "transition disabled"),
                            _h(_h.comment, "// return enabled(s)"),
                            ">,\n          <".join(map(str, en)),
                        )
                    # return all enabled transitions
                    return en
                T.append(t2)

    if log_info_enabled():
        logger.info("  return {<%s>}", ">,\n          <".join(map(str, T)))

    return T
