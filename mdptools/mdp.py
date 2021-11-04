from scipy.sparse.lil import lil_matrix

from .types import (
    Action,
    MarkovDecisionProcess as MDP,
    State,
    ActionMap,
    DistributionMap,
    ErrorCode,
    LooseTransitionMap,
    StateOrAction,
    TransitionMap,
    RenameFunction,
    Callable,
    Union,
    Digraph,
    Iterable,
)
from .utils import (
    map_list,
    tree_walker,
    parse_indices,
    key_by_value,
    rename_map,
    rename_transition_map,
)
from .utils.prompt import dist_wrong_value
from .utils.stringify import stringify

from .validate import validate
from .graph import graph


DEFAULT_NAME = "M"


class MarkovDecisionProcess:
    """The Markov Decision Process class."""

    def __init__(
        self,
        transition_map: LooseTransitionMap,
        S: Union[list[State], str] = None,
        A: Union[list[Action], str] = None,
        init: State = None,
        name: str = None,
        no_validation: bool = False,
    ):
        self._did_init = False
        self._validate_on = not no_validation
        self.is_valid = False
        self.errors: list[tuple[ErrorCode, str]] = []
        if name is None:
            name = DEFAULT_NAME
        self.name = name
        self.S, self.A, self.P = map_list(S), map_list(A), []
        if len(self.S) == 0 or len(self.A) == 0:
            tree_walker(transition_map, self.__infer_states_and_actions)
        self.init = init
        self.__suspend_validation(
            lambda: (
                self.__reset(),
                tree_walker(transition_map, self.__setitem__),
            )
        )
        self._did_init = True

    # Public properties
    # -----------------

    @property
    def init(self) -> str:
        return key_by_value(self.S, self._s_init) or None

    @init.setter
    def init(self, s: State):
        self._s_init = self.S[s] if s in self.S else 0

    @property
    def shape(self):
        return (len(self.A), len(self.S))

    @property
    def transition_map(self) -> TransitionMap:
        return {s: self.actions(s) for s in self.S}

    # Public methods
    # --------------

    def equals(self, other: "MDP") -> bool:
        return (
            self.transition_map == other.transition_map
            and self.init == other.init
        )

    def enabled(self, s: State) -> set[str]:
        if s not in self.S:
            return None
        return set(self.__enabled_generator(s))

    def actions(self, s: State) -> ActionMap:
        if s not in self.S:
            return None
        return {a: self.dist(s, a) for a in self.__enabled_generator(s)}

    def dist(self, s: State, a: Action) -> DistributionMap:
        if s in self.S and a in self.A:
            return {
                s_prime: self[s, a, s_prime]
                for s_prime in self.S
                if self[s, a, s_prime] > 0
            }
        return None

    def validate(
        self, force: bool = True, raise_exception: bool = False
    ) -> bool:
        if force or self._validate_on:
            self.is_valid = validate(self, raise_exception)
        return self.is_valid

    def remake(
        self,
        rename_states: RenameFunction = None,
        rename_actions: RenameFunction = None,
        name: str = None,
    ) -> "MDP":
        map_S = rename_map(self.S, rename_states)  # rename states
        map_A = rename_map(self.A, rename_actions)  # rename actions
        S, A = list(map_S.values()), list(map_A.values())  # apply new names
        # Rename all keys in the transition map
        tm = rename_transition_map(self.transition_map, map_S, map_A)
        # Keep old name, if no new name is specified
        if name is None:
            name = self.name
        # Create an instance of `MDP` with the renamed data
        return MarkovDecisionProcess(tm, S, A, map_S[self.init], name)

    def graph(self, file_path: str, **kwargs) -> Digraph:
        return graph(self, file_path, **kwargs)

    # Private methods
    # ---------------

    def __resize(self):
        shape = self.shape
        for m in self.P:
            m.resize(shape)

    def __ref_matrix(self, s: State) -> lil_matrix:
        return self.P[self.S[s]]

    def __infer_states_and_actions(self, path, _):
        s, a, s_prime = parse_indices(path)
        self.__add_state(s)
        if a is not None:
            self.__add_action(a)
        if s_prime is not None:
            self.__add_state(s_prime)

    def __add_state(self, s: State):
        if s not in self.S:
            self.S[s] = len(self.S)
            if self._did_init:
                self.__resize()
                self.__reset(s)

    def __add_action(self, a: Action):
        if not a in self.A:
            self.A[a] = len(self.A)
            if self._did_init:
                self.__resize()

    def __set_special(self, path: list[StateOrAction], value):
        self.__suspend_validation(
            lambda: (
                self.__reset(path),
                tree_walker(value, self.__setitem__, path),
            )
        )

    def __suspend_validation(self, callback: Callable[[], None]):
        validate_on, self._validate_on = self._validate_on, False
        callback()
        if validate_on:
            self._validate_on = True
            self.validate(force=False)

    def __reset(self, path: list[StateOrAction] = None):
        s, a, s_prime = parse_indices(path)

        if s is None:
            # Reset all matrices
            shape = self.shape
            self.P = [lil_matrix(shape, dtype=float) for _ in self.S]
        elif a is None:
            # Add elements until index matches
            while len(self.P) <= self.S[s]:
                self.P.append(None)
            # Reset the whole matrix
            self.P[self.S[s]] = lil_matrix(self.shape, dtype=float)
        elif s_prime is None:
            # Reset a row of the matrix
            for s_prime in self.S:
                self.__reset([s, a, s_prime])
        else:
            # Reset a specific value
            self[s, a, s_prime] = 0.0

    def __enabled_generator(self, s: State) -> Iterable:
        return (
            a for a in self.A for s_prime in self.S if self[s, a, s_prime] > 0
        )

    # Overrides
    # ---------

    def __getitem__(self, indices):
        s, a, s_prime = parse_indices(indices)
        if a is None:
            return self.actions(s)
        if s_prime is None:
            return self.dist(s, a)
        return self.__ref_matrix(s).__getitem__((self.A[a], self.S[s_prime]))

    def __setitem__(self, indices, value):
        s, a, s_prime = parse_indices(indices)

        if self._did_init:
            self.__add_state(s)

        if a is None:
            # Set the enabled actions of `s`
            # Note: If a `set` is given, the target will be `s` with probability 1.
            if isinstance(value, (dict, set)):
                self.__set_special([s], value)
                return
            if isinstance(value, str):
                # String is given, which is short for a transition to self
                self.__set_special([s, value], s)
            return

        if self._did_init:
            self.__add_action(a)

        if s_prime is None:
            # Set the `dist(s, a)`
            if isinstance(value, (dict, str, tuple)):
                # A `dict` describes the map of s' -> p.
                # If a string is given, is must describe `s_prime`
                self.__set_special([s, a], value)
                return
            if isinstance(value, set):
                # We do not allow an action to have more than one non-probabilistic
                # transition (multi-threading)
                raise Exception(dist_wrong_value(s, a, value))
            # A `p` value is given, representing the probability of transitioning to self
            s_prime = s

        if self._did_init:
            self.__add_state(s_prime)

        self.__ref_matrix(s).__setitem__((self.A[a], self.S[s_prime]), value)
        self.validate(force=False)

    def __repr__(self):
        return stringify(self)

    def __len__(self):
        return len(self.S)

    def __eq__(self, m2: "MDP") -> bool:
        return self.equals(m2)
