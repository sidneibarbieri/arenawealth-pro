import {
  Activity,
  AlertTriangle,
  BarChart3,
  CheckCircle2,
  CircleDollarSign,
  RefreshCw,
  ShieldCheck,
  WalletCards,
} from 'lucide-react';
import { useEffect, useMemo, useState } from 'react';

import {
  fetchPortfolio,
  fetchRecommendation,
  type PortfolioResponse,
  type Position,
  type RecommendationOrder,
  type RecommendationResponse,
} from './api';
import { formatDateTime, formatMoney, formatNumber, formatPercent } from './format';
import { type TableSort, useTableSort } from './useTableSort';

const DEFAULT_CASH = 1511.18;

function readInitialCash(): number {
  const cashParameter = new URLSearchParams(window.location.search).get('cash');
  if (!cashParameter) {
    return DEFAULT_CASH;
  }
  return parseCashInput(cashParameter);
}

function readInitialOfflineDemo(): boolean {
  return new URLSearchParams(window.location.search).get('offline_demo') === 'true';
}

function parseCashInput(value: string): number {
  const normalizedValue = value.replace(',', '.').trim();
  const parsedValue = Number(normalizedValue);
  if (!Number.isFinite(parsedValue) || parsedValue <= 0) {
    throw new Error('Cash must be a positive number.');
  }
  return parsedValue;
}

function isAbortError(error: unknown): boolean {
  return error instanceof DOMException && error.name === 'AbortError';
}

function App() {
  const [portfolio, setPortfolio] = useState<PortfolioResponse | null>(null);
  const [recommendation, setRecommendation] = useState<RecommendationResponse | null>(null);
  const [portfolioError, setPortfolioError] = useState<string | null>(null);
  const [recommendationError, setRecommendationError] = useState<string | null>(null);
  const [isPortfolioLoading, setIsPortfolioLoading] = useState(true);
  const [isRecommendationLoading, setIsRecommendationLoading] = useState(true);
  const [cashInput, setCashInput] = useState(() => readInitialCash().toFixed(2));
  const [cashToAnalyze, setCashToAnalyze] = useState(() => readInitialCash());
  const [offlineDemo, setOfflineDemo] = useState(() => readInitialOfflineDemo());
  const [refreshIndex, setRefreshIndex] = useState(0);

  useEffect(() => {
    const controller = new AbortController();

    async function loadPortfolio() {
      setIsPortfolioLoading(true);
      setPortfolioError(null);
      const payload = await fetchPortfolio(controller.signal);
      setPortfolio(payload);
      setIsPortfolioLoading(false);
    }

    loadPortfolio().catch((error: unknown) => {
      if (isAbortError(error)) {
        return;
      }
      setPortfolioError(error instanceof Error ? error.message : 'Unknown portfolio error');
      setIsPortfolioLoading(false);
    });

    return () => controller.abort();
  }, [refreshIndex]);

  useEffect(() => {
    const controller = new AbortController();

    async function loadRecommendation() {
      setIsRecommendationLoading(true);
      setRecommendationError(null);
      const payload = await fetchRecommendation(cashToAnalyze, offlineDemo, controller.signal);
      setRecommendation(payload);
      setIsRecommendationLoading(false);
    }

    loadRecommendation().catch((error: unknown) => {
      if (isAbortError(error)) {
        return;
      }
      setRecommendationError(
        error instanceof Error ? error.message : 'Unknown recommendation error',
      );
      setIsRecommendationLoading(false);
    });

    return () => controller.abort();
  }, [cashToAnalyze, offlineDemo, refreshIndex]);

  const positions = useMemo(() => {
    if (!portfolio) {
      return [];
    }
    const denominator = portfolio.summary.total_market_value || 1;
    return portfolio.positions
      .map((position) => ({
        ...position,
        weight_pct: position.weight_pct ?? (position.market_value / denominator) * 100,
      }))
      .sort((firstPosition, secondPosition) => {
        return secondPosition.market_value - firstPosition.market_value;
      });
  }, [portfolio]);

  const largestPosition = positions[0];
  const recommendedCapital =
    recommendation?.orders.reduce((total, order) => total + order.amount, 0) ?? 0;
  const topRanked = recommendation?.ranked_positions[0];

  const rankedRows = useMemo(
    () =>
      (recommendation?.ranked_positions ?? []).map((position, index) => ({
        ...position,
        rank: index + 1,
      })),
    [recommendation],
  );
  const rankingSort = useTableSort(rankedRows, 'composite_score', 'desc');
  const positionSort = useTableSort(positions, 'market_value', 'desc');

  function refreshRecommendation() {
    const parsedCash = parseCashInput(cashInput);
    setCashToAnalyze(parsedCash);
    setRefreshIndex((currentIndex) => currentIndex + 1);
  }

  return (
    <main className="app-shell">
      <aside className="side-rail" aria-label="Workspace navigation">
        <div className="brand-lockup">
          <div className="brand-mark">A</div>
          <div>
            <p className="eyebrow">ArenaWealth</p>
            <p className="brand-subtitle">Research desk</p>
          </div>
        </div>
        <nav className="rail-nav">
          <a href="#deployment">
            <CircleDollarSign size={17} />
            Deploy cash
          </a>
          <a href="#rankings">
            <BarChart3 size={17} />
            Quality rank
          </a>
          <a href="#positions">
            <WalletCards size={17} />
            Positions
          </a>
        </nav>
        <div className="rail-note">
          <ShieldCheck size={17} />
          <span>Read-only portfolio. Orders are proposed, not placed.</span>
        </div>
      </aside>

      <section className="workspace">
        <header className="topbar">
          <div>
            <p className="eyebrow">Moat and compounding workbench</p>
            <h1>ArenaWealth Pro</h1>
          </div>
          <button className="icon-button" type="button" onClick={refreshRecommendation}>
            <RefreshCw size={17} />
            Refresh
          </button>
        </header>

        {portfolioError && <StatusBlock tone="danger" message={portfolioError} />}
        {recommendationError && <StatusBlock tone="warning" message={recommendationError} />}

        {portfolio && (
          <>
            <section className="metric-strip" aria-label="Portfolio summary">
              <Metric
                label="Portfolio value"
                value={formatMoney(portfolio.summary.total_market_value)}
              />
              <Metric
                label="Unrealized P/L"
                value={`${formatMoney(portfolio.summary.total_gain_loss)} (${formatPercent(
                  portfolio.summary.total_gain_loss_pct,
                )})`}
                tone={portfolio.summary.total_gain_loss >= 0 ? 'positive' : 'negative'}
              />
              <Metric
                label="Largest position"
                value={largestPosition ? largestPosition.ticker : 'n/a'}
                detail={largestPosition ? formatPercent(largestPosition.weight_pct ?? 0) : undefined}
              />
              <Metric label="Positions" value={String(portfolio.summary.position_count)} />
            </section>

            <section className="deployment-band" id="deployment">
              <div className="section-heading">
                <div>
                  <p className="eyebrow">Cash deployment</p>
                  <h2>Allocation queue</h2>
                </div>
                <span className="freshness">
                  Data snapshot {formatDateTime(portfolio.last_updated)}
                </span>
              </div>

              <div className="control-row">
                <label className="field">
                  <span>Available cash</span>
                  <input
                    inputMode="decimal"
                    type="text"
                    value={cashInput}
                    onChange={(event) => setCashInput(event.target.value)}
                  />
                </label>
                <label className="toggle-field">
                  <input
                    type="checkbox"
                    checked={offlineDemo}
                    onChange={(event) => setOfflineDemo(event.target.checked)}
                  />
                  <span>Deterministic reviewer mode</span>
                </label>
                <button className="primary-button" type="button" onClick={refreshRecommendation}>
                  <Activity size={17} />
                  Analyze
                </button>
              </div>

              <p className="mode-hint">
                Live data drives real recommendations. Reviewer mode swaps in synthetic,
                reproducible fundamentals for offline demos, so its picks differ and are not
                actionable.
              </p>

              {isRecommendationLoading && (
                <div className="loading-row">Loading recommendation...</div>
              )}

              {recommendation && !isRecommendationLoading && (
                <div className="deployment-layout">
                  <div className="order-stack">
                    <div className="provider-line">
                      <CheckCircle2 size={17} />
                      <span>
                        {recommendation.provider_mode === 'offline-demo'
                          ? 'Reviewer demo (synthetic)'
                          : 'Live data'}{' '}
                        · {formatMoney(recommendedCapital)} queued
                      </span>
                    </div>
                    {recommendation.orders.map((order) => (
                      <OrderRow key={order.ticker} order={order} />
                    ))}
                  </div>

                  <div className="decision-notes">
                    <h3>Guardrails</h3>
                    <p>
                      Overweight:{' '}
                      <strong>{recommendation.excluded_overweight.join(', ') || 'none'}</strong>
                    </p>
                    <p>
                      Theme cap: <strong>{recommendation.excluded_theme.join(', ') || 'none'}</strong>
                    </p>
                    <p>
                      Top rank: <strong>{topRanked?.ticker ?? 'n/a'}</strong>
                      {topRanked ? ` at ${formatNumber(topRanked.composite_score)} points` : ''}
                    </p>
                  </div>
                </div>
              )}
            </section>

            {recommendation && (
              <section className="data-section" id="rankings">
                <div className="section-heading">
                  <div>
                    <p className="eyebrow">Research ranking</p>
                    <h2>Moat, compounding, valuation</h2>
                  </div>
                </div>
                <div className="table-frame">
                  <table>
                    <thead>
                      <tr>
                        <SortHeader label="#" columnKey="rank" sort={rankingSort} numeric />
                        <SortHeader label="Ticker" columnKey="ticker" sort={rankingSort} />
                        <SortHeader label="Theme" columnKey="theme" sort={rankingSort} />
                        <SortHeader
                          label="Weight"
                          columnKey="weight_pct"
                          sort={rankingSort}
                          numeric
                        />
                        <SortHeader label="Moat" columnKey="moat_class" sort={rankingSort} />
                        <SortHeader
                          label="Compounding"
                          columnKey="compounding_class"
                          sort={rankingSort}
                        />
                        <SortHeader
                          label="Score"
                          columnKey="composite_score"
                          sort={rankingSort}
                          numeric
                        />
                        <SortHeader
                          label="Valuation"
                          columnKey="valuation_points"
                          sort={rankingSort}
                          numeric
                        />
                        <SortHeader label="fPE" columnKey="forward_pe" sort={rankingSort} numeric />
                      </tr>
                    </thead>
                    <tbody>
                      {rankingSort.sortedRows.map((rankedPosition) => (
                        <tr key={rankedPosition.ticker}>
                          <td className="numeric">{rankedPosition.rank}</td>
                          <td className="ticker-cell">{rankedPosition.ticker}</td>
                          <td>{rankedPosition.theme}</td>
                          <td className="numeric">{formatPercent(rankedPosition.weight_pct)}</td>
                          <td>{rankedPosition.moat_class}</td>
                          <td>{rankedPosition.compounding_class}</td>
                          <td className="numeric">
                            {formatNumber(rankedPosition.composite_score)}
                          </td>
                          <td className="numeric">
                            {formatNumber(rankedPosition.valuation_points)}
                          </td>
                          <td className="numeric">
                            {rankedPosition.forward_pe
                              ? formatNumber(rankedPosition.forward_pe)
                              : 'n/a'}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </section>
            )}

            <section className="data-section" id="positions">
              <div className="section-heading">
                <div>
                  <p className="eyebrow">Current holdings</p>
                  <h2>Portfolio positions</h2>
                </div>
                <span className={`price-badge ${portfolio.price_source === 'live' ? 'live' : ''}`}>
                  {portfolio.price_source === 'live' ? 'Live prices' : 'Stored prices'}
                </span>
              </div>
              <div className="table-frame">
                <table>
                  <thead>
                    <tr>
                      <SortHeader label="Ticker" columnKey="ticker" sort={positionSort} />
                      <SortHeader label="Name" columnKey="name" sort={positionSort} />
                      <SortHeader label="Shares" columnKey="shares" sort={positionSort} numeric />
                      <SortHeader
                        label="Price"
                        columnKey="current_price"
                        sort={positionSort}
                        numeric
                      />
                      <SortHeader label="Day" columnKey="change_pct" sort={positionSort} numeric />
                      <SortHeader
                        label="Value"
                        columnKey="market_value"
                        sort={positionSort}
                        numeric
                      />
                      <SortHeader label="Weight" columnKey="weight_pct" sort={positionSort} numeric />
                      <SortHeader label="P/L" columnKey="gain_loss" sort={positionSort} numeric />
                    </tr>
                  </thead>
                  <tbody>
                    {positionSort.sortedRows.map((position) => (
                      <PositionRow key={position.ticker} position={position} />
                    ))}
                  </tbody>
                </table>
              </div>
            </section>
          </>
        )}

        {isPortfolioLoading && <div className="loading-row">Loading portfolio...</div>}
      </section>
    </main>
  );
}

interface MetricProps {
  label: string;
  value: string;
  detail?: string;
  tone?: 'positive' | 'negative';
}

function Metric({ label, value, detail, tone }: MetricProps) {
  const toneClass = tone ? `metric-value ${tone}` : 'metric-value';
  return (
    <div className="metric">
      <span>{label}</span>
      <strong className={toneClass}>{value}</strong>
      {detail && <small>{detail}</small>}
    </div>
  );
}

interface StatusBlockProps {
  tone: 'warning' | 'danger';
  message: string;
}

function StatusBlock({ tone, message }: StatusBlockProps) {
  return (
    <div className={`status-block ${tone}`}>
      <AlertTriangle size={18} />
      <span>{message}</span>
    </div>
  );
}

interface OrderRowProps {
  order: RecommendationOrder;
}

function OrderRow({ order }: OrderRowProps) {
  return (
    <article className="order-row">
      <div>
        <span>Buy</span>
        <strong>{order.ticker}</strong>
      </div>
      <div className="order-meta">
        <span>{formatMoney(order.amount)}</span>
        <span>{formatNumber(order.shares)} shares</span>
        <span>{formatMoney(order.fee)} fee</span>
      </div>
    </article>
  );
}

interface PositionRowProps {
  position: Position;
}

function PositionRow({ position }: PositionRowProps) {
  const weight = position.weight_pct ?? 0;
  const gainClass = position.gain_loss >= 0 ? 'positive' : 'negative';
  const dayChange = position.change_pct ?? null;
  let dayClass = '';
  if (dayChange !== null) {
    dayClass = dayChange >= 0 ? 'positive' : 'negative';
  }
  return (
    <tr>
      <td className="ticker-cell">{position.ticker}</td>
      <td>{position.name}</td>
      <td className="numeric">{formatNumber(position.shares)}</td>
      <td className="numeric">{formatMoney(position.current_price)}</td>
      <td className={`numeric ${dayClass}`}>
        {dayChange === null ? '—' : formatPercent(dayChange)}
      </td>
      <td className="numeric">{formatMoney(position.market_value)}</td>
      <td className="numeric">{formatPercent(weight)}</td>
      <td className={`numeric ${gainClass}`}>
        {formatMoney(position.gain_loss)} ({formatPercent(position.gain_loss_pct)})
      </td>
    </tr>
  );
}

interface SortHeaderProps<Row> {
  label: string;
  columnKey: keyof Row;
  sort: TableSort<Row>;
  numeric?: boolean;
}

function SortHeader<Row>({ label, columnKey, sort, numeric = false }: SortHeaderProps<Row>) {
  const isActive = sort.sortKey === columnKey;
  let indicator = '';
  if (isActive) {
    indicator = sort.sortDirection === 'asc' ? ' ▲' : ' ▼';
  }
  return (
    <th className={numeric ? 'numeric' : undefined}>
      <button type="button" className="th-sort" onClick={() => sort.toggleSort(columnKey)}>
        {label}
        {indicator}
      </button>
    </th>
  );
}

export default App;
