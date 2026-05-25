PYTHON ?= .venv/bin/python
PIP ?= .venv/bin/pip
UVICORN ?= .venv/bin/uvicorn

.PHONY: setup verify verify-e2e metrics recommendation price-backtest configure-env api ui app run paper clean

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

clean:
	rm -rf .pytest_cache .ruff_cache frontend/dist frontend/test-results frontend/playwright-report exports logs
	find . -name '__pycache__' -type d -prune -exec rm -rf {} +
