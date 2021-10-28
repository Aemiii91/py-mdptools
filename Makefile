init:
	pip install -r requirements.txt

test:
	pytest -v --cov-report= --cov=mdptools tests/