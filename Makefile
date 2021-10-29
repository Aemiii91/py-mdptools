install:
	python3 setup.py install

env:
	python3 -m venv env
	
init:
	pip install --upgrade pip
	pip install -r requirements.txt
	pip install -e . --no-deps

vscode:
	mkdir -p .vscode
	touch .vscode/settings.json
	touch .vscode/launch.json

test:
	pytest -v --cov-report=xml --cov=mdptools tests/

format:
	black . --line-length 79

clean:
	git clean -fdx
