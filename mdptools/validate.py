from typing import TYPE_CHECKING
import sys
import numpy as _np
from .utils.utils import prompt_fail, _c, lit_str


if TYPE_CHECKING:
    from mdp import MDP


MDP_REQ_EN_S_NONEMPTY = "forall s in S : en(s) != {}"
MDP_REQ_SUM_TO_ONE = "forall s in S, a in en(s) : sum_(s' in S) P(s, a, s') = 1"


def validate(mdp: 'MDP', raise_exception: bool = True) -> tuple[bool, list[str]]:
    buffer = []
    en_s_nonempty, errors = validate_enabled_nonempty(mdp)
    if not en_s_nonempty:
        for err in errors:
            buffer += [prompt_fail(MDP_REQ_EN_S_NONEMPTY, err)]
    sum_to_one, errors = validate_sum_to_one(mdp)
    if not sum_to_one:
        for err in errors:
            buffer += [prompt_fail(MDP_REQ_SUM_TO_ONE, err)]
    if len(buffer) != 0:
        message = _c[_c.error, f"Not a valid MDP [{mdp.name}]:\n"] + "\n".join(buffer)
        if raise_exception:
            sys.tracebacklimit = 0
            raise Exception(message)
    return (len(buffer) == 0, buffer)


def validate_enabled_nonempty(mdp: 'MDP'):
    """ Validate: 'forall s in S : en(s) != {}'
    """
    errors = [f"{_c[_c.function, 'en']}({_c[_c.state, s]}) -> {_c[_c.error, '{}']}"
        for s in mdp.S if len(mdp.enabled(s)) == 0]
    return (len(errors) == 0, errors)


def validate_sum_to_one(mdp: 'MDP'):
    """ Validate: 'forall s in S, a in en(s) : sum_(s' in S) P(s, a, s') = 1'
    """
    errors = [f"{_c[_c.function, 'Dist']}({_c[_c.state, s]}, {_c[_c.action, a]}) ->"
        f" {lit_str(mdp.dist(s, a))} {_c[_c.comment, '// sum -> '] + _c[_c.error, str(sum_a)]}"
        for s in mdp.S for a in mdp.enabled(s)
        if (sum_a := _np.abs(sum([mdp[s, a, s_prime] for s_prime in mdp.S])))
            <= 10*_np.spacing(_np.float64(1))]
    return (len(errors) == 0, errors)
