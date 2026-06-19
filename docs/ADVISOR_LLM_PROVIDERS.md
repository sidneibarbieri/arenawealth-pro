# Advisor LLM Providers

The advisor benchmark is provider-agnostic. A provider only supplies raw model
outputs; the deterministic audit, parsing rules, and metrics stay unchanged.

## Roles

- Azure OpenAI is for low-cost pilot runs and integration tests.
- OpenAI and Anthropic are for final provider-comparison experiments.
- The current final comparison defaults are OpenAI `gpt-5.5` and Anthropic
  `claude-opus-4-8`.
- Cached pilot runs under `exports/advisor_runs/` are local generated output and
  are not part of the publishable artifact.
- Frozen runs under `paper/data/advisor_runs/` are publishable evidence only
  when they include raw responses, usage metadata, collection timestamps, and
  hashes in `paper/data/DATA_HASHES.txt`.
- A final run becomes paper evidence only after the JSON outputs are reviewed,
  frozen, hashed, and referenced by the audit script.

## Environment

Copy `.env.example` to `.env` and set only the provider you want to run.

```bash
ADVISOR_LLM_PROVIDER=azure
AZURE_OPENAI_ENDPOINT=https://<resource>.openai.azure.com
AZURE_OPENAI_API_KEY=<secret>
AZURE_OPENAI_DEPLOYMENT=<deployment>
AZURE_OPENAI_API_VERSION=2024-10-21
```

```bash
ADVISOR_LLM_PROVIDER=openai
OPENAI_API_KEY=<secret>
OPENAI_MODEL=gpt-5.5
```

```bash
ADVISOR_LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=<secret>
ANTHROPIC_MODEL=claude-opus-4-8
ANTHROPIC_VERSION=2023-06-01
```

## Commands

Budget estimate. This makes no API calls and should be run before any live
collection.

```bash
make advisor-budget
```

Dry run. This makes no API calls.

```bash
make collect-advisor-runs
```

Live Azure pilot with the current `.env` settings. Cached runs are reused and do
not spend budget.

```bash
.venv/bin/python scripts/collect_advisor_runs.py \
  --provider azure \
  --runs 3 \
  --live \
  --max-calls 10
```

Final provider runs use the same command shape:

```bash
.venv/bin/python scripts/collect_advisor_runs.py \
  --provider openai \
  --model gpt-5.5 \
  --runs 3 \
  --live \
  --max-calls 10
```

```bash
.venv/bin/python scripts/collect_advisor_runs.py \
  --provider anthropic \
  --model claude-opus-4-8 \
  --runs 3 \
  --live \
  --max-calls 10
```

## Budget Policy

The default study is three scenarios, three repeated runs, and two providers:
18 total calls. The estimator uses prompt text divided by four as an input-token
approximation and the configured output cap as a maximum. It is intentionally a
pre-authorization ceiling, not a promise of exact billing.

Pricing snapshot used by the estimator, verified on 2026-06-19 against the
provider pricing pages for standard short-context synchronous calls:

- OpenAI `gpt-5.5`: $5.00 per million input tokens and $30.00 per million
  output tokens for standard synchronous calls.
- Anthropic `claude-opus-4-8`: $5.00 per million input tokens and $25.00 per
  million output tokens.

Re-verify provider prices before final paid collection. No live provider calls
should be made until the printed estimate is reviewed and approved.

## Reproducibility Rule

Do not describe a model result in the paper unless the corresponding raw JSON
exists, includes the prompt and raw response, is reproducible by the offline
audit, and is listed in the data hash manifest.
