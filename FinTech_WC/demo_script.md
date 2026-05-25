# Demo Script — 5-Minute Judge Presentation

## Setup (before the presentation)

1. `./run.sh` — confirm both backend and frontend are running.
2. Place `data/inbox/portfolio-25-05-2026.csv` or any Avenue export in `data/inbox/`.
3. Open `http://127.0.0.1:5173` in Chrome, full-screen, 1280x800.
4. Confirm no `.env` paid keys are set — show this is free-data mode.
5. Have screenshots ready for every step (see Offline Fallback below).

---

## The 5-Minute Arc

### 0:00 — Problem (30 seconds)

> "Self-directed investors make allocation decisions but cannot audit them.
> Most tools show a recommendation without revealing what data it used,
> whether that data is current, or whether the math survives transaction costs."

Point to the dashboard. Show it loads without requiring a login or an API key.

---

### 0:30 — Portfolio source (60 seconds)

1. Show the **Import Status** panel.
   - File: `data/inbox/portfolio-25-05-2026.csv` (or most recent file).
   - Source type: `broker_export`.
   - Positions: 17.
   - Modified: today (or recent date).

2. Say: "The system always shows which file is active. If I edit manually, it shows
   that too. I can revert to the broker export in one click."

3. Click **Edit portfolio** → add one position → show source changes to `manual_override`.
4. Click **Use broker export** → show it reverts.

---

### 1:30 — Provider health (30 seconds)

1. Show the **Provider Status** chips.
2. Explain: green = working live data; yellow = configured but untested; grey = offline fixture.
3. Say: "The workbench never pretends data is live when it isn't. Every recommendation
   shows which provider mode was in effect."

---

### 2:00 — Cash deployment (60 seconds)

1. Enter cash: `$1,500`.
2. Click **Run recommendation**.
3. Show the orders panel: 1-2 orders, each above the $250 minimum.
4. Say: "The minimum order is $250 because the brokerage charges $2.50 per trade —
   that's a 1% floor. Below that, the math says hold cash."
5. Enter cash: `$10`. Click **Run recommendation**. Show "Minimum order not met — hold cash."

---

### 2:60 — Decision log (45 seconds)

1. Show the **Decision Log** panel.
2. Point to: timestamp, policy_version, source file, provider_mode, order count.
3. Say: "Every run is recorded. A reviewer can see exactly what the system used and
   reproduce the same output by feeding in the same inputs."

---

### 3:45 — Candidate screening (30 seconds)

1. Navigate to the **Candidate Screen**.
2. Show top-ranked candidates with scores.
3. Say: "This runs the same deterministic scoring on external candidates using
   free data. The scores are the same every time you run it."

---

### 4:15 — Research evidence (30 seconds)

1. Show price backtest output (or a pre-run screenshot).
2. Say: "We run controlled baselines — not performance claims. We know what the
   data supports and where the limitations are. That's the discipline."

---

### 4:45 — Ask (15 seconds)

> "We're looking for fintech partners who work with self-directed investors or
> independent advisors. The wedge is clear: decision-support with audit trails,
> free-data-first, and honest guardrails. Let's talk."

---

## Offline Fallback

If live demo fails, use these screenshots in order:

| Step | Screenshot file |
|------|-----------------|
| Import Status | `exports/arenawealth_ui_review.png` or take one in advance |
| Provider health | Take screenshot before presentation |
| Cash deployment | Take screenshot with $1,500 and $10 scenarios |
| Decision log | Take screenshot after a real run |
| Candidate screen | Take screenshot from the working app |

Pre-generate all screenshots before traveling to the venue. Test on airplane mode.

---

## Judge Questions and Answers

**"How is this different from Robinhood or a Bloomberg terminal?"**
> "Robinhood shows buy/sell; it doesn't show why or what data it used. Bloomberg
> shows data but not an integrated recommendation + audit path for individual
> investors. We show the full provenance chain — which file, which provider,
> which policy version — so decisions are reproducible."

**"What happens when the free data is wrong?"**
> "The provider health panel shows staleness. The decision log records which
> provider mode was used. If data is flagged as cached or offline, the user
> sees that before acting."

**"This is investment advice — how do you handle regulation?"**
> "The system provides analysis and tools, not personalized investment advice.
> See our compliance framing." *(hand over compliance.md summary)*

**"Where's the business model?"**
> "Freemium workbench for individual investors, then advisor workspace with
> client isolation and audit trail as a paid tier. The compliance path for
> regulated advice is phase 3."

**"What's the evidence it works?"**
> "Deterministic reproducibility is the claim we can prove today — same inputs,
> same output, every time. Performance claims require a licensed backtest with
> real transaction data. We separate what we can prove from what we can't."
