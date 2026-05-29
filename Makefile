.PHONY: help install test coverage run docker-build docker-run clean

PYTHON ?= python3
CUSTOMERS ?= customers.csv
SUBSCRIPTIONS ?= subscriptions.csv
OUTPUT ?= output.json
IMAGE ?= utilus-analytics

help:
	@echo "Available targets:"
	@echo "  make install        Install Python dependencies"
	@echo "  make test           Run pytest"
	@echo "  make coverage       Run pytest with coverage report"
	@echo "  make run            Run CLI using CUSTOMERS, SUBSCRIPTIONS, and OUTPUT"
	@echo "  make docker-build   Build Docker image"
	@echo "  make docker-run     Run CLI in Docker using current directory as /app"
	@echo "  make clean          Remove local generated output and caches"

install:
	$(PYTHON) -m pip install -r requirements.txt

test:
	PYTHONPYCACHEPREFIX=/private/tmp/utilus_pycache $(PYTHON) -m pytest -q

coverage:
	PYTHONPYCACHEPREFIX=/private/tmp/utilus_pycache $(PYTHON) -m pytest --cov=utilus_analytics --cov-report=term-missing

run:
	PYTHONPYCACHEPREFIX=/private/tmp/utilus_pycache $(PYTHON) main.py $(CUSTOMERS) $(SUBSCRIPTIONS) $(OUTPUT)

docker-build:
	docker build -t $(IMAGE) .

docker-run:
	docker run --rm -v "$$(pwd):/app" $(IMAGE) $(CUSTOMERS) $(SUBSCRIPTIONS) $(OUTPUT)

clean:
	rm -rf .pytest_cache htmlcov .coverage output.json
