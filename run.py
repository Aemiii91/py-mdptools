#!/usr/bin/env python3
import sys
from argparse import ArgumentParser, Namespace
import importlib
from mdptools import use_colors


def main(args: Namespace):
    sys.path.append('./examples')

    if args.colors:
        use_colors()

    importlib.import_module(args.example)


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('example', type=str, help='the name of the example to run')
    parser.add_argument('-c', '--colors', action='store_true', help='enable color output')

    main(parser.parse_args())
