from random import random
from typing import Callable
from mdptools import MarkovDecisionProcess as MDP


def export() -> tuple[Callable, ...]:
    p_values = random_register()
    return (
        lambda n: make_system(n, p_values),
        lambda _: {"count_0"},
        lambda _: "Pmax=? [F p0=0]",
    )


def make_system(n: int, p_values: Callable[[int], float]) -> MDP:
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
    return MDP(hand, *coins)


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


def random_register() -> Callable:
    p_values = []

    def get_random(i: int) -> float:
        nonlocal p_values

        if i > len(p_values) - 1:
            p_values += [
                random() * 0.8 + 0.1 for _ in range(i - len(p_values) + 1)
            ]

        return p_values[i]

    return get_random
