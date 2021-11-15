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

    _log_begin(mdp, s, t)

    def add_t(condition: Callable[[Transition], bool]):
        """Add t' to Ts if condition holds"""
        for t in mdp.transitions:
            if t in Ts:
                continue
            if condition(t):
                Ts.append(t)
                _log_append(t, condition)

    # 2. For all transitions t in Ts
    for t1 in Ts:
        # (a) if t is disabled in s, either
        if not t1.is_enabled(s):
            # i. choose a process Pj ∈ active(t) such that s(j) != (pre(t) ∩ Pj)
            Pj = _choose_process(s, t1)
            if Pj is not None:
                # then, add to Ts all transitions t' such that (pre(t) ∩ Pj) ∈ post(t')
                add_t(_cond_enabled_in(t1, Pj))
                continue
            # ii. choose a condition cj in the guard G of t that evaluates to false in s
            cj = _choose_condition(s, t1)
            if cj is not None:
                # then, for all operations op used by t to evaluate cj, add to Ts
                # all transitions t' such that there exists op' ∈ used(t') : op and op'
                # can-be-dependent
                add_t(_cond_op_dependent(cj))
        # (b) if t is enabled in s
        else:
            # add to Ts all transitions t' such that t and t' are in conflict or
            # parallel and their operations do-not-accord
            add_t(_cond_dependent(t1))

    # Return all transitions in Ts that are enabled in s
    T = list(filter(lambda t: t.is_enabled(s), Ts))

    _log_end(T)

    return T


def _choose_process(s: State, t: Transition) -> MDP:
    """Choose a process Pj ∈ active(t) such that s(j) != (pre(t) ∩ Pj)"""
    res = filter(lambda p: s(p) != t.pre(p), t.active)
    return next(res, None)


def _choose_condition(s: State, t: Transition) -> frozenset[Op]:
    """Choose a condition cj in the guard G of t that evaluates to false in s"""
    return next(
        filter(lambda cj: not any(pred(s.ctx) for pred in cj), t.guard.expr),
        None,
    )


def _cond_enabled_in(t1: Transition, p: MDP) -> Callable[[Transition], bool]:
    """(pre(t) ∩ Pj) ∈ post(t')"""
    condition = lambda t2: t1.pre.intersection(p) in [s_ for s_, _ in t2.post]
    condition.__name__ = (
        f"enables <{_h.action(t1.action)}> [{_h.error('rule a.i')}]"
    )
    return condition


def _cond_op_dependent(cj: frozenset[Op]) -> Callable[[Transition], bool]:
    """For all operations op used to evaluate cj, add all transitions t'
    such that there exists op' ∈ used(t') : op and op' can-be-dependent
    """
    condition = lambda t2: any(
        op1.can_be_dependent(op2) for op1 in cj for op2 in t2.used()
    )
    condition.__name__ = f"dependent on ({cj}) [{_h.error('rule a.ii')}]"
    return condition


def _cond_dependent(t1: Transition) -> Callable[[Transition], bool]:
    """t and t' are in conflict or parallel and their operations do-not-accord"""
    condition = lambda t2: t1.in_conflict(t2) or (
        t1.is_parallel(t2)
        and t1.can_be_dependent(t2)  # TODO implement do-not-accord
    )
    condition.__name__ = (
        f"dependent with <{_h.action(t1.action)}> [{_h.error('rule b')}]"
    )
    return condition


def _log_begin(mdp: MDP, s: State, t: Transition):
    if log_info_enabled():
        logger.info(
            "%s %s\n  s := {%s}:\n  Ts := {<%s>}",
            _h.comment("begin"),
            _h.function("stubborn_sets"),
            s.to_str(mdp, colors=True, wrap=True),
            t,
        )


def _log_append(t: Transition, condition: Callable[[Transition], bool]):
    if log_info_enabled():
        logger.info("     +  <%s> (%s)", t, condition.__name__)


def _log_end(T: list[Transition]):
    if log_info_enabled():
        logger.info(
            "\n  %s {<%s>}\n%s",
            _h.variable("return"),
            ">,\n          <".join(map(str, T)),
            _h.comment("end"),
        )
