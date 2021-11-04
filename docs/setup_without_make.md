# Setup without `make`


## Virtual environment (Recommended)

Setup a virtual environment with the following command:

```console
py -m venv env
```

Activate the environment with:

```console
.\env\Scripts\activate
```


## Developer tools

Install the package in development mode, as well as all development dependencies, such as `pytest`, `pytest-cov`, and `black`:

```console
./init.bat
```

Before you commit and push your changes, format the code by calling:

```console
py -m black . --line-length 79
```

Preferably, setup your editor to automatically format on save using `black`. For vscode [see below](#vscode-recommended-workspace-files).


## Testing

Run all tests with `pytest` and generate coverage reports:

```console
py -m pytest -v --cov=mdptools tests/
```


## \[vscode\] Recommended workspace files

To add the recommended workspace files as seen in the [README](../README.md#workspace-settings), run the following command:

```console
py -m vscode
```

This will overwrite any changes you've made to either `launch.json` or `settings.json`.
