# FinTech World Cup Requirements Checklist

## Submission Assets

- [ ] One-line product description.
- [x] Problem statement — `pitch_outline.md` §1.
- [x] Product demo link or local demo script — `demo_script.md`.
- [ ] Pitch deck — slides not yet built.
- [ ] Founder/team profile.
- [x] Market and customer segment — `market_sizing.md`.
- [ ] Business model and pricing hypothesis — defined in `pitch_outline.md` §6; needs one-page write-up.
- [ ] Traction or validation evidence — no live users yet; use `make verify` output as reproducibility evidence.
- [x] Compliance boundary — `compliance.md`.

## Demo Readiness

- [ ] `./run.sh` starts the local app reliably.
- [ ] Data source health panel shows configured and working sources.
- [ ] App can run without paid APIs.
- [ ] API keys are optional and never shown in UI.
- [ ] Portfolio workflow is understandable in under three minutes.
- [ ] Portfolio source/import status is visible.
- [ ] Manual buy/sell edit is demonstrable without external brokerage access.
- [ ] Micro-order guardrails are visible.
- [ ] Candidate screen and deterministic review are visible.

## Product Gaps Before Pitch

### Done
- [x] Editable/importable portfolio workflow in the UI.
- [x] Audit log for recommendation runs.
- [x] Portfolio source/import status panel.
- [x] API health semaphores (working / configured / error).
- [x] Economic guardrails (minimum order, fee logic).
- [x] Claim-evidence matrix — `claim_evidence_matrix.md`.
- [x] Demo script with offline fallback — `demo_script.md`.
- [x] Market sizing (TAM/SAM/SOM) — `market_sizing.md`.
- [x] Compliance framing — `compliance.md`.
- [x] Artifact text hygiene — scanner passes clean.

### Still Needed for Pitch
- [ ] Pitch deck (slides) — highest remaining gap.
- [ ] Landing page or one-pager with the Arena brand direction.
- [ ] Pre-generated demo screenshots for offline fallback.
- [ ] Founder/team profile write-up.
- [ ] One-page business model and pricing hypothesis.

### Post-Pitch / Phase 2
- [ ] Multi-portfolio workspace for advisor mode.
- [ ] User authentication and data isolation.
- [ ] Compliance review for personalized recommendations (requires licensing).

## Brand Direction

Use the restrained Arena identity:

- carbon/dark surface for product authority;
- off-white work surfaces for readability;
- green as the primary trust/action accent;
- blue and gold only as secondary signal colors;
- no glossy brand-board backgrounds in the workbench itself.
