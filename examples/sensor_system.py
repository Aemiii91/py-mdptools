import re
import subprocess
import pandas as pd
import math
from tqdm import tqdm
from typing import Pattern, Type, Iterable
from dataclasses import dataclass
from os import path
from itertools import chain, combinations, product

from mdptools import MarkovDecisionProcess as MDP
from mdptools.utils import to_prism, to_prism_components
from mdptools.types import StateDescription
from mdptools.set_methods import stubborn_sets


def make_system(n: int) -> tuple[MDP, set[StateDescription], str]:
    sensors = [make_sensor(i) for i in range(1, n + 1)]
    device = make_device(n)
    return (MDP(device, *sensors), {"failed"}, "Pmax=? [F p0=3]")


def make_sensor(i: int) -> MDP:
    s = [f"active_{i}", f"prepare_{i}", f"detected_{i}", f"inactive_{i}"]
    return MDP(
        [
            (f"detect_{i}", s[0], {s[1]: 0.8, s[2]: 0.2}),
            (f"warn_{i}", s[1], s[2]),
            (f"shutdown_{i}", s[2], s[3]),
            ("tau", s[3]),
        ],
        init=s[0],
        name=f"S{i}",
    )


def make_device(n: int) -> MDP:
    s = ["running", "stopping", "off", "failed"]
    trs = list(
        chain.from_iterable(
            (
                (f"warn_{i}", s[0], s[1]),
                (f"shutdown_{i}", s[0], {s[2]: 0.9, s[3]: 0.1}),
                (f"shutdown_{i}", s[1], s[2]),
            )
            for i in range(1, n + 1)
        )
    )
    return MDP(trs + [("tau", s[2]), ("tau", s[3])], init=s[0], name="D")


@dataclass
class Result:
    goal_state: str
    prism_path: str
    props: str
    num_states: int
    reduction: float
    original: float = -1.0
    reduced: str = ""
    with_goal: str = ""


def main():
    m, _, _ = make_system(2)
    orig_state_space = list(m.search())
    orig_size = len(orig_state_space)

    results: list[Result] = []

    out_folder = "out/prism/sensor_system_goal"
    to_props = (
        lambda s: f"Pmax=? [F ({') | ('.join(' & '.join(ss) for ss in s)})]"
    )

    orig_path = path.join(out_folder, "_original.prism")
    to_prism_components(m, orig_path)

    reduced_path = path.join(out_folder, "_reduced.prism")
    to_prism(m, reduced_path, set_method=stubborn_sets)

    local_states = [p.states for p in m.processes]

    print("Generating prism files...")
    for goal_state in tqdm(all_combinations(local_states)):
        m_goal = MDP(
            *m.processes, goal_states={goal_state}, set_method=stubborn_sets
        )
        goal_str = "_".join(goal_state)
        prism_path = path.join(out_folder, f"{goal_str}.prism")

        _, state_space, goal_states = m_goal.to_prism(
            prism_path, convert_goal_states=True
        )

        props = to_props(goal_states)

        red_size = len(state_space)
        reduction = (orig_size - red_size) / orig_size

        result = Result(goal_str, prism_path, props, red_size, reduction)
        results.append(result)

    print("Running props on original system...")
    for result in tqdm(results):
        prism_orig = run_prism(orig_path, result.props)
        if prism_orig:
            result.original = prism_orig.result

    print("Running props on reduced system without goal states...")
    for result in tqdm(results):
        prism_orig = run_prism(reduced_path, result.props)
        if prism_orig:
            result.reduced = (
                "OK"
                if math.isclose(result.original, prism_orig.result)
                else "FAIL"
            )

    print("Running props on the reduced systems with goal states...")
    for result in tqdm(results):
        prism_result = run_prism(result.prism_path, result.props)
        if prism_result:
            result.with_goal = (
                "OK"
                if math.isclose(result.original, prism_result.result)
                else "FAIL"
            )

    df = pd.DataFrame(results)
    df = df[
        [
            "goal_state",
            "num_states",
            "reduction",
            "reduced",
            "with_goal",
        ]
    ]
    print(df)
    df.to_csv(path.join(out_folder, "result.csv"), index=False)


def all_combinations(it: Iterable):
    p = [(value,) for item in it for value in item]
    if len(it) <= 1:
        return p
    for n in range(2, len(it) + 1):
        for c in combinations(it, n):
            p += product(*c)
    return p


@dataclass
class PrismResult:
    num_states: int
    con_time: float
    result: float
    check_time: float


def run_prism(file_path: str, props: str) -> PrismResult:
    try:
        out = run_command(["prism", file_path, "-pf", props])
    except subprocess.CalledProcessError as e:
        print(e)
        return None
    return parse_result(out)


def run_command(args: list[str]) -> str:
    return subprocess.run(
        args, check=True, capture_output=True, text=True
    ).stdout


parse_components: dict[str, tuple[Pattern[str], Type]] = {
    "num_states": (re.compile(r"States:\s*(\d+)"), int),
    "con_time": (
        re.compile(r"Time for model construction: (\d+(?:\.\d+))"),
        float,
    ),
    "result": (re.compile(r"Result: (\d+(?:\.\d+)?(?:E[+-]\d+)?)"), float),
    "check_time": (
        re.compile(r"Time for model checking: (\d+(?:\.\d+))"),
        float,
    ),
}


def parse_result(result: str):
    return PrismResult(
        **{
            name: key(find_match(regex, result))
            for name, (regex, key) in parse_components.items()
        }
    )


def find_match(
    regex: Pattern[str], data: str, group: int = 1, fallback: str = ""
) -> str:
    match = regex.search(data)
    if match:
        return match.group(group)
    return fallback


if __name__ == "__main__":
    main()
