from ..types import MarkovDecisionProcess as MDP, State, Transition


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
                # If a disabled transition is introduced,
                if not t2.is_enabled(s):
                    # return all enabled transitions
                    return mdp.enabled(s)
                T.append(t2)

    return T
