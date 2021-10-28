from .utils.types import MarkovDecisionProcess


def parallel(
    m1: MarkovDecisionProcess, m2: MarkovDecisionProcess, name: str = None
) -> MarkovDecisionProcess:
    """Performs parallel composition of two MDPs."""
    # pylint: disable=redefined-outer-name
    from .mdp import MarkovDecisionProcess

    transition_map = {}
    act_intersect = set(m1.A).intersection(set(m2.A))

    def compose(s, t, left: bool = True):
        if not left:
            s, t = t, s
        s_name = __c_names(s, t)
        act_s, act_t = m1.actions(s), m2.actions(t)
        transition_map[s_name] = {}
        transition_map[s_name] = {
            **compose_actions(act_s, act_t, t, True),
            **compose_actions(act_t, act_s, s, False),
        }

    def compose_actions(act_s, act_t, t, left):
        action_map = {}
        for a in act_s:
            if not a in act_intersect:
                action_map[a] = compose_dist(act_s[a], {t: 1.0}, left)
            elif a in act_t:
                action_map[a] = compose_dist(act_s[a], act_t[a], left)
        return action_map

    def compose_dist(dist_s, dist_t, left):
        for s_prime in dist_s:
            for t_prime in dist_t:
                if not exists(s_prime, t_prime, left):
                    compose(s_prime, t_prime, left)
        return __c_actions(dist_s, dist_t, left)

    def exists(s, t, left):
        return __c_names(s, t, left=left) in transition_map

    compose(m1.s_init, m2.s_init)
    A_union = __a_union(m1, m2)
    s_init = __c_names(m1.s_init, m2.s_init)
    name = name or __c_names(m1.name, m2.name, "||")
    return MarkovDecisionProcess(
        transition_map, A=A_union, s_init=s_init, name=name
    )


parallel.separator = "_"


def __c_names(n1: str, n2: str, sep: str = None, left: bool = True) -> str:
    if sep is None:
        sep = parallel.separator
    return n1 + sep + n2 if left else n2 + sep + n1


def __c_actions(dist: dict, other_dist: dict, left: bool = True) -> dict:
    return {
        __c_names(s_prime, t_prime, left=left): s_value * t_value
        for s_prime, s_value in dist.items()
        for t_prime, t_value in other_dist.items()
    }


def __a_union(
    m1: MarkovDecisionProcess, m2: MarkovDecisionProcess
) -> list[str]:
    return list(dict.fromkeys(list(m1.A) + list(m2.A)))
