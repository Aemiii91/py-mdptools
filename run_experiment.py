import sys
import importlib
from argparse import ArgumentParser
from typing import Any, Callable
import pandas as pd
from time import perf_counter
from threading import Lock
from concurrent.futures import ThreadPoolExecutor

from mdptools import MarkovDecisionProcess as MDP, stubborn_sets, pr_max
from mdptools.types import StateDescription


def main():
    sys.path.append("./experiments")

    parser = ArgumentParser()
    parser.add_argument("experiment", type=str)
    parser.add_argument("--scale_from", "-f", type=int, default=1)
    parser.add_argument("--scale_to", "-t", type=int, default=3)
    parser.add_argument("--step", "-s", type=int, default=1)
    parser.add_argument("--outfile", "-o", type=str, default="")
    parser.add_argument("--workers", "-w", type=int, default=8)
    args = parser.parse_args()

    pd.set_option("display.max_rows", None)
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", None)
    pd.set_option("display.max_colwidth", None)
    pd.set_option("precision", 4)

    experiment = importlib.import_module(args.experiment)
    generate_system, generate_goal_states = experiment.export()

    test_range = range(args.scale_from, args.scale_to + 1, args.step)

    if args.outfile:
        print(f"Writing result to '{args.outfile}'.\n")

    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        for n in test_range:
            mdp = generate_system(n)
            goal_states = generate_goal_states(n)
            for name, test_case in test_cases(mdp, goal_states):
                result = {"test_system": name, "scale": n}
                t_args = (test_case, goal_states, result, args.outfile)
                executor.submit(run_experiment, *t_args)


def test_cases(mdp: MDP, goal_states: set[StateDescription]):
    ret: list[tuple[str, MDP]] = [
        ("original", mdp),
        ("reduced", MDP(*mdp.processes, set_method=stubborn_sets)),
    ]

    if goal_states:
        m = MDP(
            *mdp.processes,
            set_method=stubborn_sets,
            goal_states=goal_states,
        )
        ret += [("with_goal", m)]

    return ret


def run_experiment(
    mdp: MDP, goal_states: set[StateDescription], result: dict, outfile: str
):
    state_space, gen_time = time_execution(
        lambda: list(mdp.search(silent=True))
    )

    result["states"] = len(state_space)
    result["gen_time"] = gen_time

    if goal_states:
        result["pr_max"], result["pr_time"] = time_execution(
            lambda: pr_max(
                mdp, goal_states=goal_states, state_space=state_space
            )
        )

    write_result(result, outfile)


def time_execution(func: Callable) -> tuple[Any, int]:
    t_start = perf_counter()
    result = func()
    t_stop = perf_counter()
    seconds = round(t_stop - t_start, 3)
    return (result, seconds)


_first_write = True
_write_lock = Lock()


def write_result(result: dict, outfile: str):
    global _first_write

    df = pd.DataFrame([result])

    with _write_lock:
        if _first_write:
            print(df.to_string(index=False))
        else:
            print("\n".join(df.to_string(index=False).split("\n")[1:]))

        if outfile:
            df.to_csv(
                outfile,
                mode="w" if _first_write else "a",
                index=False,
                header=_first_write,
            )

    _first_write = False


if __name__ == "__main__":
    main()
