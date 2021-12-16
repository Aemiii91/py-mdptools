from operator import add
from .types import (
    Action,
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
from .utils import reduce, highlight as _h, rename_map, to_prism, flatten
from .model import (
    Transition,
    transition,
    compose_transitions,
    State,
    state,
    state_apply,
    remove_direction,
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
    _goal_states: frozenset[State] = frozenset()
    _goal_actions: frozenset[Transition] = frozenset()

    def __init__(
        self,
        *args: Union[list[TransitionDescription], MDP],
        init: StateDescription = None,
        processes: dict[str, tuple[str]] = None,
        name: str = None,
        set_method: SetMethod = None,
        goal_states: set[StateDescription] = None,
    ):
        self._states = None
        self._actions = None

        if len(args) == 1:
            # If only 1 argument is given, it must be a TransitionDescription
            transitions = next(iter(args), [])
            # If no processes are supplied, must be a process
            if processes is None:
                self._init_process(transitions, init)
            else:
                # Create "hollow" MDP for each process
                processes = [
                    _MDP(name, frozenset(states), state(states[0]))
                    for name, states in processes.items()
                ]
                self._init_system(processes, init, transitions)
        else:
            self._init_system(args, init)

        if name is not None:
            self.name = name
        if set_method is not None:
            self.set_method = set_method
        if goal_states is not None:
            self.goal_states = goal_states

    def _init_process(
        self, transitions: list[TransitionDescription], init: StateDescription
    ):
        if isinstance(transitions, MarkovDecisionProcess):
            raise ValueError

        if init is None:
            # Set initial state to be the first transition's preset
            init = next(iter(transitions))[1]

        self.processes = [self]
        self.transitions = list(map(self._bind_transition, transitions))

        if init is not None:
            self.init = state_apply(init)

    def _init_system(
        self,
        processes: Iterable[MDP],
        init: StateDescription,
        transitions: list[TransitionDescription] = None,
    ):
        self.processes = list(processes)

        if transitions is None:
            self.transitions = compose_transitions(self.processes)
        else:
            self.transitions = list(map(self._bind_transition, transitions))

        self.name = "||".join(p.name for p in self.processes)

        if init is None:
            self.init = reduce(add, (p.init for p in self.processes))
        else:
            self.init = state_apply(init)

    def P(self, s: State, a: Action, t: State) -> float:
        """Get the probability value of a transition."""
        tr = next(filter(lambda tr: tr.action == a, self._enabled(s)), None)
        return next((p for (s_, _), p in tr.post.items() if t == s_), 0.0)

    def can_reach_goal(self, s: State) -> bool:
        """Check if a set of goal states can be reached from a state `s`."""
        return any(g <= t for t, _ in self.search(s) for g in self.goal_states)

    def enabled(self, s: State = None) -> list[Transition]:
        """Returns a list of transitions enabled in state `s`"""
        return list(self._enabled(s))

    def enabled_take_one(
        self, s: State = None, avoid_self_loops: bool = True
    ) -> Transition:
        """Returns the first enabled transition in state `s`"""
        it = iter(self._enabled(s))
        tr = next(it, None)
        while avoid_self_loops and tr is not None and tr.only_successor(s):
            tr = next(it, None)
        return tr

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
    def goal_states(self) -> frozenset[State]:
        return self._goal_states

    @goal_states.setter
    def goal_states(self, value: Iterable[Union[State, StateDescription]]):
        if self._goal_actions:
            print("Mutation!")
        self._goal_states = frozenset(map(state, value))
        self._goal_actions = frozenset(
            filter(self._goal_action_filter, self.transitions)
        )

    @property
    def goal_actions(self) -> list[Transition]:
        """Transitions required to reach the goal states."""
        return [tr for tr in self.transitions if tr in self._goal_actions]

    @property
    def states(self) -> frozenset[str]:
        """The set of local states in the MDP"""
        if not self._states:
            self._set_states_and_actions()
        return self._states

    @property
    def actions(self) -> frozenset[str]:
        """The set of actions in the MDP"""
        if not self._actions:
            self._set_states_and_actions()
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
        buffer = f"mdp {_h.variable(self.name)}:\n"
        buffer += f"  init := {self.init}\n"
        buffer += "\n".join(f"  {tr}" for tr in self.transitions) + "\n"
        return buffer

    def __iter__(self) -> Iterator[str]:
        return iter(self.states)

    def __contains__(self, key: str) -> bool:
        return key in self.states

    def _enabled(self, s: State = None) -> Iterable[Transition]:
        if s is None:
            s = self.init
        return filter(lambda tr: tr.is_enabled(s), self.transitions)

    def _bind_transition(self, tr: TransitionDescription):
        if not isinstance(tr, Transition):
            tr = transition(*tr)

        if self.is_process:
            process = {self}
        else:
            process = set(p for p in self.processes if tr.pre(p))

        return tr.bind(process)

    def _set_states_and_actions(self):
        states = [tr.pre for tr in self.transitions]
        for tr in self.transitions:
            states += [s_ for (s_, _), _ in tr.post.items()]
        actions = [
            remove_direction(tr.action)
            for tr in self.transitions
            if not tr.action.startswith("tau")
        ]
        self._states = frozenset(flatten(states))
        self._actions = frozenset(actions)

    def _goal_action_filter(self, tr: Transition) -> bool:
        return any(
            s <= g or g <= s
            for s, _ in tr.post.keys()
            for g in self.goal_states
            if tr.pre != s
        )


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

    def __repr__(self) -> str:
        return f"MDP({self.name})"

    def __iter__(self) -> Iterator[str]:
        return iter(self.states)

    def __contains__(self, key: str) -> bool:
        return key in self.states
