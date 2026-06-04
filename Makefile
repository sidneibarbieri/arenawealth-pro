PYTHON ?= .venv/bin/python
PIP ?= .venv/bin/pip
UVICORN ?= .venv/bin/uvicorn

.PHONY: setup verify verify-e2e metrics recommendation price-backtest experiments ai-advisor-audit configure-env api ui app run paper all package clean

setup:
	python3.11 -m venv .venv
	$(PIP) install -e ".[dev]"
	cd frontend && npm install

verify:
	bash scripts/verify.sh

verify-e2e:
	cd frontend && npm run test:e2e

metrics:
	$(PYTHON) scripts/reviewer_metrics.py

recommendation:
	$(PYTHON) scripts/moat_compounding_analysis.py --cash 1511.18

price-backtest:
	$(PYTHON) scripts/price_backtest.py --start 2021-01-01 --benchmark SPY

experiments:
	$(PYTHON) scripts/run_experiments.py

ai-advisor-audit:
	$(PYTHON) scripts/run_ai_advisor_audit.py --reference

configure-env:
	bash scripts/configure_env.sh

api:
	$(UVICORN) arenawealth.api.main:app --host 127.0.0.1 --port 8000 --reload

ui:
	cd frontend && npm run dev -- --host 127.0.0.1

app:
	bash scripts/start.sh

run:
	bash scripts/start.sh

paper:
	cd paper && latexmk -pdf main.tex

all: setup verify experiments ai-advisor-audit paper
	@echo "Artifact reproduced end-to-end: tests, figures, and PDF are up to date."

package:
	bash scripts/package_artifact.sh

clean:
	rm -rf .pytest_cache .ruff_cache frontend/dist frontend/test-results frontend/playwright-report exports logs
	find . -name '__pycache__' -type d -prune -exec rm -rf {} +
