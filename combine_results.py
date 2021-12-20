import pandas as pd
import os
from argparse import ArgumentParser

from mdptools.utils import write_file


def main(files: list[str], outfile: str):
    combined_data = []

    for file_path in files:
        name, _, _ = os.path.basename(file_path).rpartition("_")
        for scale, df in pd.read_csv(file_path).groupby("scale"):
            df["name"] = f"{name}_{scale:02}"
            combined_data.append(df)

    df = pd.concat(combined_data)
    df = pd.DataFrame(df.groupby(["test_system", "name"]).max())
    df = pd.concat([df.reset_index()])

    df["total_time"] = df[["gen_time", "con_time", "check_time"]].sum(axis=1)

    reduction = []
    for _, row in df.iterrows():
        name = row["name"]
        before = df["states"][df["test_system"] == "components"][
            df["name"] == name
        ].values[0]
        after = row["states"]
        result = after
        result = (before - after) / before if before > 0 else 0.0
        reduction.append(result)
    df["reduction"] = reduction

    for column in [
        "states",
        "result",
        "check_time",
        "total_time",
        "reduction",
    ]:
        df_column = transpose_on_column(df, column)
        print("::", column)
        if outfile:
            df_column.to_csv(f"{outfile}_{column}.csv", index=False)
            tex = df_to_tex(df_column)
            write_file(f"{outfile}_{column}.tex", tex)
        else:
            print(df_column.to_string(index=False))

    if outfile:
        df.to_csv(f"{outfile}.csv", index=False)
    else:
        print(df)


def transpose_on_column(df: pd.DataFrame, column: str) -> pd.DataFrame:
    data = []
    for name, df in df.groupby("name"):
        df = df.reset_index().set_index("test_system")
        df = df[[column]].transpose()
        df["name"] = name
        data.append(df)
    df = pd.concat(data).reset_index()[
        ["name", "components", "with_goal", "reduced"]
    ]
    return df


def df_to_tex(df: pd.DataFrame) -> str:
    buffer = []

    for _, row in df.iterrows():
        s = f"\\textit{{{format_name(row['name'])}}}"
        s += f" & {tex_number(row['components'])}"
        s += f" & {tex_number(row['with_goal'])}"
        s += f" & {tex_number(row['reduced'])}"
        s += " \\\\"
        buffer.append(s)

    return "\n".join(buffer)


def format_name(s: str) -> str:
    return s.replace("_", "\\_")


def tex_number(n: float) -> str:
    return f"${round(n, 4):,}$".replace(",", "\\,")


if __name__ == "__main__":
    pd.set_option("display.max_rows", None)
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", None)
    pd.set_option("display.max_colwidth", None)
    pd.set_option("precision", 4)

    parser = ArgumentParser()
    parser.add_argument("files", type=str, nargs="+")
    parser.add_argument("--outfile", "-o", type=str, default="")

    args = parser.parse_args()

    main(args.files, args.outfile)
