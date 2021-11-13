from ..types import (
    MarkovDecisionProcess as MDP,
    SetMethod,
    State,
    Transition,
    TransitionDescription,
    Union,
    Callable,
)


def transition_bias(
    set_method: Callable[[MDP, State, Transition], list[Transition]],
    td: Union[str, Transition, TransitionDescription],
) -> SetMethod:
    def choose_transition(mdp: MDP, s: State) -> Transition:
        return next(
            filter(
                lambda t: t.action == td if isinstance(td, str) else t == td,
                mdp.enabled(s),
            ),
            None,
        )

    def algo(mdp: MDP, s: State) -> list[Transition]:
        return set_method(mdp, s, choose_transition(mdp, s))

    algo.__name__ = set_method.__name__
    return algo
