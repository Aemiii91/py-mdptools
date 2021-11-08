import itertools
import operator
from functools import reduce
from collections import Counter, defaultdict

from .state import State
from .transition import post_state, transition, Transition, apply_update
from .types import (
    MarkovDecisionProcess2 as MDP2,
    ProcessDescription,
    StateDescription,
    TransitionDescription,
    Union,
    Callable,
    Generator,
)


DEFAULT_NAME = "M"


class MarkovDecisionProcess2:
    """The Markov decision process class (v2)"""

    name: str
    init: State
    processes: list[MDP2] = []
    transitions: list[Transition]

    def __init__(
        self, *processes: Union[ProcessDescription, MDP2], name: str = None
    ):
        if len(processes) == 1 and isinstance(processes[0], dict):
            self.__apply(processes[0])
        else:
            self.processes = list(map(ensure_process, processes))
            self.init = reduce(operator.add, (p.init for p in self.processes))
            self.transitions = combine_transitions(self.processes)
            self.name = "||".join(p.name for p in self.processes)

        if name is not None:
            self.name = name

    def enabled(self, s: State = None) -> list[Transition]:
        if s is None:
            s = self.init
        return list(filter(lambda tr: tr.enabled(s), self.transitions))

    def search(
        self,
        s: State = None,
        set_method: Callable[[MDP2, State], list[Transition]] = None,
    ) -> Generator:
        if set_method is None:
            set_method = MarkovDecisionProcess2.enabled
        if s is None:
            s = self.init

        stack = [s]
        transition_map = {}

        while len(stack) > 0:
            s = stack.pop()
            if s not in transition_map:
                # Register the global state
                transition_map[s] = {}
                # Iterate transitions returned by callback
                for tr in set_method(self, s):
                    # Get the successor states for the transition
                    succ = tr.successors(s)
                    transition_map[s][tr.action] = succ
                    # Add the discovered states to the stack
                    stack += succ
                yield (s, transition_map[s])

    def __repr__(self) -> str:
        return self.name

    def __apply(self, process: ProcessDescription):
        self.name = process.get("name", DEFAULT_NAME)
        self.transitions = list(
            map(self.__bind_transition, process.get("transitions", []))
        )
        init = process.get("init", None)
        if init is None:
            init = (next(iter(self.transitions)).pre,)
        self.init = apply_update(post_state(init))

    def __bind_transition(self, tr: TransitionDescription):
        tr = iter(tr)
        action, pre, post = (next(tr, None) for _ in range(3))
        return transition(action, pre, post=post, active={self})


def ensure_process(process: Union[ProcessDescription, MDP2]) -> MDP2:
    if not isinstance(process, MarkovDecisionProcess2):
        return MarkovDecisionProcess2(process)
    return process


def combine_transitions(processes: list[MDP2]) -> list[Transition]:
    transitions = []

    # List all process transitions
    process_transitions = [
        (pid, tr) for pid, p in enumerate(processes) for tr in p.transitions
    ]
    # Count the number of processes for each action
    global_actions = Counter(
        itertools.chain.from_iterable(
            (tr.action for tr in p.transitions) for p in processes
        )
    )
    # Create a dict of actions that appear in more than one process
    synched_actions = {
        a: defaultdict(list)
        for a, count in global_actions.items()
        if count > 1
    }

    for pid, tr in process_transitions:
        if tr.action in synched_actions:
            # Collect all transitions belonging to a synched action
            synched_actions[tr.action][pid].append(tr)
        else:
            transitions.append(tr)

    # Generate all permutations of synched transitions
    transitions += [
        (t1 + t2)
        for queue in synched_actions.values()
        for t1, t2 in itertools.product(*queue.values())
    ]

    return transitions
