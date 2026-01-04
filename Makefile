name := ctool
version := $(shell cd src &> /dev/null && python -c 'from $(name).__version__ import VERSION; print(VERSION)')

sdist := dist/$(name)-$(version).tar.gz
wheel := dist/$(name)-$(version)-py3-none-any.whl

sources := $(wildcard src/$(name)/*)

venv := .venv
vpy := .venv/bin/python

byproducts := build src/$(name).egg-info .mypy_cache .pytest_cache $(venv) coverage.json
products := dist


PYTHON ?= $(shell which python3 || which python)

.PHONY: build
build: dist wheel

.PHONY: dist
dist: $(sdist)

.PHONY: wheel
wheel: $(wheel)

.PHONY: venv
venv: $(venv)/created

$(venv)/created: requirements.txt dev-requirements.txt
	@rm -rf $(venv)
	@$(PYTHON) -m venv $(venv)
	@$(vpy) -m pip install -r requirements.txt
	@$(vpy) -m pip install -r requirements.txt -r dev-requirements.txt
	@$(vpy) -m pip install -e .
	@touch $(venv)/created

$(sdist): $(sources) pyproject.toml setup.py
	@$(PYTHON) -m build --sdist

$(wheel): $(sdist)
	@$(PYTHON) -m build --wheel

.PHONY: clean
clean:
	rm -rf $(products) $(byproducts)

.PHONY: test
test: venv
	@$(vpy) -m pytest

.PHONY: format
format: venv
	@$(vpy) -m isort src
	@$(vpy) -m black src

.PHONY: lint
lint: | pylint flake8 mypy

.PHONY: pylint
pylint: venv
	-@$(vpy) -m pylint src

.PHONY: flake8
flake8: venv
	-@$(vpy) -m flake8 src

.PHONY: mypy
mypy: venv
	-@$(vpy) -m mypy src

.PHONY: coverage
coverage: venv
	@$(vpy) -m coverage erase
	@$(vpy) -m coverage run --module pytest
	@$(vpy) -m coverage report --show-missing
	@$(vpy) -m coverage json
