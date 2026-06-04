# Bibliography Catalog

Indexed catalog of every work cited in the manuscript, grouped by the related-work
thread it supports. The BibTeX source of truth is `paper/references.bib`. PDFs of
open-access works live in `pdfs/` (git-ignored); paywalled works are listed in
`order.txt` for manual download.

## Status legend

- `have` — open-access PDF downloaded into `pdfs/`.
- `order` — listed in `order.txt`; PDF not auto-fetchable.

## Thread 1 — What to own: quality and profitability

| BibKey | Work | Year | Venue | Status |
| --- | --- | --- | --- | --- |
| `novyMarx2013` | The Other Side of Value: The Gross Profitability Premium | 2013 | J. Financial Economics | order |
| `asness2019qmj` | Quality Minus Junk | 2019 | Review of Accounting Studies | order |

Relevance: establish the selection signals our scoring reuses. We propose no new
factor; the contribution is the orthogonal cash-deployment layer.

## Thread 2 — How to trade it: transaction-cost theory and planning

| BibKey | Work | Year | Venue | Status |
| --- | --- | --- | --- | --- |
| `constantinides1986capital` | Capital Market Equilibrium with Transaction Costs | 1986 | J. Political Economy | order |
| `davis1990portfolio` | Portfolio Selection with Transaction Costs | 1990 | Mathematics of Operations Research | order |
| `lobo2007portfolio` | Portfolio Optimization with Linear and Fixed Transaction Costs | 2007 | Annals of Operations Research | have |
| `zhang2019dynamic` | Dynamic Portfolio Optimization with Liquidity Cost and Market Impact | 2019 | Quantitative Finance | have |
| `delarosa2023planning` | Planning for the Efficient Updating of Mutual Fund Portfolios | 2023 | arXiv:2311.16204 | have |

Relevance: the closest prior art. No-trade regions (Constantinides; Davis-Norman)
are the proportional-cost analogue of our fixed-cost guardrail; Lobo-Fazel-Boyd
formalize fixed+linear costs; Zhang et al. add liquidity/impact; de la Rosa casts
rebalancing under fixed fees as planning. We differ by studying a quantized fee,
incremental deployment, and closed-form auditable guardrails.

## Thread 3 — Against the grain: deterministic vs learned advice

| BibKey | Work | Year | Venue | Status |
| --- | --- | --- | --- | --- |
| `elalami2025mlfinance` | Machine Learning and Deep Learning in Computational Finance: A Systematic Review | 2025 | arXiv:2511.21588 | have |

Relevance: documents the ML-in-finance mainstream and its open problems
(interpretability, generalizability, data quality). We position our deterministic
engine as the transparent reference a learned recommender must beat.

## Thread 4 — Whether to believe it: reproducibility over overfitting

| BibKey | Work | Year | Venue | Status |
| --- | --- | --- | --- | --- |
| `bailey2014pseudo` | Pseudo-Mathematics and Financial Charlatanism | 2014 | Notices of the AMS | order |
| `demiguel2009naive` | Optimal Versus Naive Diversification (1/N) | 2009 | Review of Financial Studies | order |

Relevance: motivate the tune-nothing, report-the-negative-result stance. Backtest
overfitting is easy to produce; 1/N is hard to beat. Our equal-weight/risk-parity
result is consistent with both.

## Reproducing this catalog

1. Open-access PDFs are fetched by re-running the download block in the project
   history, or directly from the URLs in `order.txt`.
2. Paywalled PDFs: follow `order.txt`, save each under the bracketed filename in
   `pdfs/`.
3. All BibKeys above must appear in `paper/references.bib` and be cited in
   `paper/main.tex`; CI for the paper is `make paper` (no undefined citations).
