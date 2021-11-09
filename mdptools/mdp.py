from .types import (
    dataclass,
    Digraph,
    MarkovDecisionProcess as MDP,
    RenameFunction,
    StateDescription,
    TransitionDescription,
    Union,
    Callable,
    Generator,
    defaultdict,
    Iterable,
)
from .utils import (
    itertools,
    operator,
    reduce,
    Counter,
    highlight as _h,
    rename_map,
    to_prism,
    SimpleQueue,
)
from .model import (
    Transition,
    transition,
    post_state,
    apply_update,
    State,
    state,
)
from .graph import graph


DEFAULT_NAME = "M"


class MarkovDecisionProcess:
    """The Markov decision process class (v2)"""

    name: str = DEFAULT_NAME
    init: State = None
    processes: list[MDP] = []
    transitions: list[Transition] = []

    def __init__(
        self,
        *args: Union[list[TransitionDescription], MDP],
        init: StateDescription = None,
        processes: dict[str, tuple[str]] = None,
        name: str = None,
    ):
        self._states = None
        self._actions = None
        if len(args) == 1:
            transitions = next(iter(args), [])
            if processes is None:
                self.__init_process(transitions, init)
            else:
                processes = [
                    _MDPShell(name, frozenset(states), state(states[0]))
                    for name, states in processes.items()
                ]
                self.__init_system(processes, init, transitions)
        else:
            self.__init_system(args, init)

        if name is not None:
            self.name = name

    def __init_process(
        self, transitions: list[TransitionDescription], init: StateDescription
    ):
        if isinstance(transitions, MarkovDecisionProcess):
            if init is None:
                init = transitions.init
            self.name = transitions.name
            transitions = transitions.transitions

        self.processes = [self]
        self.transitions = list(map(self.__bind_transition, transitions))

        if init is None and self.transitions:
            init = next(iter(self.transitions)).pre
        if init is not None:
            self.init = apply_update(post_state(init))

    def __init_system(
        self,
        processes: Iterable[MDP],
        init: StateDescription,
        transitions: list[TransitionDescription] = None,
    ):
        self.processes = list(processes)

        if transitions is None:
            self.transitions = combine_transitions(self.processes)
        else:
            self.transitions = list(map(self.__bind_transition, transitions))

        self.name = "||".join(p.name for p in self.processes)

        if init is None:
            self.init = reduce(operator.add, (p.init for p in self.processes))
        else:
            self.init = apply_update(post_state(init))

    def enabled(self, s: State = None) -> list[Transition]:
        if s is None:
            s = self.init
        return list(filter(lambda tr: tr.is_enabled(s), self.transitions))

    def enabled_take_one(self, s: State = None) -> Transition:
        if s is None:
            s = self.init
        return next(
            iter(filter(lambda tr: tr.is_enabled(s), self.transitions)), None
        )

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
        if not self.is_process:
            raise Exception("Can't remake composed MDP")
        if name is None:
            name = self.name
        return MarkovDecisionProcess(
            [tr.rename(states, actions) for tr in self.transitions],
            name=name,
            init=self.init.rename(states),
        )

    def to_graph(self, file_path: str = None, **kw) -> Digraph:
        return graph(self, file_path=file_path, **kw)

    def to_prism(self, file_path: str = None) -> str:
        return to_prism(self, file_path)

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
    def is_process(self) -> bool:
        return len(self.processes) == 1

    def __eq__(self, other: MDP) -> bool:
        init = self.init == other.init
        trs = all(tr in other.transitions for tr in self.transitions)
        return init and trs

    def __hash__(self) -> int:
        return id(self)

    def __contains__(self, key: str) -> bool:
        return key in self.states

    def __repr__(self) -> str:
        return f"MDP({self.name})"

    def __str__(self) -> str:
        buffer = f"mdp {_h[_h.variable, self.name]}:\n"
        buffer += f"  init := {self.init}\n"
        buffer += "\n".join(f"  {tr}" for tr in self.transitions) + "\n"
        return buffer

    def __bind_transition(self, tr: TransitionDescription):
        if not isinstance(tr, Transition):
            it = iter(tr)
            action, pre, post = (next(it, None) for _ in range(3))
            tr = transition(action, pre, post=post)

        if self.is_process:
            process = {self}
        else:
            process = set(
                p for p in self.processes for ss in tr.pre.s if ss in p
            )

        return tr.bind(process)

    def __set_states_and_actions(self):
        states, actions = set(), set()
        for tr in self.transitions:
            states = states.union(tr.pre.s)
            for (s_, _), _ in tr.post.items():
                states = states.union(s_.s)
            actions = actions.union({tr.action})
        self._states = frozenset(states)
        self._actions = frozenset(actions)


@dataclass(eq=True, frozen=True)
class _MDPShell:
    name: str
    states: frozenset[str]
    init: State

    def __contains__(self, key: str) -> bool:
        return key in self.states


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
        if count > 1 and not a.startswith("tau")
    }

    for pid, tr in process_transitions:
        if tr.action in synched_actions:
            # Collect all transitions belonging to a synched action
            synched_actions[tr.action][pid].append(tr)
        else:
            transitions.append(tr)

    # Generate all permutations of synched transitions
    transitions += [
        reduce(operator.add, trs)
        for queue in synched_actions.values()
        for trs in itertools.product(*queue.values())
    ]

    return transitions
