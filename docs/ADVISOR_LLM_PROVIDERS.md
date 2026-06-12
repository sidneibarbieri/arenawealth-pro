# Advisor LLM Providers

The advisor benchmark is provider-agnostic. A provider only supplies raw model
outputs; the deterministic audit, parsing rules, and metrics stay unchanged.

## Roles

- Azure OpenAI is for low-cost pilot runs and integration tests.
- OpenAI and Anthropic are for final provider-comparison experiments.
- Cached pilot runs under `exports/advisor_runs/` are local generated output and
  are not part of the publishable artifact.
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
OPENAI_MODEL=gpt-4o
```

```bash
ADVISOR_LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=<secret>
ANTHROPIC_MODEL=claude-sonnet-4-5
ANTHROPIC_VERSION=2023-06-01
```

## Commands

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
  --model gpt-4o \
  --runs 3 \
  --live \
  --max-calls 10
```

```bash
.venv/bin/python scripts/collect_advisor_runs.py \
  --provider anthropic \
  --model claude-sonnet-4-5 \
  --runs 3 \
  --live \
  --max-calls 10
```

## Reproducibility Rule

Do not describe a model result in the paper unless the corresponding raw JSON
exists, includes the prompt and raw response, is reproducible by the offline
audit, and is listed in the data hash manifest.

