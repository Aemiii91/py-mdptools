init:
	pip install -r requirements.txt
	pip install -e . --no-deps

test:
	pytest -v --cov-report=xml --cov=mdptools tests/

install:
	python3 setup.py install

env:
	python3 -m venv env
	source env/bin/activate

env-win:
	py -m venv env
	.\\env\\Scripts\\activate

format:
	black . --line-length 79