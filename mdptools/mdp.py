from mdptools.utils.utils import rename_map
from .types import (
    MarkovDecisionProcess as MDP,
    RenameFunction,
    State,
    StateDescription,
    TransitionDescription,
    Union,
    Callable,
    Generator,
    defaultdict,
)
from .utils import (
    itertools,
    operator,
    reduce,
    Counter,
    highlight as _h,
)
from .model.transition import Transition, transition, post_state, apply_update


DEFAULT_NAME = "M"


class MarkovDecisionProcess:
    """The Markov decision process class (v2)"""

    name: str = DEFAULT_NAME
    init: State = None
    processes: list[MDP] = []
    transitions: list[Transition]

    def __init__(
        self,
        *processes: Union[list[TransitionDescription], MDP],
        init: StateDescription = None,
        name: str = None,
    ):
        self._states = None
        self._actions = None
        if len(processes) == 1 and isinstance(processes[0], list):
            self.transitions = list(map(self.__bind_transition, processes[0]))
            if init is None:
                init = next(iter(self.transitions)).pre
            self.init = apply_update(post_state(init))
        else:
            self.processes = list(processes)
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
        set_method: Callable[[MDP, State], list[Transition]] = None,
    ) -> Generator:
        if set_method is None:
            set_method = MarkovDecisionProcess.enabled
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
                    stack += list(succ.keys())
                yield (s, transition_map[s])

    def bfs(
        self,
        s: State = None,
        set_method: Callable[[MDP, State], list[Transition]] = None,
    ) -> Generator:
        from queue import SimpleQueue

        if set_method is None:
            set_method = MarkovDecisionProcess.enabled
        if s is None:
            s = self.init

        queue = SimpleQueue()
        transition_map = {}

        queue.put((s, 0))

        while not queue.empty():
            s, level = queue.get()
            if s not in transition_map:
                # Register the global state
                transition_map[s] = {}
                # Iterate transitions returned by callback
                for tr in set_method(self, s):
                    # Get the successor states for the transition
                    successors = tr.successors(s)
                    transition_map[s][tr.action] = successors
                    # Add the discovered states to the stack
                    for succ in successors.keys():
                        queue.put((succ, level + 1))
                yield (s, transition_map[s], level)

    def remake(
        self,
        state_fn: RenameFunction = None,
        action_fn: RenameFunction = None,
        name: str = None,
    ) -> "MDP":
        states, actions = (
            rename_map(self.states, state_fn),
            rename_map(self.actions, action_fn),
        )
        if not self.is_single:
            raise Exception("Can't remake composed MDP")
        if name is None:
            name = self.name
        return MarkovDecisionProcess(
            [tr.rename(states, actions) for tr in self.transitions],
            name=name,
            init=self.init.rename(states),
        )

    @property
    def states(self) -> frozenset[str]:
        if not self._states:
            self.__set_states_and_actions()
        return self._states

    @property
    def actions(self) -> frozenset[str]:
        if not self._actions:
            self.__set_states_and_actions()
        return self._actions

    @property
    def is_single(self) -> bool:
        return len(self.processes) == 0

    def __repr__(self) -> str:
        return f"MDP({self.name})"

    def __str__(self) -> str:
        buffer = f"mdp {_h[_h.variable, self.name]}:\n"
        buffer += f"  init := {self.init}\n"
        buffer += "\n".join(f"  {tr}" for tr in self.transitions) + "\n"
        return buffer

    def __bind_transition(self, tr: TransitionDescription):
        if isinstance(tr, Transition):
            return tr.bind(self)
        it = iter(tr)
        action, pre, post = (next(it, None) for _ in range(3))
        return transition(action, pre, post=post, active={self})

    def __set_states_and_actions(self):
        states, actions = set(), set()
        for tr in self.transitions:
            states = states.union(tr.pre.s)
            for (s_, _), _ in tr.post.items():
                states = states.union(s_.s)
            actions = actions.union(set(tr.action))
        self._states = frozenset(states)
        self._actions = frozenset(actions)


def combine_transitions(processes: list[MDP]) -> list[Transition]:
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
