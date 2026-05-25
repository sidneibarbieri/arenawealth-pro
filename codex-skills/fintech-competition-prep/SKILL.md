---
name: fintech-competition-prep
description: Use when preparing a fintech product for a startup competition, accelerator pitch, FinTech World Cup, or investor demo where judges evaluate problem clarity, solution novelty, market size, business model, compliance awareness, and live demo quality within 5-10 minutes.
metadata:
  short-description: FinTech competition and pitch preparation
---

# FinTech Competition Preparation

Use this skill when a project needs to be packaged for a product-pitch
competition (e.g., FinTech World Cup, Money20/20 Hackathon, accelerator demo
days) where the audience is judges with finance and product backgrounds, not
academic reviewers.

This is distinct from `prize-submission-strategy`, which targets research
venues. Competitions favor working demos, market narrative, and business
traction over methodology rigor.

## What Judges Score

Typical FinTech competition rubric (verify against the specific event):

1. Problem sharpness — is the pain real and clearly stated?
2. Solution differentiation — why is this better or different?
3. Demo quality — does it work live in front of judges?
4. Market size — is the addressable market worth pursuing?
5. Business model — is there a plausible path to revenue?
6. Team and execution signal — can this team ship?
7. Compliance/regulatory awareness — do they know the rules?

## Workflow

### 1. Sharpen the problem statement
- One sentence: who suffers, what is the specific pain, what is the current
  best alternative.
- Avoid "investors lose money" — too generic. Prefer: "retail investors in
  self-directed accounts hold losing positions 2x longer than winning ones
  due to loss aversion; no existing tool intervenes at the order level."

### 2. Build the claim-evidence matrix
- Each differentiation claim needs a demo screen, a metric, or a study.
- Remove claims that have no supporting evidence in the demo.
- Frame limitations as known boundaries, not weaknesses.

### 3. Size the market honestly
- TAM / SAM / SOM with sources.
- "Self-directed retail brokerage accounts in the US" is more credible than
  "global wealth management."
- Use public statistics, not internal projections.

### 4. Define the demo narrative (5 minutes)
A competition demo should follow this arc:
1. Pain (30s): show the problem in one sentence and one number.
2. Solution (60s): show the product doing the core thing.
3. Differentiation (60s): show what others cannot do.
4. Guardrails (60s): show that the system knows its limits.
5. Decision log (60s): show provenance and auditability.
6. Ask (30s): state what you need from judges/investors.

### 5. Prepare the live demo path
- Identify the 3-step golden path: import portfolio → run analysis → inspect
  decision.
- Test the path with no internet (airline mode) using offline fixtures.
- Have a screenshot fallback for every interactive step.
- Do not run live API calls during the demo unless latency is under 2s.

### 6. Write the compliance slide
Even if the product is pre-revenue, judges expect to see:
- What regulation applies (e.g., SEC, FINRA, MiFID II, CVM).
- What the product does vs what it explicitly does not do (e.g., "provides
  analysis, not investment advice").
- How user data is stored and who can access it.
- What the path to a licensed operation looks like.

### 7. Separate pitch materials from the artifact
- Competition slides go in `FinTech_WC/` or a venue-specific directory.
- Never commit venue-specific language into the main source or paper.
- The live product should not display competition branding.

## Package Structure

```
FinTech_WC/
├── README.md           # competition overview and submission checklist
├── pitch_outline.md    # slide-by-slide narrative
├── demo_script.md      # step-by-step demo instructions
├── market_sizing.md    # TAM/SAM/SOM with sources
├── compliance.md       # regulatory framing
└── requirements.md     # venue-specific requirements checklist
```

## Common Mistakes

- Claiming "first ever" without a literature or product search.
- Demo requiring live internet with no fallback.
- Market size numbers without sources.
- No compliance slide — judges in finance always ask about regulation.
- Mixing competition materials into the research paper or vice versa.
- Showing fake performance numbers (e.g., "+42% vs S&P") without a
  documented backtest methodology.
