""" Test helpers
"""
from mdptools import MarkovDecisionProcess


def error_code(mdp: MarkovDecisionProcess, idx: int = 0) -> int:
    return mdp.errors[idx][0][0]
