from scipy.sparse.lil import lil_matrix

from .utils.types import (
    MarkovDecisionProcess as MDP,
    ActionMap,
    DistributionMap,
    ErrorCode,
    LooseTransitionMap,
    TransitionMap,
    RenameFunction,
    Callable,
    Union,
    Digraph,
)
from .utils.utils import (
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
from .parallel import parallel
from .graph import graph


DEFAULT_NAME = "M"


class MarkovDecisionProcess:
    """The Markov Decision Process class."""

    def __init__(
        self,
        transition_map: LooseTransitionMap,
        S: Union[list[str], str] = None,
        A: Union[list[str], str] = None,
        init: str = None,
        name: str = DEFAULT_NAME,
    ):
        self._did_init = False
        self._validate_on = True
        self.is_valid = False
        self.errors: list[tuple[ErrorCode, str]] = []
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
    def init(self, s):
        self._s_init = self.S[s] if isinstance(s, str) else 0

    @property
    def shape(self):
        return (len(self.A), len(self.S))

    @property
    def transition_map(self) -> TransitionMap:
        return {s: self.actions(s) for s in self.S}

    # Public methods
    # --------------

    def equals(self, m2: "MDP") -> bool:
        return (
            self.transition_map == m2.transition_map and self.init == m2.init
        )

    def enabled(self, s) -> set[str]:
        return {
            a for a in self.A for s_prime in self.S if self[s, a, s_prime] > 0
        }

    def actions(self, s) -> ActionMap:
        return {a: self.dist(s, a) for a in self.enabled(s)}

    def dist(self, s, a) -> DistributionMap:
        return {
            s_prime: self[s, a, s_prime]
            for s_prime in self.S
            if self[s, a, s_prime] > 0
        }

    def validate(self) -> bool:
        if self._validate_on:
            self.is_valid = validate(self, raise_exception=False)
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
        return MarkovDecisionProcess(
            tm, S, A, map_S[self.init], name or self.name
        )

    def parallel(self, m2: "MDP", name: str = None) -> "MDP":
        return parallel(self, m2, name)

    def graph(self, file_path: str, file_format: str = "svg") -> Digraph:
        return graph(self, file_path, file_format)

    # Private methods
    # ---------------

    def __resize(self):
        shape = self.shape
        for m in self.P:
            m.resize(shape)

    def __ref_matrix(self, s: str) -> lil_matrix:
        return self.P[self.S[s]]

    def __infer_states_and_actions(self, path, _):
        s, a, s_prime = parse_indices(path)
        self.__add_state(s)
        if a is not None:
            self.__add_action(a)
        if s_prime is not None:
            self.__add_state(s_prime)

    def __add_state(self, s: str):
        if s not in self.S:
            self.S[s] = len(self.S)
            if self._did_init:
                self.__reset(s)

    def __add_action(self, a: str):
        if not a in self.A:
            self.A[a] = len(self.A)
            if self._did_init:
                self.__resize()

    def __set_special(self, path, value):
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
            self.validate()

    def __reset(self, path=None):
        s, a, s_prime = parse_indices(path)
        if s is None:
            self.__reset_all()
        elif a is None:
            self.__reset_matrix(s)
        elif s_prime is None:
            self.__reset_matrix_values(s, a)
        else:
            self[s, a, s_prime] = 0.0

    def __reset_all(self):
        shape = self.shape
        self.P = [lil_matrix(shape, dtype=float) for _ in self.S]

    def __reset_matrix(self, s: str):
        if self.S[s] >= len(self.P):
            self.P += [None]
        self.P[self.S[s]] = lil_matrix(self.shape, dtype=float)

    def __reset_matrix_values(self, s: str, a: str):
        ref = self.__ref_matrix(s)
        for s_prime in self.S:
            ref[self.A[a], self.S[s_prime]] = 0.0

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

        if s_prime is None:
            # Set the `dist(s, a)`
            if isinstance(value, (dict, str)):
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
            self.__add_state(s)
            self.__add_action(a)
            self.__add_state(s_prime)

        self.__ref_matrix(s).__setitem__((self.A[a], self.S[s_prime]), value)
        self.validate()

    def __repr__(self):
        return stringify(self)

    def __or__(self, m2: "MDP") -> "MDP":
        return self.parallel(m2)

    def __eq__(self, m2: "MDP") -> bool:
        return self.equals(m2)

    def __copy__(self) -> "MDP":
        S, A = list(self.S), list(self.A)
        return MarkovDecisionProcess(
            self.transition_map, S, A, self.init, self.name
        )
