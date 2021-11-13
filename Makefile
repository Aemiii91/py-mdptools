ifeq ($(OS),Windows_NT)
    OPEN := start
	PYTHON := py
else
    UNAME := $(shell uname -s)
    ifeq ($(UNAME),Linux)
        OPEN := xdg-open
		PYTHON := python3
    endif
endif


EXAMPLES := all


run:
	$(PYTHON) -m run -c -v $(EXAMPLES)

install:
	$(PYTHON) -m pip install .

env:
	$(PYTHON) -m venv env
	
init:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r requirements.txt
	$(PYTHON) -m pip install -e . --no-deps

vscode:
	$(PYTHON) -m vscode

test:
	$(PYTHON) -m pytest -v --cov-report=xml --cov=mdptools tests/

coverage:
	$(PYTHON) -m pytest -q --cov-report=html --cov=mdptools tests/
	$(OPEN) htmlcov/index.html &

format:
	$(PYTHON) -m black . --line-length 79

clean:
	git clean -fdx
