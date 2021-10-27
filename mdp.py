from typing import Callable, Union as _union, TYPE_CHECKING
from scipy.sparse.lil import lil_matrix as _lil_matrix

import utils as _utils
from validate import validate


if TYPE_CHECKING:
    from render import Digraph


use_colors = _utils.use_colors


# Custom types
TransitionMap = dict[str, _union[
    set[str],
    dict[str, _union[
        dict[str, float],
        float]],
    ]]


class MDP:
    def __init__(self,
            transition_map: TransitionMap,
            S: _union[list[str], str] = [],
            A: _union[list[str], str] = [],
            s_init: str = None,
            name: str = 'M'):
        self._init = False
        self.is_valid = False
        self.errors = []
        self._validate_on = True

        self.name = name
        self.S, self.A, self.P = _utils.map_list(S), _utils.map_list(A), []

        if len(self.S) == 0 or len(self.A) == 0:
            _utils.walk_dict(transition_map, self.__infer_states_and_actions)
            
        self.s_init = s_init
        
        self.__suspend_validation(lambda: (
            self.__reset(),
            _utils.walk_dict(transition_map, self.__setitem__)
        ))

        self._init = True
    

    def __getitem__(self, indices):
        s, a, s_prime = _utils.parse_sas_str(indices)
        if a == None:
            return self.actions(s)
        if s_prime == None:
            return self.dist(s, a)
        return self.__ref_matrix(s).__getitem__((self.A[a], self.S[s_prime]))


    def __setitem__(self, indices, value):
        s, a, s_prime = _utils.parse_sas_str(indices)

        if a == None:
            if isinstance(value, dict) or isinstance(value, set):
                self.__set_special([s], value)
                return

        if s_prime == None:
            if isinstance(value, dict):
                self.__set_special([s, a], value)
                return
            elif isinstance(value, set):
                raise Exception(_utils.dist_wrong_value(s, a, value))
            elif isinstance(value, str):
                s_prime, value = value, 1.0
            else:
                s_prime = s

        if self._init:
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


    def __ref_matrix(self, s: str) -> _lil_matrix:
        return self.P[self.S[s]]


    def __set_special(self, path, value):
        self.__suspend_validation(lambda: (
            self.__reset(path),
            _utils.walk_dict(value, self.__setitem__, path)
        ))


    def __suspend_validation(self, callback):
        old, self._validate_on = self._validate_on, False
        
        callback()

        if old:
            self._validate_on = True
            self.validate()


    def __reset(self, path = []):
        s, a, s_prime = _utils.parse_sas_str(path)
        shape = self.shape

        if s == None:
            self.P = [_lil_matrix(shape, dtype=float) for _ in self.S]
        elif a == None:
            i = self.S[s]
            if i >= len(self.P):
                self.P += [None]
            self.P[i] = _lil_matrix(shape, dtype=float)
        elif s_prime == None:
            ref = self.__ref_matrix(s)
            for s_prime in self.S:
                ref[self.A[a]] = 0.0
        else:
            self[s, a, s_prime] = 0.0


    def __resize(self):
        shape = self.shape
        for m in self.P:
            m.resize(shape)


    def __infer_states_and_actions(self, path, _):
        s, a, s_prime = _utils.parse_sas_str(path)
        self.__add_state(s)
        if a != None:
            self.__add_action(a)
        if s_prime != None:
            self.__add_state(s_prime)


    def __add_state(self, s: str):
        if not s in self.S:
            self.S[s] = len(self.S)
            if self._init:
                self.__reset(s)


    def __add_action(self, a: str):
        if not a in self.A:
            self.A[a] = len(self.A)
            if self._init:
                self.__resize()


    def __rename_states(self, callback):
        self.S = { (callback(s) or s): i for s, i in self.S.items() }


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
    def transition_map(self):
        return { s: self.actions(s) for s in self.S}


    def enabled(self, s):
        return { a for a in self.A for s_prime in self.S if self[s, a, s_prime] > 0 }


    def actions(self, s):
        return { a: self.dist(s, a) for a in self.enabled(s) }


    def dist(self, s, a):
        return { s_prime: self[s, a, s_prime] for s_prime in self.S if self[s, a, s_prime] > 0}

    
    def validate(self) -> bool:
        if self._validate_on:
            self.is_valid, self.errors = validate(self, raise_exception=False)
        return self.is_valid


    def rn(self, old: str = '', new: str = '', name: str = None,
                      callback: Callable[[str], str] = None) -> 'MDP':
        clone = self.__copy__()
        clone.__rename_states(callback or (lambda s: s.replace(old, new)))
        if name != None:
            clone.name = name
        return clone


    def equals(self, m2: 'MDP') -> bool:
        return self.transition_map == m2.transition_map and self.s_init == m2.s_init


    def parallel(self, m2: 'MDP', name: str = None) -> 'MDP':
        return parallel(self, m2, name)


def parallel(m1: MDP, m2: MDP, name: str = None) -> MDP:
    from parallel import parallel as _parallel
    return _parallel(m1, m2, name)


def set_parallel_separator(sep: str = '_'):
    from parallel import parallel as _parallel
    _parallel.separator = sep

def get_parallel_separator() -> str:
    from parallel import parallel as _parallel
    return _parallel.separator


def graph(mdp: _union[MDP, list[MDP]], file_path: str,
    file_format: str = 'svg') -> 'Digraph':
    from render import graph
    return graph(mdp, file_path, file_format)

