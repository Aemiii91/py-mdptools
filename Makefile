install:
	python3 -m pip install .

env:
	python3 -m venv env
	
init:
	python3 -m pip install --upgrade pip
	python3 -m pip install -r requirements.txt
	python3 -m pip install -e . --no-deps

vscode:
	mkdir -p .vscode
	touch .vscode/settings.json
	touch .vscode/launch.json

test:
	python3 -m pytest -v --cov-report=xml --cov=mdptools tests/

format:
	python3 -m black . --line-length 79

clean:
	git clean -fdx
