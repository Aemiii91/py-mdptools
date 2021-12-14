"""Tools for representing and manipulating Markov Decision Processes (MDP)
"""
from .mdp import MarkovDecisionProcess
from .graph import graph
from .validate import validate

from .utils import highlight as _h, logger, set_logging_level, pr_max

use_colors = _h.use_colors
