# Claim-Evidence Matrix

Each product claim must map to a demo screen, a test, a command output, or a
published study. Remove or reframe any claim without an evidence entry.

---

## Core Claims

### Claim 1: Deterministic recommendations
> "The same portfolio and cash input always produces the same recommendation."

| Evidence type | Location |
|---------------|----------|
| Unit test | `tests/unit/test_analytics_deployment.py` — same inputs, same orders |
| Demo step | Run recommendation twice with same cash; both Decision Log rows match |
| Policy version field | Decision Log shows `policy_version` per run |

Status: **supported**

---

### Claim 2: Free-data-first operation
> "The workbench runs useful analysis without paid API keys."

| Evidence type | Location |
|---------------|----------|
| Offline fixture | `data/universe_database.py` — synthetic but structured universe |
| Provider mode | Dashboard shows `provider_mode: offline` when no keys are set |
| Test | `make verify` passes with no `.env` keys configured |

Status: **supported**

---

### Claim 3: Full data-source health visibility
> "Users see the status of each provider before trusting results."

| Evidence type | Location |
|---------------|----------|
| UI panel | Provider status chips in the workbench header |
| States | `working`, `configured`, `not_configured`, `error` per provider |
| Endpoint | `GET /api/v1/health/providers` returns machine-readable status |

Status: **supported**

---

### Claim 4: Economic guardrails on order size
> "The system blocks economically unviable orders (< US$250) to protect against fee erosion."

| Evidence type | Location |
|---------------|----------|
| Rule | `src/arenawealth/analytics/deployment.py` — `MINIMUM_ORDER_USD = 250` |
| Test | `tests/unit/test_analytics_deployment.py` — `cash=0.10` returns no orders |
| UI message | "Minimum order is US$250 (1% fee cap at US$2.50 per trade)" |

Status: **supported**

---

### Claim 5: Auditable decision log
> "Every recommendation run is recorded with its inputs, source, provider mode, and policy version."

| Evidence type | Location |
|---------------|----------|
| Database table | `decisions` in SQLite, schema in `src/arenawealth/models/database.py` |
| Endpoint | `GET /api/v1/portfolio/user/decisions` |
| UI panel | Decision Log panel shows last N runs with timestamp and metadata |
| Test | Decision log test in `tests/unit/test_analytics_deployment.py` |

Status: **supported**

---

### Claim 6: Portfolio source provenance
> "Users always know whether recommendations are based on a broker export, a manual edit, or a fixture."

| Evidence type | Location |
|---------------|----------|
| Source types | `broker_export`, `manual_override`, `private`, `fixture` |
| Endpoint | `GET /api/v1/portfolio/user/source` |
| UI panel | Import Status panel shows active file, modification date, position count |
| Revert | `DELETE /api/v1/portfolio/user/source/manual` reverts to broker export |

Status: **supported**

---

### Claim 7: Broker CSV auto-import
> "The workbench automatically picks up the newest broker export from an inbox directory."

| Evidence type | Location |
|---------------|----------|
| Implementation | `src/arenawealth/importers/holdings_source.py` — `find_latest_inbox_csv()` |
| Test | `tests/unit/test_holdings_source.py` — selects most recent CSV by mtime |
| Inbox path | `data/inbox/*.csv` — ignored by git, user places exports here |

Status: **supported**

---

## Claims Requiring Caution

### Claim: "Risk-parity allocation"
> "Holdings are weighted using risk-parity principles."

Evidence: scoring function exists in `src/arenawealth/analytics/`.  
Limitation: the parity weighting is simplified; it does not use full covariance
estimation. Do not claim full institutional-grade risk parity.

Status: **partial — present as "risk-informed weighting" not "risk parity"**

---

### Claim: "Multi-regime detection"
> "The system detects market regime and adjusts allocation."

Evidence: regime enum exists; no live macro signal currently feeds it.  
Limitation: regime is currently static or user-set.

Status: **future work — do not pitch as live today**

---

## Claims to Remove

The following claims appeared in earlier drafts and have no current evidence:

- "+42% returns vs S&P 500" — no documented backtest with methodology.
- "11 novel features not found in any existing platform" — no comparison study.
- "First behavioral AI in retail platforms" — no literature review supports this.
- "Expected 150-300 citations" — not a meaningful claim before submission.

Remove these from all pitch materials.
