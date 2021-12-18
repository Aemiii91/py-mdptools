from random import random

from mdptools import MarkovDecisionProcess as MDP
from mdptools.types import StateDescription


def make_system(n: int) -> tuple[MDP, set[StateDescription], str]:
    coins = [make_coin(i + 1, p_values(i)) for i in range(n)]
    hand = MDP(
        [("done", "count_0")]
        + [
            (f"flip_{i}", f"count_{c}", f"count_{c-1}")
            for i in range(n, 0, -1)
            for c in range(1, n + 1)
        ],
        name="H",
        init=(f"count_{n}"),
    )
    return (MDP(hand, *coins), {"count_0"}, "Pmax=? [F p0=0]")


def make_coin(i: int, p: float) -> MDP:
    return MDP(
        [
            (
                f"flip_{i}",
                f"unknown_{i}",
                {f"heads_{i}": round(p, 2), f"tails_{i}": round(1 - p, 2)},
            )
        ],
        name=f"C{i}",
    )


_p_values = []


def p_values(i: int) -> float:
    global _p_values

    if i > len(_p_values) - 1:
        _p_values += [
            random() * 0.8 + 0.1 for _ in range(i - len(_p_values) + 1)
        ]

    return _p_values[i]
