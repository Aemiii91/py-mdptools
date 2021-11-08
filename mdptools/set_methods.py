from .types import MarkovDecisionProcess as MDP, State, Generator


def persistent_set(mdp: MDP, s: State) -> Generator:
    transitions = [mdp.enabled_take_one(s)]

    for t in transitions:
        if t is None:
            return
        yield t
        for t_ in mdp.transitions:
            if t_ in transitions:
                continue
            if t.in_conflict(t_) or (
                t.is_parallel(t_) and t.can_be_dependent(t_)
            ):
                if not t_.is_enabled(s):
                    return
                transitions.append(t_)
