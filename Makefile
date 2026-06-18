PYTHON ?= .venv/bin/python
PIP ?= .venv/bin/pip
UVICORN ?= .venv/bin/uvicorn
UV_CACHE_DIR ?= .uv-cache

.PHONY: setup verify verify-e2e metrics recommendation price-backtest experiments ai-advisor-audit bibliography advisor-budget collect-advisor-runs verify-data repro-docker configure-env api ui app run paper all package clean

setup:
	python3.11 -m venv .venv
	if command -v uv >/dev/null 2>&1; then \
		UV_CACHE_DIR=$(UV_CACHE_DIR) uv pip install --python .venv/bin/python -e ".[dev]"; \
	else \
		.venv/bin/python -m ensurepip --upgrade; \
		.venv/bin/python -m pip install -e ".[dev]"; \
	fi
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

bibliography:
	$(PYTHON) scripts/manage_bibliography.py

advisor-budget:
	$(PYTHON) scripts/estimate_advisor_budget.py --runs 3

collect-advisor-runs:
	$(PYTHON) scripts/collect_advisor_runs.py --runs 3

verify-data:
	$(PYTHON) scripts/hash_data.py

repro-docker:
	docker build -f Dockerfile.repro -t arenawealth-repro .
	docker run --rm arenawealth-repro

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
