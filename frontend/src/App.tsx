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

const money = new Intl.NumberFormat('en-US', {
  style: 'currency',
  currency: 'USD',
  maximumFractionDigits: 0,
});

const number = new Intl.NumberFormat('en-US', {
  maximumFractionDigits: 2,
});

function App() {
  const [data, setData] = useState<PortfolioResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

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
