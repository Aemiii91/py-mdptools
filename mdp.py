from typing import Union
import numpy as np
from scipy.sparse.lil import lil_matrix

import utils as _utils
from validate import validate

_c = _utils.color_text
use_colors = _utils.use_colors


# Custom types
StrOrStrList = Union[list[str], str]
TransitionMap = dict[str, Union[
    set[str],
    dict[str, Union[
        dict[str, float],
        float]],
    ]]


class MDP:
    def __init__(self,
            transition_map: TransitionMap,
            S: StrOrStrList = [],
            A: StrOrStrList = [],
            s_init: str = None,
            name: str = 'M'):
        self.valid = False
        self.name = name
        self.s_init = s_init
        self.S, self.A = _utils.map_list(S), _utils.map_list(A)

        if len(self.S) == 0 or len(self.A) == 0:
            _utils.walk_dict(transition_map, self.__infer_states_and_actions)
        
        shape = (len(self.A), len(self.S))
        self.P = np.array([lil_matrix(shape, dtype=float) for _ in self.S])
        
        self._validate_on = False
        _utils.walk_dict(transition_map, self.__setitem__)

        self._validate_on = True
        self.validate()
    

    def __getitem__(self, indices):
        s, a, s_prime = _utils.parse_sas_str(indices)
        if a == None:
            return self.P[self.S[s]]
        if s_prime == None:
            s_prime = s
        return self[s].__getitem__((self.A[a], self.S[s_prime]))


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
                raise Exception(_utils.prompt_error(
                    "Set is not allowed as a distribution value.",
                    "Please use a Dictionary instead.",
                    f"{_c(_utils.bc.LIGHTBLUE, 'Dist')}({_c(_utils.bc.LIGHTGREEN, s)}, {_c(_utils.bc.LIGHTGREEN, a)}) -> {_utils.lit_str(value)}"))
            s_prime = s
        self[s].__setitem__((self.A[a], self.S[s_prime]), value)
        self.validate()


    def __repr__(self):
        lines = [f"{_c(_utils.bc.LIGHTCYAN, self.name)} ({_c(_utils.bc.LIGHTCYAN, 'MDP')}):"]
        lines += [f"  {_c(_utils.bc.PURPLE, 'S')} := {_utils.lit_str(tuple(self.S), _utils.bc.LIGHTGREEN)}"]
        lines += [f"  {_c(_utils.bc.PURPLE, 'A')} := {_utils.lit_str(tuple(self.A), _utils.bc.LIGHTRED)}"]
        lines += [f"  {_c(_utils.bc.PURPLE, 's_init')} := {_c(_utils.bc.LIGHTGREEN, self.s_init)}"]
        lines += [f"  {_c(_utils.bc.LIGHTBLUE, 'en')}({_utils.bc.LIGHTGREEN}{s}{_utils.bc.RESET}) -> {_utils.lit_str(self.actions(s), self._color_map)}"
            for s in self.S]
        return "\n".join(lines)


    def __str__(self):
        return self.__repr__()


    @property
    def _color_map(self):
        if _utils.bc.LIGHTGREEN == '':
            return {}
        return {
            _utils.bc.LIGHTGREEN: list(self.S.keys()),
            _utils.bc.LIGHTRED: list(self.A.keys())
        }


    def __set_special(self, path, value):
        old, self._validate_on = self._validate_on, False
        self.__reset(path)
        _utils.walk_dict(value, self.__setitem__, path)
        if old:
            self._validate_on = True
            self.validate()


    def __reset(self, path):
        s, a, s_prime = _utils.parse_sas_str(path)
        if a == None:
            self.P[self.S[s]] = lil_matrix((len(self.A), len(self.S)), dtype=float)
        elif s_prime == None:
            m = self.P[self.S[s]]
            for s_prime in self.S:
                m[self.A[a]] = 0.0
        else:
            self[s, a, s_prime] = 0.0


    def __infer_states_and_actions(self, path, _):
        s, a, s_prime = _utils.parse_sas_str(path)
        self.__add_state(s)
        if a != None:
            self.__add_action(a)
        if s_prime != None:
            self.__add_state(s_prime)


    def __add_state(self, s: str):
        if not self.s_init:
            self.s_init = s
        if not s in self.S:
            self.S[s] = len(self.S)


    def __add_action(self, a: str):
        if not a in self.A:
            self.A[a] = len(self.A)


    def validate(self) -> bool:
        if self._validate_on:
            self.valid = validate(self)
        return self.valid


    def enabled(self, s):
        enabled = []
        for a in self.A:
            for s_prime in self.S:
                if self[s, a, s_prime] > 0 and a not in enabled:
                    enabled.append(a);
        return enabled;


    def actions(self, s):
        return {a: self.dist(s, a) for a in self.enabled(s)}


    def dist(self, s, a):
        d = { s_prime: self[s, a, s_prime] for s_prime in self.S if self[s, a, s_prime] > 0}
        return d if len(d) > 1 else next(iter(d))




if __name__ == '__main__':
    M1 = MDP({
        's0': { 'a': { 's1': .2, 's2': .8 }, 'b': { 's2': .7, 's3': .3 } },
        's1': { 'tau_1' },
        's2': { 'x', 'y', 'z' },
        's3': { 'x', 'z' }
    }, S='s0,s1,s2,s3', A='a,b,x,y,z,tau_1', name='M1')
    print(M1)
