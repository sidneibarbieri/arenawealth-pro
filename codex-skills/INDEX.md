# Codex Skills Export

This package contains reusable Codex skills distilled from the ArenaWealth work.
They are generic and can be copied into other repositories or installed into
`~/.codex/skills`.

## Skills

- `deterministic-finance-research`: free-data financial research, baselines,
  ablations, and defensible limitations.
- `decision-audit-trails`: snapshots, decision logs, provenance, and replay.
- `free-data-source-readiness`: free provider configuration and health checks.
- `api-health-semaphores`: visual API health indicators (working/configured/error)
  with probe caching, no secret leakage, and UI chip patterns.
- `portfolio-workbench-ux`: import/edit/monitor portfolio workbench flows.
- `prize-submission-strategy`: prize-oriented research/product preparation with
  evidence discipline.
- `fintech-competition-prep`: startup pitch and competition packaging — demo
  script, claim-evidence matrix, market sizing, compliance framing.
- `repo-artifact-sanitization`: artifact hygiene, legacy triage, and reviewer
  path validation.
- `brand-to-product-polish`: translate brand studies into restrained product UI.

## Install

```bash
cd codex-skills
./install.sh
```

The installer copies each skill folder into `~/.codex/skills` without copying
project-private data.

