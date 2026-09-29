.PHONY: install test run lint clean

install:
	pip install -e ".[dev]"

test:
	pytest -q

run:
	python -m ark.experiments.runner --episodes 20

lint:
	ruff check src tests

clean:
	rm -rf .pytest_cache .ruff_cache dist build *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
