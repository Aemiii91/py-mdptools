#!/usr/bin/env python3
import logging
import sys
from os import walk
from argparse import ArgumentParser, Namespace
import importlib
import math
from mdptools import use_colors, set_logging_level
from mdptools.utils import highlight as _h, get_terminal_width


EXAMPLE_DIR = "./examples"
LINE_WIDTH = get_terminal_width()


def main(args: Namespace):
    sys.path.append(EXAMPLE_DIR)

    if args.colors:
        use_colors()

    if args.verbose:
        set_logging_level(logging.INFO)

    examples = args.examples

    if len(examples) == 1 and examples[0] == "all":
        examples = map(
            lambda filename: filename[:-3],
            filter(
                lambda filename: filename.endswith(".py"),
                next(walk(EXAMPLE_DIR), (None, None, []))[2],
            ),
        )

    for example in examples:
        pad_left = int(math.floor((LINE_WIDTH - len(example)) / 2 - 2))
        pad_right = int(math.ceil((LINE_WIDTH - len(example)) / 2 - 2))
        print(_h.numeral("┌" + "─" * (LINE_WIDTH - 2) + "┐"))
        print(
            _h.numeral("│") + " " * pad_left,
            example,
            " " * pad_right + _h.numeral("│"),
        )
        print(_h.numeral("└" + "─" * (LINE_WIDTH - 2) + "┘"))
        importlib.import_module(example)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        "examples",
        type=str,
        nargs="+",
        help="the name(s) of the example(s) to run",
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
