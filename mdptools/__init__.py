"""Tools for representing and manipulating Markov Decision Processes (MDP)
"""
from .mdp import MarkovDecisionProcess
from .graph import graph
from .validate import validate

from .utils import highlight as _c

use_colors = _c.use_colors
