check-lint:
	. venv/bin/activate && (isort --check .; black --check .; flake8 .; mypy)

lint:
	. venv/bin/activate && (isort .; black .; flake8 .; mypy)

test:
	. venv/bin/activate && pytest

run-dev:
	. venv/bin/activate && uvicorn lta.api.app:app --port 8123 --reload
