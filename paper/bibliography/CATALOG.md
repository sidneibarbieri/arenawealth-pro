# Bibliography Catalog

Indexed catalog of works cited in the manuscript or tracked as active
state-of-the-art candidates. The BibTeX source of truth is
`paper/references.bib`. PDFs of open-access works live in `pdfs/` (git-ignored);
paywalled works are listed in `order.txt` for manual download.

## Status legend

- `have` — open-access PDF downloaded into `pdfs/`.
- `order` — listed in `order.txt`; PDF not auto-fetchable.

## Thread 1 — What to own: quality and profitability

| BibKey | Work | Year | Venue | Status |
| --- | --- | --- | --- | --- |
| `novyMarx2013` | The Other Side of Value: The Gross Profitability Premium | 2013 | J. Financial Economics | order |
| `asness2019qmj` | Quality Minus Junk | 2019 | Review of Accounting Studies | order |
| `kanuri2016moat` | Sustainable Competitive Advantage and Stock Performance | 2016 | Applied Economics | order |
| `otero2025quality` | How to Improve Quality Investing | 2025 | BRQ Business Research Quarterly | order |

Relevance: establish the selection signals our scoring reuses. We propose no new
factor; the contribution is the orthogonal cash-deployment layer.

Research gap: economic moat and quality investing are studied as selection
signals, but the artifact still lacks a point-in-time benchmark that tests
whether a transparent moat/compounding policy beats simple quality, equal-weight,
and AI-advisor baselines.

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
| `liu2024financialai` | A Survey of Financial AI | 2024 | arXiv:2411.12747 | have |
| `elalami2025mlfinance` | Machine Learning and Deep Learning in Computational Finance | 2025 | arXiv:2511.21588 | have |
| `yang2023fingpt` | FinGPT | 2023 | arXiv:2306.06031 | order |
| `yang2024finrobot` | FinRobot | 2024 | arXiv:2405.14767 | have |
| `chawla2025riskadvice` | Evaluating AI for Finance | 2025 | arXiv:2505.18953 | have |

Relevance: documents the ML-in-finance mainstream and its open problems
(interpretability, generalizability, data quality). We position our deterministic
engine as the transparent reference a learned recommender must beat.

Research gap: current financial-AI systems emphasize agents, workflows,
forecasting, and risk profiling. The missing benchmark is an auditable,
deterministic buy-and-hold recommendation baseline with replayable inputs,
explicit constraints, and free data.

## Thread 4 — AI and robo-advisory recommendations

| BibKey | Work | Year | Venue | Status |
| --- | --- | --- | --- | --- |
| `oehler2024chatgpt` | Does ChatGPT Provide Better Advice than Robo-Advisors? | 2024 | Finance Research Letters | order |
| `ko2024chatgpt` | Can ChatGPT Improve Investment Decisions? | 2024 | Finance Research Letters | order |

Relevance: closest application-level comparators. They evaluate LLMs as
investment-advice or portfolio-selection aids. Our opportunity is not to replace
the deterministic policy with an LLM, but to measure whether LLM-generated
recommendations can beat, explain, or faithfully augment a deterministic,
replayable baseline.

## Thread 5 — Whether to believe it: reproducibility over overfitting

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
