"""Tools for representing and manipulating Markov Decision Processes (MDP)
"""
from .mdp import MarkovDecisionProcess
from .parallel import parallel
from .graph import graph
from .validate import validate
import types

from .utils import highlight as _c

use_colors = _c.use_colors
