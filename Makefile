UVX ?= uvx
VENV ?= env
VENV_PYTHON ?= python3
PROMPT ?= Hello from simple-agent!

VENV_BIN := $(VENV)/bin
VENV_ACTIVATE := source $(VENV_BIN)/activate
DEFAULT_PYTHON := $(if $(wildcard $(VENV_BIN)/python),$(VENV_BIN)/python,)

PYTHON ?= $(if $(DEFAULT_PYTHON),$(DEFAULT_PYTHON),$(UVX) python)
RUFF ?= $(UVX) ruff

.PHONY: venv run lint tools install clean

venv:
	$(VENV_PYTHON) -m venv $(VENV)
	@echo "Activate with: $(VENV_ACTIVATE)"

install:
	$(PYTHON) -m pip install -r requirements.txt

run:
	$(PYTHON) main.py "$(PROMPT)"

tools:
	$(PYTHON) main.py --list-tools

lint:
	$(RUFF) check simple_agent main.py

clean:
	rm -rf $(VENV) __pycache__ .ruff_cache
