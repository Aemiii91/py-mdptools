from ..model.commands import Op
from ..types import (
    MarkovDecisionProcess as MDP,
    State,
    Transition,
    Callable,
)


def stubborn_sets(
    mdp: MDP, s: State, t: Transition = None
) -> list[Transition]:
    """Algorithm 3 from [godefroid1996]"""
    # 1. Take one transition t that is enabled in s.
    if t is None or not t.is_enabled(s):
        t = mdp.enabled_take_one(s)
    if t is None:
        return []

    # Let Ts = {t}.
    Ts = [t]

    def add_t(condition: Callable[[Transition], bool]):
        for t in mdp.transitions:
            if t in Ts:
                continue
            if condition(t):
                Ts.append(t)

    # 2. For all transitions t in Ts
    for t1 in Ts:
        # (a) if t is disabled in s, either
        if not t1.is_enabled(s):
            # i. choose a process Pj ∈ active(t) such that s(j) != (pre(t) ∩ Pj)
            Pj = __choose_process(s, t1)
            if Pj is not None:
                # then, add to Ts all transitions t' such that (pre(t) ∩ Pj) ∈ post(t')
                add_t(__cond_enabled_in(t1, Pj))
                continue
            # ii. choose a condition cj in the guard G of t that evaluates to false in s
            cj = __choose_condition(s, t1)
            if cj is not None:
                # then, for all operations op used by t to evaluate cj, add to Ts
                # all transitions t' such that there exists op' ∈ used(t') : op and op'
                # can-be-dependent
                add_t(__cond_op_dependent(cj))
        # (b) if t is enabled in s
        else:
            # add to Ts all transitions t' such that t and t' are in conflict or
            # parallel and their operations do-not-accord
            add_t(__cond_dependent(t1))

    # Return all transitions in Ts that are enabled in s
    return list(filter(lambda t: t.is_enabled(s), Ts))


def __choose_process(s: State, t: Transition) -> MDP:
    """Choose a process Pj ∈ active(t) such that s(j) != (pre(t) ∩ Pj)"""
    return next(
        filter(lambda p: {s(p)} != t.pre.s.intersection(p.states), t.active),
        None,
    )


def __choose_condition(s: State, t: Transition) -> Op:
    """Choose a condition cj in the guard G of t that evaluates to false in s"""
    return next(filter(lambda cj: not cj(s.ctx), t.guard.used()), None)


def __cond_enabled_in(t1: Transition, p: MDP) -> Callable[[Transition], bool]:
    """(pre(t) ∩ Pj) ∈ post(t')"""
    return lambda t2: t1.pre.s.intersection(p.states) in t2.post


def __cond_op_dependent(op1: Op) -> Callable[[Transition], bool]:
    """For all operations op used to evaluate cj, add all transitions t'
    such that there exists op' ∈ used(t') : op and op' can-be-dependent
    """
    return lambda t2: any(op1.can_be_dependent(op2) for op2 in t2.used())


def __cond_dependent(t1: Transition) -> Callable[[Transition], bool]:
    """t and t' are in conflict or parallel and their operations do-not-accord"""
    return lambda t2: t1.in_conflict(t2) or (
        t1.is_parallel(t2)
        and t1.can_be_dependent(t2)  # TODO implement do-not-accord
    )
