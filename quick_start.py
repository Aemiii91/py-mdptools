# %%
from typing import Literal, Tuple
from mdptoolbox import mdp, example
import numpy as np
from enum import Enum
from numpy.core.numeric import indices
from scipy.sparse import csr_matrix
import re


def stringify(obj) -> str:
    return obj.__str__().replace("'", "")


# %%
# MDP
class MDP:
    def __init__(self, S: Enum, Act: Enum, P: dict[list[int], any]):
        self.S = S
        self.Act = Act
        self.P = np.array([
            csr_matrix((len(Act), len(S)), dtype=float)
            for _ in range(len(S))])
        for (sas, p) in P.items():
            self.__set(sas, p)
        self.valid = self.__validate()
    
    def __getitem__(self, indices):
        if not isinstance(indices, tuple):
            return self.P[indices.value]
        i = iter(indices)
        s, rest = next(i), list(i)
        return self[s].__getitem__(tuple(x.value for x in rest))

    def __setitem__(self, indices, value):
        if not isinstance(indices, tuple):
            return
        i = iter(indices)
        s, rest = next(i), list(i)
        return self[s].__setitem__(tuple(x.value for x in rest), value)

    def __repr__(self):
        return "\n".join([
            f"en({s.name}) = {stringify(self.actions(s))}"
            for s in self.S])

    def __str__(self):
        return self.__repr__()

    def __set(self, sas, p):
        s, a, s_prime = [x for x in re.split(r"\s*,\s*", sas)]
        s, a, s_prime = self.S[s], self.Act[a], self.S[s_prime]
        self[s, a, s_prime] = p

    def __validate(self):
        total_errors = []
        en_s_nonempty, errors = self.__validate_en_s_nonempty()
        if not en_s_nonempty:
            for err in errors:
                total_errors.append(f"Requirement not met: \"forall s in S : en(s) != {{}}\". [{err}]")
        sum_to_one, errors = self.__validate_sum_to_one()
        if not sum_to_one:
            for err in errors:
                total_errors.append(f"Requirement not met: \"forall s in S, a in en(s) : sum_(s' in S) P(s, a, s') = 1\"'.\n[{err})]")
        if len(total_errors) != 0:
            raise Exception("\n".join(total_errors))
        return True

    def __validate_en_s_nonempty(self):
        # Requirement: 'forall s in S : en(s) != empty'
        errors = []
        for s in self.S:
            en = self.enabled(s)
            if len(en) == 0:
                errors.append(s.name)
        return (len(errors) == 0, errors)

    def __validate_sum_to_one(self):
        # Requirement: 'forall s in S, a in en(s) : sum_(s' in S) P(s, a, s') = 1'
        errors = []
        for s in self.S:
            en = self.enabled(s)
            for a in en:
                a_sum = sum([self[s, a, s_prime] for s_prime in self.S])
                if a_sum != 1:
                    errors.append(f"({s.name}, {a.name}")
        return (len(errors) == 0, errors)

    def enabled(self, s):
        enabled = []
        for a in self.Act:
            for s_prime in self.S:
                if (self[s, a, s_prime] > 0 and a not in enabled):
                    enabled.append(a);
        return enabled;

    def actions(self, s):
        return {a.name: self.dist(s, a) for a in self.enabled(s)}

    def dist(self, s, a):
        d = { s_prime.name: self[s, a, s_prime] for s_prime in self.S if self[s, a, s_prime] > 0}
        return d if len(d) > 1 else next(iter(d))


class S(Enum):
    s0, s1, s2, s3 = range(4)

class Act(Enum):
    a, b, x, y, z, tau_1 = range(6)

P = {
    's0, a, s1': .2,
    's0, a, s2': .8,
    's0, b, s2': .7,
    's0, b, s3': .3,
    # 's1, tau_1, s1': 1,
    's2, x, s2': 1,
    's2, y, s2': 1,
    's2, z, s2': 1,
    's3, x, s3': 1,
    's3, z, s3': 1
}

M = MDP(S, Act, P)
M

# %%
