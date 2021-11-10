import sys

from .types import (
    Action,
    Distribution,
    ErrorCode,
    MarkovDecisionProcess,
    State,
)
from .utils import np, highlight as _h, format_str, float_is


MDP_REQ_EN_S_NONEMPTY: ErrorCode = (0, "∀ s ∈S : en(s) != Ø")
MDP_REQ_SUM_TO_ONE: ErrorCode = (
    1,
    "∀ s ∈ S, a ∈ en(s) : Σ_(s' ∈ S) P(s,a,s') = 1",
)


def validate(
    mdp: MarkovDecisionProcess, raise_exception: bool = False
) -> tuple[bool, list[tuple[ErrorCode, str]]]:
    """Validates a MDP based on the defined conditions:

    1. ∀ s ∈ S : en(s) != Ø
    2. ∀ s ∈ S, a ∈ en(s) : Σ_(s' ∈ S) P(s,a,s') = 1

    Args:
        mdp (MarkovDecisionProcess): The MDP process to validate
        raise_exception (bool, optional): Raise an exception if the MDP is invalid. Defaults to False.

    Raises:
        Exception: Invalid MDP

    Returns:
        tuple[bool, list[tuple[ErrorCode, str]]]: (is_valid, errors)
    """
    total_errors = []
    buffer = []

    def add_err(err_code: ErrorCode, err: str):
        nonlocal total_errors
        total_errors += [(err_code, err)]
        return [
            f"[{_h(_h.fail, 'Failed')}] {_h(_h.note, err_code[1])}\n{' '*9}>> {err}"
        ]

    en_s_nonempty, errors = __validate_enabled_nonempty(mdp)
    if not en_s_nonempty:
        for err in errors:
            buffer += add_err(MDP_REQ_EN_S_NONEMPTY, err)

    sum_to_one, errors = __validate_sum_to_one(mdp)
    if not sum_to_one:
        for err in errors:
            buffer += add_err(MDP_REQ_SUM_TO_ONE, err)

    if len(buffer) != 0:
        message = _h(_h.error, f"Not a valid MDP [{mdp.name}]:\n") + "\n".join(
            buffer
        )
        if raise_exception:
            sys.tracebacklimit = 0
            raise Exception(message)

    return (len(buffer) == 0, total_errors)


def __validate_enabled_nonempty(
    mdp: MarkovDecisionProcess,
) -> tuple[bool, list[str]]:
    """Validate: 'forall s in S : en(s) != {}'"""
    errors = [
        f"{_h(_h.function, 'en')}({format_str(s, _h.state)}) -> {_h(_h.error, '{}')}"
        for s, _ in mdp.search()
        if len(mdp.enabled(s)) == 0
    ]
    return (len(errors) == 0, errors)


def __validate_sum_to_one(
    mdp: MarkovDecisionProcess,
) -> tuple[bool, list[str]]:
    """Validate: 'forall s in S, a in en(s) : sum_(s' in S) P(s, a, s') = 1'"""
    errors = []

    for a, s, _, dist in mdp.transitions:
        sum_a = np.abs(sum(dist.values()))
        if not float_is(sum_a, 1.0):
            errors += __format_sum_to_one(dist, s, a, sum_a)

    return (len(errors) == 0, errors)


def __format_sum_to_one(
    dist: Distribution, s: State, a: Action, sum_a: float
) -> list[str]:
    return [
        f"{_h(_h.function, 'Dist')}({format_str(s, _h.state)}, "
        f"{_h(_h.action, a)}) -> {format_str(dist)} "
        f"{_h(_h.comment, '// sum -> ') + _h(_h.error, str(sum_a))}"
    ]
