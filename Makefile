# Docker Whitelist, Build and Push
export PLATFORM_ARCHITECTURE=linux/amd64

# Python & tests
export PYTHON_VERSION?=3.12
export BEHAVE_TEST_FOLDER=test/bdd

.PHONY: env-%
env-%:
	@ if [ "${${*}}" = "" ];then echo "Missing environment variable $*";exit 1;fi

### Python scripts ###

# Path to the virtual environment python executable
VENV_PYTHON=.venv/bin/python

.PHONY: ensure-uv
ensure-uv:
	@command -v uv >/dev/null 2>&1 || { echo >&2 "uv is required but not installed. Install it via: curl -LsSf https://astral.sh/uv/install.sh | sh"; exit 1; }

# Target to check if venv exists and is up-to-date (simple check)
.venv/touchfile: pyproject.toml
	@echo "Creating/Updating virtual environment..."
	uv venv --python $(PYTHON_VERSION)
	@touch $@ # Create/update a marker file

.PHONY: venv
venv: .venv/touchfile # Depend on the marker file

.PHONY: install
install: ensure-uv venv # Ensure venv exists before installing
	@echo ">> Installing dependencies into .venv"
	uv pip install --python $(VENV_PYTHON) -e . # Use global uv, target .venv python

.PHONY: install-dev
install-dev: ensure-uv venv # Ensure venv exists before installing
	@echo ">> Installing development dependencies into .venv"
	uv pip install --python $(VENV_PYTHON) -e ".[dev]" # Use global uv, target .venv python

.PHONY: install-pre-commit
install-pre-commit: ensure-uv venv # Ensure venv exists before installing
	uv pip install --python $(VENV_PYTHON) pre-commit # Use global uv, target .venv python
	$(VENV_PYTHON) -m pre_commit install
	$(VENV_PYTHON) -m pre_commit run --all-files

.PHONY: ruff
ruff: ensure-uv venv # Ensure venv exists
	$(VENV_PYTHON) -m ruff check . --fix # Use ruff from the virtual env

.PHONY: format
format: ensure-uv venv # Ensure venv exists
	$(VENV_PYTHON) -m ruff format . # Use ruff from the virtual env

.PHONY: check
check: ensure-uv venv # Ensure venv exists
	$(VENV_PYTHON) -m ruff check . --fix # Use ruff from the virtual env
	$(VENV_PYTHON) -m mypy . # Use mypy from the virtual env

.PHONY: all-dev
all-dev: ruff format check test

### BDD and Unit Tests ###

.PHONY: test-bdd
test-bdd: ensure-uv install-dev # Ensure dev deps are installed
	@echo "Running BDD tests..."
	$(VENV_PYTHON) -m pytest $(BEHAVE_TEST_FOLDER) # Use pytest from the virtual env

.PHONY: test-unit
test-unit: ensure-uv install-dev # Ensure dev deps are installed
	$(VENV_PYTHON) -m pytest --cov=src tests/unit # Use pytest from the virtual env
	$(VENV_PYTHON) -m coverage report
	$(VENV_PYTHON) -m coverage html

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
	rm -rf .venv # Also clean the venv

.PHONY: run
run: ensure-uv install # Depend on install, which depends on venv
	$(VENV_PYTHON) run.py # Use python from the virtual env

.PHONY: build
build: clean
	mkdir -p dist
	cp -rf src/* dist/
	cd dist && zip -r package.zip .

.PHONY: help
help:
	@echo "Available commands:"
	@echo "  make venv          - Create/Update the virtual environment"
	@echo "  make install       - Install dependencies into .venv"
	@echo "  make install-dev   - Install development dependencies into .venv"
	@echo "  make format        - Format code using ruff from .venv"
	@echo "  make check         - Run linting and type checks using tools from .venv"
	@echo "  make test          - Run all tests using pytest from .venv"
	@echo "  make clean         - Clean up generated files and .venv"
	@echo "  make run           - Install deps if needed and run the application using python from .venv"
	@echo "  make build         - Build the package"
