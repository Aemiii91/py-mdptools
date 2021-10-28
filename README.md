# py-mdptools

[![pytest](https://github.com/mholdg16/py-mdptools/actions/workflows/pytest.yml/badge.svg)](https://github.com/mholdg16/py-mdptools/actions/workflows/pytest.yml)
[![codecov](https://codecov.io/gh/mholdg16/py-mdptools/branch/master/graph/badge.svg?token=2ONO8MQDHT)](https://codecov.io/gh/mholdg16/py-mdptools)

A library containing tools for representing and manipulating Markov Decision Processes (MDP).

---

## Installation

Manually install the package with the command:

    make install

---

## Development

### Virtual environment (Recommended)

Setup a virtual environment with the following command:

    make env

Or, if you're on Windows:

    make env-win


### Developer tools

Install the package in development mode, as well as all development dependencies, such as `pytest`, `pytest-cov`, and `black`:

    make init

After any edits you can format the code by calling:

    make format

Or more preferably, setup your editor to automatically format on save using `black`.


### Testing

Run all tests with `pytest` and generate coverage reports:

    make test