init:
	pip install -r requirements.txt

test:
	pytest -v --cov-report=xml --cov=mdptools tests/