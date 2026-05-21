import { useEffect, useMemo, useState } from 'react';

interface PortfolioSummary {
  total_market_value: number;
  total_cost_basis: number;
  total_gain_loss: number;
  total_gain_loss_pct: number;
  position_count: number;
  currency: string;
}

interface Position {
  ticker: string;
  name: string;
  shares: number;
  current_price: number;
  market_value: number;
  gain_loss: number;
  gain_loss_pct: number;
  weight_pct?: number;
}

interface PortfolioResponse {
  summary: PortfolioSummary;
  positions: Position[];
  last_updated: string;
}

interface RecommendationOrder {
  ticker: string;
  amount: number;
  shares: number;
  fee: number;
}

interface RankedPosition {
  ticker: string;
  theme: string;
  weight_pct: number;
  moat_class: string;
  compounding_class: string;
  composite_score: number;
  valuation_points: number;
  forward_pe: number | null;
}

interface RecommendationResponse {
  cash: number;
  provider_mode: string;
  generated_at: string;
  orders: RecommendationOrder[];
  excluded_overweight: string[];
  excluded_theme: string[];
  ranked_positions: RankedPosition[];
}

const money = new Intl.NumberFormat('en-US', {
  style: 'currency',
  currency: 'USD',
  maximumFractionDigits: 2,
});

const number = new Intl.NumberFormat('en-US', {
  maximumFractionDigits: 2,
});

function App() {
  const [data, setData] = useState<PortfolioResponse | null>(null);
  const [recommendation, setRecommendation] = useState<RecommendationResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [recommendationError, setRecommendationError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isRecommendationLoading, setIsRecommendationLoading] = useState(true);

  useEffect(() => {
    const controller = new AbortController();

    async function loadPortfolio() {
      setIsLoading(true);
      setError(null);
      const response = await fetch('/api/v1/portfolio/user', {
        signal: controller.signal,
      });
      if (!response.ok) {
        throw new Error(`Portfolio request failed: ${response.status}`);
      }
      const payload = (await response.json()) as PortfolioResponse;
      setData(payload);
      setIsLoading(false);
    }

    loadPortfolio().catch((loadError: unknown) => {
      if (loadError instanceof DOMException && loadError.name === 'AbortError') {
        return;
      }
      setError(loadError instanceof Error ? loadError.message : 'Unknown error');
      setIsLoading(false);
    });

    return () => controller.abort();
  }, []);

  useEffect(() => {
    const controller = new AbortController();

    async function loadRecommendation() {
      setIsRecommendationLoading(true);
      setRecommendationError(null);
      const response = await fetch('/api/v1/portfolio/user/recommendation?cash=1511.18', {
        signal: controller.signal,
      });
      if (!response.ok) {
        throw new Error(`Recommendation request failed: ${response.status}`);
      }
      const payload = (await response.json()) as RecommendationResponse;
      setRecommendation(payload);
      setIsRecommendationLoading(false);
    }

    loadRecommendation().catch((loadError: unknown) => {
      if (loadError instanceof DOMException && loadError.name === 'AbortError') {
        return;
      }
      setRecommendationError(loadError instanceof Error ? loadError.message : 'Unknown error');
      setIsRecommendationLoading(false);
    });

    return () => controller.abort();
  }, []);

  const positions = useMemo(() => {
    if (!data) {
      return [];
    }
    const denominator = data.summary.total_market_value || 1;
    return data.positions
      .map((position) => ({
        ...position,
        weight_pct: position.weight_pct ?? (position.market_value / denominator) * 100,
      }))
      .sort((first, second) => second.market_value - first.market_value);
  }, [data]);

  return (
    <main className="min-h-screen bg-slate-50 text-slate-950">
      <section className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-7xl flex-col gap-4 px-6 py-6 md:flex-row md:items-end md:justify-between">
          <div>
            <p className="text-sm font-medium text-slate-500">ArenaWealth Pro</p>
            <h1 className="mt-1 text-3xl font-semibold tracking-normal text-slate-950">
              Portfolio Dashboard
            </h1>
          </div>
          {data && (
            <p className="text-sm text-slate-500">
              Last updated: {new Date(data.last_updated).toLocaleString('en-US')}
            </p>
          )}
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-6 py-8">
        {isLoading && <p className="text-slate-600">Loading portfolio...</p>}

        {error && (
          <div className="border border-red-200 bg-red-50 p-4 text-sm text-red-800">
            {error}
          </div>
        )}

        {data && (
          <div className="space-y-8">
            <div className="grid gap-4 md:grid-cols-4">
              <Metric label="Total value" value={money.format(data.summary.total_market_value)} />
              <Metric label="Cost basis" value={money.format(data.summary.total_cost_basis)} />
              <Metric
                label="Gain/loss"
                value={money.format(data.summary.total_gain_loss)}
                tone={data.summary.total_gain_loss >= 0 ? 'positive' : 'negative'}
              />
              <Metric label="Positions" value={String(data.summary.position_count)} />
            </div>

            <section className="border border-slate-200 bg-white p-5">
              <div className="flex flex-col gap-2 md:flex-row md:items-end md:justify-between">
                <div>
                  <h2 className="text-xl font-semibold">Cash Deployment</h2>
                  <p className="text-sm text-slate-500">
                    Moat, compounding, valuation, concentration, and theme-aware sizing.
                  </p>
                </div>
                {recommendation && (
                  <p className="text-sm text-slate-500">
                    Provider: {recommendation.provider_mode} · Cash:{' '}
                    {money.format(recommendation.cash)}
                  </p>
                )}
              </div>

              {isRecommendationLoading && (
                <p className="mt-4 text-sm text-slate-600">Loading recommendation...</p>
              )}

              {recommendationError && (
                <div className="mt-4 border border-amber-200 bg-amber-50 p-3 text-sm text-amber-900">
                  {recommendationError}
                </div>
              )}

              {recommendation && (
                <div className="mt-5 grid gap-5 lg:grid-cols-[1fr_1.4fr]">
                  <div className="space-y-3">
                    {recommendation.orders.map((order) => (
                      <div key={order.ticker} className="border border-slate-200 p-4">
                        <p className="text-sm text-slate-500">Buy</p>
                        <p className="mt-1 text-2xl font-semibold">{order.ticker}</p>
                        <p className="mt-2 text-sm text-slate-700">
                          {money.format(order.amount)} · {number.format(order.shares)} shares ·{' '}
                          {money.format(order.fee)} fee
                        </p>
                      </div>
                    ))}
                    <p className="text-xs text-slate-500">
                      Overweight skipped: {recommendation.excluded_overweight.join(', ') || 'none'}
                    </p>
                    <p className="text-xs text-slate-500">
                      Theme skipped: {recommendation.excluded_theme.join(', ') || 'none'}
                    </p>
                  </div>

                  <div className="overflow-hidden border border-slate-200">
                    <table className="min-w-full divide-y divide-slate-200">
                      <thead className="bg-slate-100 text-left text-xs font-semibold uppercase text-slate-600">
                        <tr>
                          <th className="px-3 py-2">Ticker</th>
                          <th className="px-3 py-2">Theme</th>
                          <th className="px-3 py-2 text-right">Weight</th>
                          <th className="px-3 py-2 text-right">Score</th>
                          <th className="px-3 py-2 text-right">Valuation</th>
                          <th className="px-3 py-2 text-right">fPE</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-100 text-sm">
                        {recommendation.ranked_positions.slice(0, 8).map((position) => (
                          <tr key={position.ticker}>
                            <td className="px-3 py-2 font-semibold">{position.ticker}</td>
                            <td className="px-3 py-2 text-slate-600">{position.theme}</td>
                            <td className="px-3 py-2 text-right">
                              {number.format(position.weight_pct)}%
                            </td>
                            <td className="px-3 py-2 text-right">
                              {number.format(position.composite_score)}
                            </td>
                            <td className="px-3 py-2 text-right">
                              {number.format(position.valuation_points)}
                            </td>
                            <td className="px-3 py-2 text-right">
                              {position.forward_pe ? number.format(position.forward_pe) : 'n/a'}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </section>

            <div className="overflow-hidden border border-slate-200 bg-white">
              <table className="min-w-full divide-y divide-slate-200">
                <thead className="bg-slate-100 text-left text-xs font-semibold uppercase text-slate-600">
                  <tr>
                    <th className="px-4 py-3">Ticker</th>
                    <th className="px-4 py-3">Name</th>
                    <th className="px-4 py-3 text-right">Shares</th>
                    <th className="px-4 py-3 text-right">Price</th>
                    <th className="px-4 py-3 text-right">Value</th>
                    <th className="px-4 py-3 text-right">Weight</th>
                    <th className="px-4 py-3 text-right">P/L</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 text-sm">
                  {positions.map((position) => (
                    <tr key={position.ticker} className="hover:bg-slate-50">
                      <td className="px-4 py-3 font-semibold">{position.ticker}</td>
                      <td className="px-4 py-3 text-slate-600">{position.name}</td>
                      <td className="px-4 py-3 text-right">{number.format(position.shares)}</td>
                      <td className="px-4 py-3 text-right">
                        {money.format(position.current_price)}
                      </td>
                      <td className="px-4 py-3 text-right">
                        {money.format(position.market_value)}
                      </td>
                      <td className="px-4 py-3 text-right">
                        {number.format(position.weight_pct)}%
                      </td>
                      <td
                        className={`px-4 py-3 text-right font-medium ${
                          position.gain_loss >= 0 ? 'text-emerald-700' : 'text-red-700'
                        }`}
                      >
                        {money.format(position.gain_loss)} ({number.format(position.gain_loss_pct)}
                        %)
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </section>
    </main>
  );
}

interface MetricProps {
  label: string;
  value: string;
  tone?: 'positive' | 'negative';
}

function Metric({ label, value, tone }: MetricProps) {
  const toneClass =
    tone === 'positive' ? 'text-emerald-700' : tone === 'negative' ? 'text-red-700' : 'text-slate-950';

  return (
    <div className="border border-slate-200 bg-white p-4">
      <p className="text-sm text-slate-500">{label}</p>
      <p className={`mt-2 text-2xl font-semibold ${toneClass}`}>{value}</p>
    </div>
  );
}

export default App;
