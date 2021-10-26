import importlib
import mdp


def main(argc: int, argv: list[str]):
    mdp.use_colors()

    if argc == 2:
        test = importlib.import_module(f"tests.test_{argv[1]}")
        test.run()
    else:
        print('Please specify a test name to run.\n>> python3 main.py [test_name]')


if __name__ == '__main__':
    import sys
    main(len(sys.argv), sys.argv)