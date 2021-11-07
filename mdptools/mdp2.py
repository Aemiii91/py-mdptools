from .utils import flatten, is_guard, is_update, partition
from .types import (
    Distribution,
    Guard,
    ProcessDescription,
    StateDescription,
    TransitionDescription,
    Union,
    Transition,
    State,
    MarkovDecisionProcess2 as MDP2,
)


DEFAULT_NAME = "M"


class MarkovDecisionProcess2:
    """The Markov decision process class (v2)"""

    def __init__(self, *processes: Union[ProcessDescription, MDP2]):
        if len(processes) == 1 and isinstance(processes[0], dict):
            self.__apply(processes[0])
        else:
            self.processes = map()

    def __repr__(self) -> str:
        return self.name

    def __apply(self, process: ProcessDescription):
        self.name = process.get("name", DEFAULT_NAME)
        self.transitions = list(
            map(self.bind_transition, process.get("transitions", []))
        )
        init = process.get("init", None)
        if init is None:
            init = self.transitions[0].pre
        self.init = State(init)

    def bind_transition(self, transition: TransitionDescription):
        action, pre, post = transition
        pre, guard = partition(is_guard, list(flatten(pre)))
        pre = State(pre)
        guard = Guard(" & ".join(guard))
        post = structure_post(post)
        return Transition(action, pre, guard, post, {self})


def structure_post(post) -> Distribution:
    def post_state(s_) -> tuple[State, str]:
        s_, update = partition(is_update, list(flatten(s_)))
        return (State(s_), ", ".join(update))

    if isinstance(post, (str, set, tuple, State)):
        return {post_state(post): 1.0}

    return {post_state(s_): p for s_, p in post.items()}
