from .types import (
    SetMethod,
    dataclass,
    Digraph,
    MarkovDecisionProcess as MDP,
    RenameFunction,
    StateDescription,
    TransitionDescription,
    Union,
    Generator,
    Iterable,
    Iterator,
)
from .utils import (
    operator,
    reduce,
    highlight as _h,
    rename_map,
    to_prism,
)
from .model import (
    Transition,
    transition,
    compose_transitions,
    State,
    state,
    state_apply,
)
from .search import search, bfs
from .graph import graph
from .validate import validate


DEFAULT_NAME = "M"


class MarkovDecisionProcess:
    """The Markov decision process class (v2)"""

    name: str = DEFAULT_NAME
    init: State = None
    processes: list[MDP] = []
    transitions: list[Transition] = []
    set_method: SetMethod = None

    def __init__(
        self,
        *args: Union[list[TransitionDescription], MDP],
        init: StateDescription = None,
        processes: dict[str, tuple[str]] = None,
        name: str = None,
        set_method: SetMethod = None,
    ):
        self._states = None
        self._actions = None

        if len(args) == 1:
            # If only 1 argument is given, it must be a TransitionDescription
            transitions = next(iter(args), [])
            # If no processes are supplied, must be a process
            if processes is None:
                self.__init_process(transitions, init)
            else:
                # Create "hollow" MDP for each process
                processes = [
                    _MDP(name, frozenset(states), state(states[0]))
                    for name, states in processes.items()
                ]
                self.__init_system(processes, init, transitions)
        else:
            self.__init_system(args, init)

        if name is not None:
            self.name = name
        if set_method is not None:
            self.set_method = set_method

    def __init_process(
        self, transitions: list[TransitionDescription], init: StateDescription
    ):
        if isinstance(transitions, MarkovDecisionProcess):
            raise ValueError

        if init is None:
            # Set initial state to be the first transition's preset
            _, init, _ = next(iter(transitions))

        self.processes = [self]
        self.transitions = list(map(self.__bind_transition, transitions))

        if init is not None:
            self.init = state_apply(init)

    def __init_system(
        self,
        processes: Iterable[MDP],
        init: StateDescription,
        transitions: list[TransitionDescription] = None,
    ):
        self.processes = list(processes)

        if transitions is None:
            self.transitions = compose_transitions(self.processes)
        else:
            self.transitions = list(map(self.__bind_transition, transitions))

        self.name = "||".join(p.name for p in self.processes)

        if init is None:
            self.init = reduce(operator.add, (p.init for p in self.processes))
        else:
            self.init = state_apply(init)

    def enabled(self, s: State = None) -> list[Transition]:
        """Returns a list of transitions enabled in state `s`"""
        return list(self.__enabled(s))

    def enabled_take_one(self, s: State = None) -> Transition:
        """Returns the first enabled transition in state `s`"""
        return next(iter(self.__enabled(s)), None)

    def search(self, s: State = None, **kw) -> Generator:
        """Performs a depth-first-search of the state space"""
        return search(self, s, **kw)

    def bfs(self, s: State = None, **kw) -> Generator:
        """Performs a breadth-first-search of the state space"""
        return bfs(self, s, **kw)

    def rename(
        self,
        state_fn: RenameFunction = None,
        action_fn: RenameFunction = None,
        name: str = None,
    ) -> "MDP":
        """Clones the MDP, renaming states and actions using supplied rename functions"""
        states, actions = (
            rename_map(self.states, state_fn),
            rename_map(self.actions, action_fn),
        )
        if not self.is_process:
            return MarkovDecisionProcess(
                *(p.rename(state_fn, action_fn) for p in self.processes)
            )
        if name is None:
            name = self.name
        return MarkovDecisionProcess(
            [tr.rename(states, actions) for tr in self.transitions],
            name=name,
            init=self.init.rename(states),
        )

    def to_graph(self, file_path: str = None, **kw) -> Digraph:
        """Compiles the MDP to a Digraph using Graphviz"""
        return graph(self, file_path=file_path, **kw)

    def to_prism(self, file_path: str = None, **kw) -> str:
        """Compiles the MDP to the Prism Model Checler language"""
        return to_prism(self, file_path, **kw)

    @property
    def states(self) -> frozenset[str]:
        """The set of local states in the MDP"""
        if not self._states:
            self.__set_states_and_actions()
        return self._states

    @property
    def actions(self) -> frozenset[str]:
        """The set of actions in the MDP"""
        if not self._actions:
            self.__set_states_and_actions()
        return self._actions

    @property
    def is_process(self) -> bool:
        """Boolean value describing if the MDP is a process
        (if false, the MDP is a system)
        """
        return len(self.processes) == 1

    @property
    def is_valid(self) -> bool:
        """Boolean value describing if the MDP is valid"""
        is_valid, _ = validate(self)
        return is_valid

    def __eq__(self, other: MDP) -> bool:
        init = self.init == other.init
        trs = all(tr in other.transitions for tr in self.transitions)
        return init and trs

    def __hash__(self) -> int:
        return id(self)

    def __repr__(self) -> str:
        return f"MDP({self.name})"

    def __str__(self) -> str:
        buffer = f"mdp {_h(_h.variable, self.name)}:\n"
        buffer += f"  init := {self.init}\n"
        buffer += "\n".join(f"  {tr}" for tr in self.transitions) + "\n"
        return buffer

    def __iter__(self) -> Iterator[str]:
        return iter(self.states)

    def __contains__(self, key: str) -> bool:
        return key in self.states

    def __enabled(self, s: State = None) -> Iterable[Transition]:
        if s is None:
            s = self.init
        return filter(lambda tr: tr.is_enabled(s), self.transitions)

    def __bind_transition(self, tr: TransitionDescription):
        if not isinstance(tr, Transition):
            tr = transition(*tr)

        if self.is_process:
            process = {self}
        else:
            process = set(p for p in self.processes if tr.pre(p))

        return tr.bind(process)

    def __set_states_and_actions(self):
        states, actions = set(), set()
        for tr in self.transitions:
            states = states.union(tr.pre)
            for (s_prime, _), _ in tr.post.items():
                states = states.union(s_prime)
            actions = actions.union({tr.action})
        self._states = frozenset(states)
        self._actions = frozenset(actions)


@dataclass(eq=True, frozen=True)
class _MDP:
    name: str
    states: frozenset[str]
    init: State

    def rename(self, state_fn, _) -> "_MDP":
        """Clone and rename states"""
        states = rename_map(self.states, state_fn)
        return _MDP(
            self.name, frozenset(states.values()), self.init.rename(states)
        )

    def __iter__(self) -> Iterator[str]:
        return iter(self.states)

    def __contains__(self, key: str) -> bool:
        return key in self.states
