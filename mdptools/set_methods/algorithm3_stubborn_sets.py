from mdptools.utils.utils import ordered_state_str
from ..model.commands import Op
from ..types import (
    MarkovDecisionProcess as MDP,
    State,
    Transition,
    Callable,
)
from ..utils import (
    highlight as _h,
    logger,
    log_info_enabled,
    ordered_state_str,
)


def stubborn_sets(
    mdp: MDP, s: State, t: Transition = None
) -> list[Transition]:
    """Algorithm 3 from [godefroid1996]"""
    # 1. Take one transition t that is enabled in s.
    if t is None or not t.is_enabled(s):
        t = mdp.enabled_take_one(s)

    # Let Ts = {t}.
    Ts = [t]

    if log_info_enabled():
        logger.info(
            "[Stubborn sets]\n  s = {%s}:\n  Ts = {<%s>}",
            ordered_state_str(s, mdp, ",", lambda st: _h(_h.state, st)),
            t,
        )

    def add_t(condition: Callable[[Transition], bool]):
        for t in mdp.transitions:
            if t in Ts:
                continue
            if condition(t):
                if log_info_enabled():
                    logger.info("     +  <%s> (%s)", t, condition.__name__)
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
    T = list(filter(lambda t: t.is_enabled(s), Ts))

    if log_info_enabled():
        logger.info("  T = {<%s>}", ">,\n       <".join(map(str, T)))

    return T


def __choose_process(s: State, t: Transition) -> MDP:
    """Choose a process Pj ∈ active(t) such that s(j) != (pre(t) ∩ Pj)"""
    return next(
        filter(lambda p: {s(p)} != t.pre.intersection(p), t.active),
        None,
    )


def __choose_condition(s: State, t: Transition) -> frozenset[Op]:
    """Choose a condition cj in the guard G of t that evaluates to false in s"""
    return next(
        filter(lambda cj: not any(pred(s.ctx) for pred in cj), t.guard.expr),
        None,
    )


def __cond_enabled_in(t1: Transition, p: MDP) -> Callable[[Transition], bool]:
    """(pre(t) ∩ Pj) ∈ post(t')"""
    condition = lambda t2: t1.pre.intersection(p) in [s_ for s_, _ in t2.post]
    condition.__name__ = f"enables <{_h(_h.action, t1.action)}> [rule a.i]"
    return condition


def __cond_op_dependent(cj: frozenset[Op]) -> Callable[[Transition], bool]:
    """For all operations op used to evaluate cj, add all transitions t'
    such that there exists op' ∈ used(t') : op and op' can-be-dependent
    """
    condition = lambda t2: any(
        op1.can_be_dependent(op2) for op1 in cj for op2 in t2.used()
    )
    condition.__name__ = "dependent on ({cj}) [rule a.ii]"
    return condition


def __cond_dependent(t1: Transition) -> Callable[[Transition], bool]:
    """t and t' are in conflict or parallel and their operations do-not-accord"""
    condition = lambda t2: t1.in_conflict(t2) or (
        t1.is_parallel(t2)
        and t1.can_be_dependent(t2)  # TODO implement do-not-accord
    )
    condition.__name__ = (
        f"dependent with <{_h(_h.action, t1.action)}> [rule b]"
    )
    return condition
