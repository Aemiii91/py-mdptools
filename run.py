#!/usr/bin/env python3
import logging
import sys
from argparse import ArgumentParser, Namespace
import importlib
from mdptools import use_colors, set_logging_level


def main(args: Namespace):
    sys.path.append("./examples")

    if args.colors:
        use_colors()

    if args.verbose:
        set_logging_level(logging.INFO)

    importlib.import_module(args.example)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        "example", type=str, help="the name of the example to run"
    )
    parser.add_argument(
        "-c", "--colors", action="store_true", help="enable color output"
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="enable verbose logging output",
    )
    main(parser.parse_args())
