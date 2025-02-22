# Docker Whitelist, Build and Push
export PLATFORM_ARCHITECTURE=linux/amd64

# Python & tests
export PYTHON_VERSION?=3.12
export BEHAVE_TEST_FOLDER=test/bdd

.PHONY: env-%
env-%:
	@ if [ "${${*}}" = "" ];then echo "Missing environment variable $*";exit 1;fi

### Python scripts ###

.PHONY: ensure-uv
ensure-uv:
	@command -v uv >/dev/null 2>&1 || { echo >&2 "uv is required but not installed. Install it via: curl -LsSf https://astral.sh/uv/install.sh | sh"; exit 1; }

.PHONY: venv
venv: ensure-uv
	@echo "Creating virtual environment..."
	uv venv
	@echo "Virtual environment created. Activate it with: source .venv/bin/activate"

.PHONY: install
install: ensure-uv
	@echo ">> Installing dependencies"
	uv pip install -e .

.PHONY: install-dev
install-dev: ensure-uv
	@echo ">> Installing development dependencies"
	uv pip install -e ".[dev]"

.PHONY: install-pre-commit
install-pre-commit: ensure-uv
	uv pip install pre-commit
	pre-commit install
	pre-commit run --all-files

.PHONY: ruff
ruff: ensure-uv
	ruff check . --fix

.PHONY: format
format: ensure-uv
	ruff format .

.PHONY: check
check: ensure-uv
	ruff check . --fix
	mypy .

.PHONY: all-dev
all-dev: ruff format check test

### BDD and Unit Tests ###

.PHONY: test-bdd
test-bdd: ensure-uv
	@echo "Running BDD tests..."
	pytest $(BEHAVE_TEST_FOLDER)

.PHONY: test-unit
test-unit: ensure-uv
	pytest --cov=src tests/unit
	coverage report
	coverage html

.PHONY: test
test: test-bdd test-unit

.PHONY: clean
clean:
	@echo "Cleaning up..."
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov
	rm -rf .mypy_cache
	rm -rf .ruff_cache
	rm -rf dist
	rm -rf build
	rm -rf *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +

.PHONY: run
run: ensure-uv
	python run.py

.PHONY: run-streamlit
run-streamlit:
ifeq ($(SHELL), /usr/bin/fish)
	PYTHONPATH=./src (pyenv which python) -m streamlit run src/application/frontend/streamlit_app.py --server.port 8502
else
	PYTHONPATH=./src $(shell pyenv which python) -m streamlit run src/application/frontend/streamlit_app.py --server.port 8502
endif

.PHONY: run-all
run-all:
	make run & make run-streamlit

.PHONY: build
build: clean
	mkdir -p dist
	cp -rf src/* dist/
	cd dist && zip -r package.zip .

.PHONY: help
help:
	@echo "Available commands:"
	@echo "  make venv          - Create a virtual environment"
	@echo "  make install       - Install dependencies"
	@echo "  make install-dev   - Install development dependencies"
	@echo "  make format        - Format code using ruff"
	@echo "  make check         - Run linting and type checks"
	@echo "  make test          - Run all tests"
	@echo "  make clean         - Clean up generated files"
	@echo "  make run           - Run the FastAPI application"
	@echo "  make build         - Build the package"
