import sys
import importlib
from argparse import ArgumentParser
from typing import Any, Callable
import pandas as pd
from time import perf_counter
from threading import Lock
from concurrent.futures import ThreadPoolExecutor

from mdptools import MarkovDecisionProcess as MDP, stubborn_sets
from mdptools.utils import write_file, to_prism_components
from mdptools.types import StateDescription


SystemMaker = Callable[[int], tuple[MDP, set[StateDescription], str]]


def main(
    exp_name: str,
    n_from: int,
    n_to: int,
    step: int,
    outfile: str,
    workers: int,
    without_goal: bool,
):
    sys.path.append("./experiments")
    experiment = importlib.import_module(exp_name)
    make_system: SystemMaker = experiment.make_system

    prism_path = (
        lambda file_name: f"out/prism/{exp_name}/{exp_name}_{file_name}"
    )

    if outfile:
        print(f"Writing result to '{outfile}'.\n")

    with ThreadPoolExecutor(max_workers=workers) as executor:
        for n in range(n_from, n_to + 1, step):
            mdp, goal_states, prism_pf = make_system(n)
            test_goal = goal_states if not without_goal else None
            write_file(prism_path(f"{n}.props"), prism_pf)
            to_prism_components(mdp, prism_path(f"{n}_components.prism"))

            for name, test_case in test_cases(mdp, test_goal):
                result = {"test_system": name, "scale": n}
                prism_file = prism_path(f"{n}_{name}.prism")
                args = (test_case, result, outfile, prism_file)
                executor.submit(run_experiment, *args)


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


write_lock = Lock()


def run_experiment(
    mdp: MDP,
    result: dict,
    outfile: str,
    prism_file: str,
):
    (prism_code, state_space), gen_time = time_execution(
        lambda: list(mdp.to_prism())
    )

    result["states"] = len(state_space)
    result["gen_time"] = gen_time

    with write_lock:
        write_file(prism_file, prism_code)
        write_result(result, outfile)


def time_execution(func: Callable) -> tuple[Any, int]:
    t_start = perf_counter()
    result = func()
    t_stop = perf_counter()
    seconds = round(t_stop - t_start, 3)
    return (result, seconds)


first_write = True


def write_result(result: dict, outfile: str):
    global first_write

    df = pd.DataFrame([result])

    if first_write:
        print(df.to_string(index=False))
    else:
        print("\n".join(df.to_string(index=False).split("\n")[1:]))

    if outfile:
        df.to_csv(
            outfile,
            mode="w" if first_write else "a",
            index=False,
            header=first_write,
        )

    first_write = False


if __name__ == "__main__":
    pd.set_option("display.max_rows", None)
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", None)
    pd.set_option("display.max_colwidth", None)
    pd.set_option("precision", 4)

    parser = ArgumentParser()
    parser.add_argument("experiment", type=str)
    parser.add_argument("--scale_from", "-f", type=int, default=1)
    parser.add_argument("--scale_to", "-t", type=int, default=3)
    parser.add_argument("--step", "-s", type=int, default=1)
    parser.add_argument("--outfile", "-o", type=str, default="")
    parser.add_argument("--workers", "-w", type=int, default=8)
    parser.add_argument("--without_goal", action="store_true")

    args = parser.parse_args()

    main(
        args.experiment,
        args.scale_from,
        args.scale_to,
        args.step,
        args.outfile,
        args.workers,
        args.without_goal,
    )
