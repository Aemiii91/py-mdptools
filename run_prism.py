import os
import re
import subprocess
from typing import Pattern, Type
import pandas as pd
from argparse import ArgumentParser


def main():
    parser = ArgumentParser()
    parser.add_argument("prism_folder", type=str)
    parser.add_argument("--property", "-pf", type=str, default="")
    parser.add_argument("--outfile", "-o", type=str, default="")
    args = parser.parse_args()

    pd.set_option("display.max_rows", None)
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", None)
    pd.set_option("display.max_colwidth", None)
    pd.set_option("precision", 4)

    prism_folder = args.prism_folder
    prism_files = [
        os.path.join(prism_folder, fn)
        for fn in os.listdir(prism_folder)
        if fn.endswith(".prism")
    ]
    prism_files = sorted(prism_files, key=lambda fn: os.stat(fn).st_size)

    dir_name = os.path.basename(prism_folder)
    print(f"Running prism on '{dir_name}' containing {len(prism_files)} files")

    def shell_args(file: str) -> list[str]:
        ret = ["prism", file]
        if args.property:
            ret += ["-pf", args.property]
        return ret

    for file in prism_files:
        name, _ = os.path.splitext(os.path.basename(file))
        name = name.replace(f"{dir_name}_", "")
        try:
            result = subprocess.run(
                shell_args(file), check=True, capture_output=True, text=True
            ).stdout
        except subprocess.CalledProcessError as e:
            print(e)
            continue

        parsed = {"test_system_name": name, **parse_result(result)}
        write_result(parsed, args.outfile)


parse_components: dict[str, tuple[Pattern[str], Type]] = {
    "states": (re.compile(r"States:\s*(\d+)"), int),
    "gen_time": (
        re.compile(r"Time for model construction: (\d+(?:\.\d+))"),
        float,
    ),
    "result": (re.compile(r"Result: (\d+(?:\.\d+)?)"), float),
    "check_time": (
        re.compile(r"Time for model checking: (\d+(?:\.\d+))"),
        float,
    ),
}


def parse_result(result: str):
    return {
        name: key(find_match(regex, result))
        for name, (regex, key) in parse_components.items()
    }


def find_match(
    regex: Pattern[str], data: str, group: int = 1, fallback: str = ""
) -> str:
    match = regex.search(data)
    if match:
        return match.group(group)
    return fallback


_first_write = True


def write_result(result: dict, outfile: str):
    global _first_write

    df = pd.DataFrame([result])

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
