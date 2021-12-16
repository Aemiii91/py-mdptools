# pylint: disable=cell-var-from-loop
from argparse import ArgumentParser
from typing import Any, Callable
import pandas as pd
from time import perf_counter

from mdptools import MarkovDecisionProcess as MDP, stubborn_sets, pr_max

from sensor_system import make_system


pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)
pd.set_option("display.width", None)
pd.set_option("display.max_colwidth", None)
pd.set_option("precision", 4)


goal_states = {"failed"}

experiments: dict[str, Callable[[MDP], MDP]] = {
    "orig": lambda m: m,
    "red": lambda m: MDP(*m.processes, set_method=stubborn_sets),
    "goal": lambda m: MDP(
        *m.processes, set_method=stubborn_sets, goal_states=goal_states
    ),
}


def time_execution(func: Callable) -> tuple[Any, int]:
    t_start = perf_counter()
    result = func()
    t_stop = perf_counter()
    ms = int(round((t_stop - t_start) * 1000))
    return (result, ms)


def test_system(n: int) -> dict:
    result = {"sensors": n}

    m = make_system(n)
    comp = None

    for name, func in experiments.items():
        test_case = func(m)

        state_space, gen_time = time_execution(
            lambda: list(test_case.search(silent=True))
        )
        result[name] = len(state_space)
        result[f"{name}_t"] = gen_time

        if comp is None:
            comp = result[name]
        else:
            result[f"{name}_r"] = round(abs(comp - result[name]) / comp, 4)

        result[f"{name}_pr"], result[f"{name}_pr_t"] = time_execution(
            lambda: pr_max(
                test_case, goal_states=goal_states, state_space=state_space
            )
        )

    return result


def main(args):
    data = []
    first_write = True

    if args.outfile:
        print(f"Writing result to '{args.outfile}'.\n")

    for n in range(1, args.sensor_count + 1):
        result = test_system(n)
        data.append(result)
        df = pd.DataFrame([result])
        if first_write:
            print(df.to_string(index=False))
            if args.outfile:
                df.to_csv(args.outfile)
            first_write = False
        else:
            print("\n".join(df.to_string(index=False).split("\n")[1:]))
            if args.outfile:
                df.to_csv(args.outfile, mode="a", header=False)


parser = ArgumentParser()
parser.add_argument("--sensor_count", "-s", type=int, default=5)
parser.add_argument("--outfile", "-o", type=str, default="")
main(parser.parse_args())
