# mdptools

[![pytest](https://github.com/mholdg16/py-mdptools/actions/workflows/pytest.yml/badge.svg)](https://github.com/mholdg16/py-mdptools/actions/workflows/pytest.yml)
[![codecov](https://codecov.io/gh/mholdg16/py-mdptools/branch/master/graph/badge.svg?token=2ONO8MQDHT)](https://codecov.io/gh/mholdg16/py-mdptools)
[![black](https://github.com/mholdg16/py-mdptools/actions/workflows/black.yml/badge.svg)](https://github.com/mholdg16/py-mdptools/actions/workflows/black.yml)

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

Preferably, setup your editor to automatically format on save using `black`. For vscode [see below](#workspace-settings).


### Testing

Run all tests with `pytest` and generate coverage reports:

    make test


### [vscode] Recommended workspace files

#### Workspace settings

`.vscode/settings.json`

```jsonc
{
    // Enable pytest integration
    "python.testing.pytestArgs": [
        "tests"
    ],
    "python.testing.unittestEnabled": false,
    "python.testing.pytestEnabled": true,
    // Auto formatting
    "python.formatting.provider": "black",
    "python.formatting.blackArgs": [
        "--line-length",
        "79"
    ],
    "editor.formatOnSave": true,
    // Hide unused files and folders
    "files.exclude": {
        "env/": true,
        "build/": true,
        "dist/": true,
        "**/__pycache__": true,
        ".pytest_cache": true,
        "mdptools.egg-info": true,
        ".coverage": true,
        "coverage.xml": true
    }
}
```


#### Run and debug

`.vscode/launch.json`

```jsonc
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Run example",
            "type": "python",
            "request": "launch",
            "module": "run",
            "args": [
                "<EXAMPLE>"
            ],
        }
    ]
}
```

Replace `<EXAMPLE>` with the name of the example script to debug (without '`.py`').
