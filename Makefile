# WERKBANK — Entwickler-Toolchain
#
# Schnellstart:
#   make dev-setup   Dev-Tools installieren (ruff, mypy, coverage, bandit, pytest)
#   make check       Lokales Pre-Push-Set: lint + type + sast + test (schnell)
#   make all         check + harter Gate-Lauf (werkbank_self)
#
# Das Framework selbst ist stdlib-only; die Tools hier sind dev-only.

.DEFAULT_GOAL := help

PROFILE ?= werkbank_self
TEST_DIR := gates/checks/tests
TEST_PATTERN := test_*.py

.PHONY: help dev-setup test lint type sast cover gate check all

help:
	@echo "WERKBANK make-Ziele:"
	@echo "  dev-setup  Dev-Tools installieren (requirements-dev.txt)"
	@echo "  test       Unittests (discover)"
	@echo "  lint       ruff check ."
	@echo "  type       mypy gates"
	@echo "  sast       bandit (Medium+; Test-Fixtures ausgeschlossen)"
	@echo "  cover      coverage run + report"
	@echo "  gate       harter Gate-Lauf, Profil $(PROFILE)"
	@echo "  check      lint + type + sast + test (Pre-Push)"
	@echo "  all        check + gate"

dev-setup:
	pip install -r requirements-dev.txt

test:
	python3 -m unittest discover -s $(TEST_DIR) -p "$(TEST_PATTERN)"

lint:
	ruff check .

type:
	mypy gates

sast:
	bandit -r gates -q --severity-level medium -x gates/checks/tests

cover:
	coverage run -m unittest discover -s $(TEST_DIR) -p "$(TEST_PATTERN)" && coverage report

gate:
	python3 gates/runner.py --target . --report GATE-REPORT.md --profile $(PROFILE) --ci

check: lint type sast test

all: check gate
