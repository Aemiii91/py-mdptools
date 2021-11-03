ifeq ($(OS),Windows_NT)
    OPEN := start
else
    UNAME := $(shell uname -s)
    ifeq ($(UNAME),Linux)
        OPEN := xdg-open
    endif
endif


install:
	python3 -m pip install .

env:
	python3 -m venv env
	
init:
	python3 -m pip install --upgrade pip
	python3 -m pip install -r requirements.txt
	python3 -m pip install -e . --no-deps

vscode:
	python3 -m vscode

test:
	python3 -m pytest -v --cov-report=xml --cov=mdptools tests/

coverage:
	python3 -m pytest -q --cov-report=html --cov=mdptools tests/
	$(OPEN) htmlcov/index.html &

format:
	python3 -m black . --line-length 79

clean:
	git clean -fdx
