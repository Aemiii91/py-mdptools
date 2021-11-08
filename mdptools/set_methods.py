from typing import Generator, Iterable

from mdptools.model.transition import transition
from .types import MarkovDecisionProcess as MDP, State, Generator, Transition


def persistent_set(mdp: MDP, s: State) -> Iterable[Transition]:
    transitions = [next(iter(mdp.enabled(s)))]

    for t in transitions:
        for t_ in mdp.transitions:
            if t_ in transitions:
                continue
            if t.in_conflict(t_) or (
                t.is_parallel(t_) and t.can_be_dependent(t_)
            ):
                if not t_.is_enabled(s):
                    return transitions
                transitions.append(t_)

    return transitions
