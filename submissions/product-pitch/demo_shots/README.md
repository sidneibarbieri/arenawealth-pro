# Demo Fallback Screenshots

Captured from the live app on a real Avenue portfolio (17 positions, ~$200k).
Use these if the live demo fails at the venue. Map to `demo_script.md` steps.

| File | Demo step | What it shows |
|------|-----------|---------------|
| `01_overview.png` | 0:00 Problem | Dashboard loads, no login, portfolio value + positions |
| `02_deploy_1500.png` | 2:00 Cash deployment | $1,500 → two economic orders (TDG, MSFT) above the $250 floor, with guardrails panel |
| `03_guardrail_10.png` | 2:00 Guardrail | $10 → amber warning: "Cash is below the economic order minimum of $250.00" |
| `04_health.png` | 1:30 Provider health | Health status: 5 total, 5 ready, 0 errors |
| `05_import_status.png` | 0:30 Portfolio source | Active file, 17 positions, broker source, modified date |
| `06_decision_log.png` | 2:60 Decision log | Audit trail: policy version, source, mode, cash, orders |
| `07_candidates.png` | 3:45 Candidate screen | Ranked external candidates |

## Regenerate

These were captured in **deterministic reviewer mode** (offline, reproducible).
Before the venue, regenerate with your real, current portfolio:

1. `./run.sh`
2. Place your latest broker CSV in `data/inbox/`
3. Re-run the capture, or take screenshots manually following `demo_script.md`

Reviewer-mode picks are synthetic and not actionable — fine for layout, but for a
real pitch, run with live data (set provider keys) so the orders are real.
