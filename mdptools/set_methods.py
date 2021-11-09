from .types import MarkovDecisionProcess as MDP, State, Transition


def persistent_set(mdp: MDP, s: State) -> list[Transition]:
    # 1. Take one transition t that is enabled in s. Let T = {t}.
    T = [mdp.enabled_take_one(s)]

    # 2. For all transitions t in T, add to T all transitions t' such that
    for t in T:
        if t is None:
            return []
        for t_ in mdp.transitions:
            if t_ in T:
                continue
            # t and t' are in conflict; or
            if t.in_conflict(t_) or (
                # t and t' are parallel and can-be-dependent
                t.is_parallel(t_)
                and t.can_be_dependent(t_)
            ):
                # If a disabled transition is introduced,
                if not t_.is_enabled(s):
                    # return all enabled transitions
                    return mdp.enabled(s)
                T.append(t_)

    return T
