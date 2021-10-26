from typing import TYPE_CHECKING

import utils
from utils import prompt_fail, color_text, lit_str

_c = color_text
MDP = any

if TYPE_CHECKING:
    from mdp import MDP


def validate(mdp: MDP):
        buffer = []
        en_s_nonempty, errors = validate_enabled_nonempty(mdp)
        if not en_s_nonempty:
            for err in errors:
                prompt_fail(buffer, "forall s in S : en(s) != {}", err)
        sum_to_one, errors = validate_sum_to_one(mdp)
        if not sum_to_one:
            for err in errors:
                prompt_fail(buffer, "forall s in S, a in en(s) : sum_(s' in S) P(s, a, s') = 1", err)
        if len(buffer) != 0:
            raise Exception("\n" + "\n".join(buffer))
        return True


def validate_enabled_nonempty(mdp: MDP):
    """ Validate: 'forall s in S : en(s) != {}'
    """
    errors = []
    for s in mdp.S:
        en = mdp.enabled(s)
        if len(en) == 0:
            errors.append(f"{_c(utils.bc.LIGHTBLUE, 'en')}({_c(utils.bc.LIGHTGREEN, s)}) -> {{}}")
    return (len(errors) == 0, errors)


def validate_sum_to_one(mdp: MDP):
    """ Validate: 'forall s in S, a in en(s) : sum_(s' in S) P(s, a, s') = 1'
    """
    errors = []
    for s in mdp.S:
        en = mdp.enabled(s)
        for a in en:
            a_sum = sum([mdp[s, a, s_prime] for s_prime in mdp.S])
            if a_sum != 1:
                errors.append(f"{_c(utils.bc.LIGHTBLUE, 'Dist')}({_c(utils.bc.LIGHTGREEN, s)}, {_c(utils.bc.LIGHTGREEN, a)}) -> {lit_str(mdp.dist(s, a))} {_c(utils.bc.LIGHTGREY, '// sum -> ') + _c(utils.bc.RED, str(a_sum))}")
    return (len(errors) == 0, errors)