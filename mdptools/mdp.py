from typing import Callable, Union, TYPE_CHECKING
from scipy.sparse.lil import lil_matrix as _lil_matrix

from .utils import utils as _utils
from .validate import validate


if TYPE_CHECKING:
    from render import Digraph


use_colors = _utils.use_colors


# Custom types
TransitionMap = dict[str, Union[
    set[str],
    dict[str, Union[
        dict[str, float],
        float]],
    ]]


class MDP:
    """The Markov Decision Process (MDP) class.
    """
    def __init__(self,
            transition_map: TransitionMap,
            S: Union[list[str], str] = None,
            A: Union[list[str], str] = None,
            s_init: str = None,
            name: str = 'M'):
        self._did_init = False
        self._validate_on = True
        self.is_valid = False
        self.errors = []
        self.name = name
        self.S, self.A, self.P = _utils.map_list(S), _utils.map_list(A), []
        if len(self.S) == 0 or len(self.A) == 0:
            _utils.walk_dict(transition_map, self.__infer_states_and_actions)
        self.s_init = s_init
        self.__suspend_validation(lambda: (
            self.__reset(),
            _utils.walk_dict(transition_map, self.__setitem__)
        ))
        self._did_init = True

    # Overrides
    def __getitem__(self, indices):
        s, a, s_prime = _utils.parse_sas_str(indices)
        if a is None:
            return self.actions(s)
        if s_prime is None:
            return self.dist(s, a)
        return self.__ref_matrix(s).__getitem__((self.A[a], self.S[s_prime]))

    def __setitem__(self, indices, value):
        s, a, s_prime = _utils.parse_sas_str(indices)

        if a is None:
            if isinstance(value, dict, set):
                self.__set_special([s], value)
                return

        if s_prime is None:
            if isinstance(value, dict):
                self.__set_special([s, a], value)
                return
            if isinstance(value, set):
                raise Exception(_utils.dist_wrong_value(s, a, value))
            if isinstance(value, str):
                s_prime, value = value, 1.0
            else:
                s_prime = s

        if self._did_init:
            self.__add_state(s)
            self.__add_action(a)
            self.__add_state(s_prime)

        self.__ref_matrix(s).__setitem__((self.A[a], self.S[s_prime]), value)
        self.validate()

    def __repr__(self):
        return _utils.mdp_to_str(self)

    def __str__(self):
        return self.__repr__()

    def __add__(self, m2: 'MDP') -> 'MDP':
        return self.parallel(m2)

    def __eq__(self, m2: 'MDP') -> bool:
        return self.equals(m2)

    def __copy__(self) -> 'MDP':
        return MDP(self.transition_map, list(self.S), list(self.A), self.s_init, self.name)

    # Public properties
    @property
    def s_init(self):
        return _utils.key_by_value(self.S, self._s_init) or None
    @s_init.setter
    def s_init(self, s):
        self._s_init = self.S[s] if isinstance(s, str) else 0

    @property
    def shape(self):
        return (len(self.A), len(self.S))

    @property
    def transition_map(self) -> dict[str, dict[str, dict[str, float]]]:
        return { s: self.actions(s) for s in self.S}

    # Public methods
    def equals(self, m2: 'MDP') -> bool:
        return self.transition_map == m2.transition_map and self.s_init == m2.s_init

    def enabled(self, s) -> set[str]:
        return { a for a in self.A for s_prime in self.S if self[s, a, s_prime] > 0 }

    def actions(self, s) -> dict[str, dict[str, float]]:
        return { a: self.dist(s, a) for a in self.enabled(s) }

    def dist(self, s, a) -> dict[str, float]:
        return { s_prime: self[s, a, s_prime] for s_prime in self.S if self[s, a, s_prime] > 0}

    def validate(self) -> bool:
        if self._validate_on:
            self.is_valid, self.errors = validate(self, raise_exception=False)
        return self.is_valid

    def remake(self, rename_states: _utils.RenameFunction = None,
            rename_actions: _utils.RenameFunction = None, name: str = None) -> 'MDP':
        S_map = _utils.rename_map(self.S, rename_states)
        A_map = _utils.rename_map(self.A, rename_actions)
        S, A = list(S_map.values()), list(A_map.values())
        tm = _utils.rename_transition_map(self.transition_map, S_map, A_map)
        if name is None:
            name = self.name
        return MDP(tm, S, A, S_map[self.s_init], name or self.name)

    def parallel(self, m2: 'MDP', name: str = None) -> 'MDP':
        return parallel(self, m2, name)

    def graph(self, file_path: str, file_format: str = 'svg') -> 'Digraph':
        from .render import graph as _graph
        return _graph(self, file_path, file_format)

    # Private methods
    def __ref_matrix(self, s: str) -> _lil_matrix:
        return self.P[self.S[s]]

    def __set_special(self, path, value):
        self.__suspend_validation(lambda: (
            self.__reset(path),
            _utils.walk_dict(value, self.__setitem__, path)
        ))

    def __suspend_validation(self, callback: Callable[[], None]):
        old, self._validate_on = self._validate_on, False
        callback()
        if old:
            self._validate_on = True
            self.validate()

    def __reset(self, path = None):
        s, a, s_prime = _utils.parse_sas_str(path)
        shape = self.shape
        if s is None:
            self.P = [_lil_matrix(shape, dtype=float) for _ in self.S]
        elif a is None:
            i = self.S[s]
            if i >= len(self.P):
                self.P += [None]
            self.P[i] = _lil_matrix(shape, dtype=float)
        elif s_prime is None:
            ref = self.__ref_matrix(s)
            for s_prime in self.S:
                ref[self.A[a]] = 0.0
        else:
            self[s, a, s_prime] = 0.0

    def __infer_states_and_actions(self, path, _):
        s, a, s_prime = _utils.parse_sas_str(path)
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

    def __resize(self):
        shape = self.shape
        for m in self.P:
            m.resize(shape)




def parallel(m1: MDP, m2: MDP, name: str = None) -> MDP:
    from .parallel import parallel as _parallel
    return _parallel(m1, m2, name)

def set_parallel_separator(sep: str = '_'):
    from .parallel import parallel as _parallel
    _parallel.separator = sep

def get_parallel_separator() -> str:
    from .parallel import parallel as _parallel
    return _parallel.separator


def graph(mdp: Union[MDP, list[MDP]], file_path: str,
    file_format: str = 'svg', engine: str = 'dot', rankdir: str = 'TB') -> 'Digraph':
    from .render import graph as _graph
    return _graph(mdp, file_path, file_format, engine, rankdir)
