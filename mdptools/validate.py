import sys
import numpy as _np

from .utils.types import ErrorCode, MarkovDecisionProcess
from .utils import highlight as _c, lit_str, prompt


MDP_REQ_EN_S_NONEMPTY: ErrorCode = (0, "forall s in S : en(s) != {}")
MDP_REQ_SUM_TO_ONE: ErrorCode = (1, "forall s in S, a in en(s) : sum_(s' in S) P(s, a, s') = 1")


def validate(mdp: MarkovDecisionProcess, raise_exception: bool = True) -> bool:
    mdp.errors = []
    buffer = []

    def add_err(err_code: ErrorCode, err: str):
        mdp.errors += [(err_code, err)]
        return [prompt.fail(err_code[1], err)]

    en_s_nonempty, errors = __validate_enabled_nonempty(mdp)
    if not en_s_nonempty:
        for err in errors:
            buffer += add_err(MDP_REQ_EN_S_NONEMPTY, err)

    sum_to_one, errors = __validate_sum_to_one(mdp)
    if not sum_to_one:
        for err in errors:
            buffer += add_err(MDP_REQ_SUM_TO_ONE, err)

    if len(buffer) != 0:
        message = _c[_c.error, f"Not a valid MDP [{mdp.name}]:\n"] + "\n".join(buffer)
        if raise_exception:
            sys.tracebacklimit = 0
            raise Exception(message)

    return len(buffer) == 0


def __validate_enabled_nonempty(mdp: MarkovDecisionProcess) -> tuple[bool, list[str]]:
    """ Validate: 'forall s in S : en(s) != {}'
    """
    errors = [f"{_c[_c.function, 'en']}({_c[_c.state, s]}) -> {_c[_c.error, '{}']}"
        for s in mdp.S if len(mdp.enabled(s)) == 0]
    return (len(errors) == 0, errors)


def __validate_sum_to_one(mdp: MarkovDecisionProcess) -> tuple[bool, list[str]]:
    """ Validate: 'forall s in S, a in en(s) : sum_(s' in S) P(s, a, s') = 1'
    """
    errors = [f"{_c[_c.function, 'Dist']}({_c[_c.state, s]}, {_c[_c.action, a]}) ->"
        f" {lit_str(mdp.dist(s, a))} {_c[_c.comment, '// sum -> '] + _c[_c.error, str(sum_a)]}"
        for s in mdp.S for a in mdp.enabled(s)
        if (sum_a := _np.abs(sum([mdp[s, a, s_prime] for s_prime in mdp.S])))
            <= 10*_np.spacing(_np.float64(1))]
    return (len(errors) == 0, errors)
