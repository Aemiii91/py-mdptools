import pandas as pd
import os
from argparse import ArgumentParser


def main(files: list[str], outfile: str):
    combined_data = []

    for file_path in files:
        name, _, _ = os.path.basename(file_path).rpartition("_")
        for scale, df in pd.read_csv(file_path).groupby("scale"):
            df: pd.DataFrame = (
                df[["test_system", "states"]]
                .set_index("test_system")
                .transpose()
            )
            df["name"] = f"{name}_{scale}"
            print(df)

    if outfile:
        df = pd.DataFrame(combined_data)
        df.to_csv(outfile)


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
