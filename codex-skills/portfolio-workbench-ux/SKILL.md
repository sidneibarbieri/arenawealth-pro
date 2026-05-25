---
name: portfolio-workbench-ux
description: Use when designing or improving an operational portfolio, dashboard, or analytical workbench that needs import, manual edits, monitoring, cash deployment, sorting, cache visibility, and efficient user flows.
metadata:
  short-description: Operational portfolio workbench UX
---

# Portfolio Workbench UX

Use this skill for investor, analyst, or advisor workbenches.

## Core User Stories

- Import the newest broker export from an inbox.
- Manually create or edit holdings when no broker export exists.
- Record buy and sell actions.
- Enter available cash and run analysis on demand.
- See data-source health before trusting results.
- See whether prices are live, cached, or stored.
- Sort tables by meaningful columns.
- Inspect guardrails, exclusions, and rankings.
- Review an audit trail of prior decisions.

## Design Rules

1. Load the workbench quickly.
   - Do not run slow recommendations on initial render.
   - Fetch expensive data only after explicit action.
   - Cache observations with timestamps.

2. Separate source state from decision state.
   - Show active source, source type, modified time, and position count.
   - Manual edits should be reversible.
   - Broker exports should remain immutable inputs.

3. Make bad recommendations impossible where practical.
   - Apply minimum order amounts when fees dominate.
   - Show no-order states as valid outcomes.
   - Explain exclusions and concentration rules.

4. Keep visual density professional.
   - Avoid marketing hero layouts inside the workbench.
   - Use restrained color as state signal.
   - Prevent table overflow on mobile.

5. Validate with browser checks.
   - Desktop and mobile screenshots.
   - No console errors.
   - No horizontal overflow.
   - Main headings and actions visible.

## Output Standard

The workbench should be usable by a real operator and demonstrable to a judge in
under three minutes.

