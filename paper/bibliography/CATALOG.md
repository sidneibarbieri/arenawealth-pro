# Bibliography Catalog

This catalog is generated from `paper/bibliography/sources.json`.
`paper/references.bib` remains the BibTeX source used by the manuscript.
PDFs are local research material under `paper/bibliography/pdfs/` and are
ignored by Git; `_order.txt` lists missing or manually downloadable papers.

## Status legend

- `have` — local PDF exists.
- `open-missing` — marked open, but the PDF is not present locally.
- `manual` — requires manual, licensed, or author-copy download.

## AI and Robo Advice

| BibKey | Work | Year | Publication | Role | Status |
| --- | --- | --- | --- | --- | --- |
| `dacunto2019robo` | The Promises and Pitfalls of Robo-Advising | 2019 | Review of Financial Studies | robo-advice evidence | have |
| `hean2024personalfinance` | Can AI Help with Your Personal Finances? | 2024 | arXiv | personal-finance advice comparator | have |
| `ko2024chatgpt` | Can ChatGPT Improve Investment Decisions? From a Portfolio Management Perspective | 2024 | Finance Research Letters | LLM portfolio-management comparator | have |
| `lee2024stockrec` | Stock Recommendations for Individual Investors | 2024 | AI-in-Finance proceedings | individual-stock recommendation comparator | have |
| `oehler2024chatgpt` | Does ChatGPT Provide Better Advice than Robo-Advisors? | 2024 | Finance Research Letters | robo-advice LLM comparator | have |
| `chawla2025riskadvice` | Evaluating AI for Finance: Is AI Credible at Assessing Investment Risk? | 2025 | arXiv | risk-profile audit comparator | have |
| `lee2025bias` | Your AI, Not Your View: The Bias of LLMs in Investment Analysis | 2025 | AI-in-Finance proceedings | LLM investment-bias comparator | have |
| `oh2025alpha` | Democratizing Alpha: LLM-Driven Portfolio Construction for Retail Investors Using Public Financial Media | 2025 | AI-in-Finance proceedings | LLM portfolio-construction comparator | have |
| `spadea2025flarko` | Aligning Language Models with Investor and Market Behavior for Financial Recommendations | 2025 | AI-in-Finance proceedings | LLM financial recommendation comparator | have |
| `zhi2025productbias` | Exposing Product Bias in LLM Investment Recommendation | 2025 | arXiv | LLM product-bias comparator | have |

## Baselines and Overfitting

| BibKey | Work | Year | Publication | Role | Status |
| --- | --- | --- | --- | --- | --- |
| `demiguel2009naive` | Optimal Versus Naive Diversification: How Inefficient Is the 1/N Portfolio Strategy? | 2009 | Review of Financial Studies | naive diversification baseline | have |
| `bailey2014pseudo` | Pseudo-Mathematics and Financial Charlatanism: The Effects of Backtest Overfitting on Out-of-Sample Performance | 2014 | Notices of the AMS | backtest-overfitting warning | have |

## Financial AI Systems

| BibKey | Work | Year | Publication | Role | Status |
| --- | --- | --- | --- | --- | --- |
| `yang2023fingpt` | FinGPT: Open-Source Financial Large Language Models | 2023 | arXiv | financial LLM system precedent | have |
| `liu2024financialai` | A Survey of Financial AI: Architectures, Advances and Open Challenges | 2024 | arXiv | financial AI taxonomy | have |
| `yang2024finrobot` | FinRobot: An Open-Source AI Agent Platform for Financial Applications using Large Language Models | 2024 | arXiv | financial agent-system comparator | have |
| `chen2025stockbench` | StockBench: Can LLM Agents Trade Stocks Profitably in Real-world Markets? | 2025 | arXiv | LLM trading-agent benchmark comparator | have |
| `elalami2025mlfinance` | Machine Learning and Deep Learning in Computational Finance: A Systematic Review | 2025 | arXiv | computational-finance survey | have |
| `hu2025fintrust` | FinTrust: A Comprehensive Benchmark of Trustworthiness Evaluation in Finance Domain | 2025 | EMNLP | finance trustworthiness benchmark | have |
| `saha2025agents` | Large Language Model Agents for Investment Management | 2025 | SSRN | investment-management agent survey | have |
| `benhenda2026lookahead` | Look-Ahead-Bench: a Standardized Benchmark of Look-ahead Bias in Point-in-Time LLMs for Finance | 2026 | arXiv | point-in-time LLM look-ahead-bias benchmark | have |
| `li2026finsaber` | Can LLM-based Financial Investing Strategies Outperform the Market in Long Run? | 2026 | KDD | long-horizon LLM investing benchmark | have |
| `qian2026ama` | When Agents Trade: Live Multi-Market Trading Arena for LLM Agents | 2026 | WWW | live multi-market LLM trading-agent benchmark | have |

## Market Simulation and Audit

| BibKey | Work | Year | Publication | Role | Status |
| --- | --- | --- | --- | --- | --- |
| `gu2024spoofability` | The Effect of Liquidity on the Spoofability of Financial Markets | 2024 | AI-in-Finance proceedings | award-level style reference | have |

## Quality and Profitability

| BibKey | Work | Year | Publication | Role | Status |
| --- | --- | --- | --- | --- | --- |
| `novyMarx2013` | The Other Side of Value: The Gross Profitability Premium | 2013 | Journal of Financial Economics | quality factor baseline | have |
| `kanuri2016moat` | Sustainable Competitive Advantage and Stock Performance: The Case for Wide Moat Stocks | 2016 | Applied Economics | moat-investing comparator | have |
| `asness2019qmj` | Quality Minus Junk | 2019 | Review of Accounting Studies | quality factor baseline | have |
| `gu2020machine` | Empirical Asset Pricing via Machine Learning | 2020 | Review of Financial Studies | machine-learning asset-pricing baseline | have |
| `otero2025quality` | How to Improve Quality Investing | 2025 | BRQ Business Research Quarterly | quality-investing comparator | have |

## Transaction Costs

| BibKey | Work | Year | Publication | Role | Status |
| --- | --- | --- | --- | --- | --- |
| `constantinides1986capital` | Capital Market Equilibrium with Transaction Costs | 1986 | Journal of Political Economy | transaction-cost theory | have |
| `davis1990portfolio` | Portfolio Selection with Transaction Costs | 1990 | Mathematics of Operations Research | transaction-cost theory | have |
| `liu2004transaction` | Optimal Consumption and Investment with Transaction Costs and Multiple Risky Assets | 2004 | Journal of Finance | multi-asset transaction-cost theory | have |
| `lobo2007portfolio` | Portfolio Optimization with Linear and Fixed Transaction Costs | 2007 | Annals of Operations Research | fixed-cost optimization precedent | have |
| `garleanu2013dynamic` | Dynamic Trading with Predictable Returns and Transaction Costs | 2013 | Journal of Finance | dynamic trading with costs | have |
| `zhang2019dynamic` | Dynamic Portfolio Optimization with Liquidity Cost and Market Impact | 2019 | Quantitative Finance | liquidity and market-impact precedent | have |
| `delarosa2023planning` | Planning for the Efficient Updating of Mutual Fund Portfolios | 2023 | arXiv | portfolio-update planning precedent | have |

## Reproducibility note

The paper and artifact do not require these PDFs to run. The bibliography
library is a research aid for reading, related-work synthesis, and citation
auditing. Run `make bibliography` to refresh local downloads, the catalog,
`PDF_INDEX.json`, and `_order.txt`.
