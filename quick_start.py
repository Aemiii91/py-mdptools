# %%
from mdptoolbox import mdp, example
import numpy as np
from enum import Enum
# from scipy.sparse import csr_matrix


def isStochastic(matrix):
    """Check that ``matrix`` is row stochastic.

    Returns
    =======
    is_stochastic : bool
        ``True`` if ``matrix`` is row stochastic, ``False`` otherwise.

    """
    try:
        absdiff = (np.abs(matrix.sum(axis=1) - np.ones(matrix.shape[0])))
    except AttributeError:
        matrix = np.array(matrix)
        absdiff = (np.abs(matrix.sum(axis=1) - np.ones(matrix.shape[0])))
    return (absdiff.max() <= 10*np.spacing(np.float64(1)))

# %%
S, A = (4, 5)

class Act(Enum):
    a = 0
    b = 1
    x = 2
    y = 3
    z = 4

T = np.zeros((A, S, S))

for a in Act:
    for i in range(S):
        T[a.value, i, i] = 1.0

def set(a, s, s_prime, p):
    T[a.value, s, s] = 0.0
    T[a.value, s, s_prime] = p;

T.shape

# %%
# Transition matrix
set(Act.a, 0, 1, .2); set(Act.a, 0, 2, .8)

set(Act.b, 0, 2, .7); set(Act.b, 0, 3, .3)
set(Act.x, 2, 2, 1)
set(Act.x, 3, 3, 1)
set(Act.y, 2, 2, 1)
set(Act.z, 2, 2, 1)
set(Act.z, 3, 3, 1)

for a in Act:
    pa = T[a.value]
    print(a.name, isStochastic(pa))
    print(pa)

# %%
M = mdp.MDP(T, np.ones((A, S, S)), None, None, None)
M.P, M.R

# %%
P, R = example.forest()
P, R

# %%
