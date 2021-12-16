from ..types import (
    MarkovDecisionProcess as MDP,
    SetMethod,
    State,
    Transition,
    TransitionDescription,
    Union,
    Callable,
)


def init_transition_set(
    mdp: MDP, s: State, bias: list[Transition]
) -> list[Transition]:
    first_enabled = mdp.enabled_take_one(s)

    if not bias:
        bias = mdp.goal_actions

    if not bias:
        if not first_enabled:
            return []
        bias = [first_enabled]

    return bias


def transition_bias(
    set_method: Callable[[MDP, State, set[Transition]], list[Transition]],
    td: Union[str, Transition, TransitionDescription],
) -> SetMethod:
    """Give a set method a transition bias."""

    def choose_transition(mdp: MDP, s: State) -> Transition:
        return next(
            filter(
                lambda t: t.action == td if isinstance(td, str) else t == td,
                mdp.enabled(s),
            ),
            None,
        )

    def algo(mdp: MDP, s: State) -> list[Transition]:
        return set_method(mdp, s, {choose_transition(mdp, s)})

    algo.__name__ = set_method.__name__
    return algo
