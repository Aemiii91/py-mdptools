""" Test utils
"""
from mdptools import MDP


def error_code(mdp: MDP, idx: int = 0) -> int:
    return mdp.errors[idx][0][0]
