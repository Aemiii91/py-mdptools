""" Test helpers
"""
from mdptools import MarkovDecisionProcess
from mdptools.types import ErrorCode


def error_code(errors: list[tuple[ErrorCode, str]], idx: int = 0) -> int:
    return errors[idx][0][0]
