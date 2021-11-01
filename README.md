# mdptools

[![pytest](https://github.com/mholdg16/py-mdptools/actions/workflows/pytest.yml/badge.svg)](https://github.com/mholdg16/py-mdptools/actions/workflows/pytest.yml)
[![codecov](https://codecov.io/gh/mholdg16/py-mdptools/branch/master/graph/badge.svg?token=2ONO8MQDHT)](https://codecov.io/gh/mholdg16/py-mdptools)
[![black](https://github.com/mholdg16/py-mdptools/actions/workflows/black.yml/badge.svg)](https://github.com/mholdg16/py-mdptools/actions/workflows/black.yml)

A library containing tools for representing and manipulating Markov Decision Processes (MDP).


## Installation

Manually install the package with the command:

```console
make install
```


## Development

### Virtual environment (Recommended)

Setup a virtual environment with the following command:

```console
make env
```

Activate the environment with:

```console
source env/bin/activate
```

Or, if you're on Windows:

```console
.\env\Scripts\activate
```


### Developer tools

Install the package in development mode, as well as all development dependencies, such as `pytest`, `pytest-cov`, and `black`:

```console
make init
```

Before you commit and push your changes, format the code by calling:

```console
make format
```

Preferably, setup your editor to automatically format on save using `black`. For vscode [see below](#workspace-settings).


### Testing

Run all tests with `pytest` and generate coverage reports:

```console
make test
```


### [vscode] Recommended workspace files

To add the recommended workspace files as seen below, run the following command:

```console
make vscode
```

This will overwrite any changes you've made to either `launch.json` or `settings.json`.


#### Workspace settings

`.vscode/settings.json`

```jsonc
{
    // Enable pytest integration
    "python.testing.unittestEnabled": false,
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": [
        "tests"
    ],
    // Auto formatting
    "editor.formatOnSave": true,
    "python.formatting.provider": "black",
    "python.formatting.blackArgs": [
        "--line-length",
        "79"
    ],
    // Hide unused files and folders
    "files.exclude": {
        "**/__pycache__/": true,
        ".pytest_cache/": true,
        "build/": true,
        "dist/": true,
        "env/": true,
        "mdptools.egg-info/": true,
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

Replace `<EXAMPLE>` with the name of the example script you want to debug (located in the `examples` folder).
