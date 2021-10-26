from typing import Union
import numpy as np
from scipy.sparse.lil import lil_matrix

import utils
from utils import lit_str, map_list, parse_sas_str, prompt_error, walk_dict, color_text, use_colors
from validate import validate

_c = color_text
use_colors = use_colors


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
            name: str = 'M'):

        self._validate_on_set = False
        self.name = name
        self.S, self.A = map_list(S), map_list(A)
        if len(self.S) == 0 or len(self.A) == 0:
            walk_dict(transition_map, self.__infer_states_and_actions)
        shape = (len(self.A), len(self.S))
        self.P = np.array([lil_matrix(shape, dtype=float) for _ in self.S])
        walk_dict(transition_map, self.__setitem__)
        self.valid = validate(self)
        self._validate_on_set = True
    
    def __getitem__(self, indices):
        s, a, s_prime = parse_sas_str(indices)
        if a == None:
            return self.P[self.S[s]]
        if s_prime == None:
            s_prime = s
        return self[s].__getitem__((self.A[a], self.S[s_prime]))

    def __setitem__(self, indices, value):
        s, a, s_prime = parse_sas_str(indices)
        if a == None:
            if isinstance(value, dict) or isinstance(value, set):
                self.__set_special([s], value)
                return
        if s_prime == None:
            if isinstance(value, dict):
                self.__set_special([s, a], value)
                return
            elif isinstance(value, set):
                raise Exception(prompt_error(
                    "Set is not allowed as a distribution value.",
                    "Please use a Dictionary instead.",
                    f"{_c(utils.bc.LIGHTBLUE, 'Dist')}({_c(utils.bc.LIGHTGREEN, s)}, {_c(utils.bc.LIGHTGREEN, a)}) -> {lit_str(value)}"))
            s_prime = s
        self[s].__setitem__((self.A[a], self.S[s_prime]), value)
        if self._validate_on_set:
            self.valid = validate(self)

    def __repr__(self):
        lines = [f"{utils.bc.LIGHTCYAN}{self.name}: MDP{utils.bc.RESET}"]
        lines += [f"  {_c(utils.bc.PURPLE, 'S')} := {lit_str(tuple(self.S))}"]
        lines += [f"  {_c(utils.bc.PURPLE, 'A')} := {lit_str(tuple(self.A))}"]
        lines += [f"  {_c(utils.bc.LIGHTBLUE, 'en')}({utils.bc.LIGHTGREEN}{s}{utils.bc.RESET}) -> {lit_str(self.actions(s))}"
            for s in self.S]
        return "\n".join(lines)

    def __str__(self):
        return self.__repr__()

    def __set_special(self, path, value):
        old, self._validate_on_set = self._validate_on_set, False
        self.__reset(path)
        walk_dict(value, self.__setitem__, path)
        if old:
            self.valid = validate(self)
            self._validate_on_set = True

    def __reset(self, path):
        s, a, s_prime = parse_sas_str(path)
        if a == None:
            self.P[self.S[s]] = lil_matrix((len(self.A), len(self.S)), dtype=float)
        elif s_prime == None:
            m = self.P[self.S[s]]
            for s_prime in self.S:
                m[self.A[a]] = 0.0
        else:
            self[s, a, s_prime] = 0.0

    def __infer_states_and_actions(self, path, _):
        s, a, s_prime = parse_sas_str(path)
        if not s in self.S:
            self.S[s] = len(self.S)
        if a != None and not a in self.A:
            self.A[a] = len(self.A)
        if s_prime != None and not s_prime in self.S:
            self.S[s_prime] = len(self.S)

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
