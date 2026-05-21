export interface PortfolioSummary {
  total_market_value: number;
  total_cost_basis: number;
  total_gain_loss: number;
  total_gain_loss_pct: number;
  position_count: number;
  currency: string;
}

export interface Position {
  ticker: string;
  name: string;
  shares: number;
  current_price: number;
  change_pct?: number | null;
  market_value: number;
  gain_loss: number;
  gain_loss_pct: number;
  weight_pct?: number;
}

export interface PortfolioResponse {
  summary: PortfolioSummary;
  positions: Position[];
  price_source?: string;
  last_updated: string;
}

export interface RecommendationOrder {
  ticker: string;
  amount: number;
  shares: number;
  fee: number;
}

export interface RankedPosition {
  ticker: string;
  theme: string;
  weight_pct: number;
  moat_class: string;
  compounding_class: string;
  composite_score: number;
  valuation_points: number;
  forward_pe: number | null;
}

export interface RecommendationResponse {
  cash: number;
  provider_mode: string;
  generated_at: string;
  orders: RecommendationOrder[];
  excluded_overweight: string[];
  excluded_theme: string[];
  ranked_positions: RankedPosition[];
}

async function parseJsonResponse<ResponsePayload>(
  response: Response,
  resourceName: string,
): Promise<ResponsePayload> {
  if (!response.ok) {
    throw new Error(`${resourceName} request failed: ${response.status}`);
  }
  return (await response.json()) as ResponsePayload;
}

export async function fetchPortfolio(signal: AbortSignal): Promise<PortfolioResponse> {
  const response = await fetch('/api/v1/portfolio/user', { signal });
  return parseJsonResponse<PortfolioResponse>(response, 'Portfolio');
}

export async function fetchRecommendation(
  cash: number,
  offlineDemo: boolean,
  signal: AbortSignal,
): Promise<RecommendationResponse> {
  const parameters = new URLSearchParams({
    cash: cash.toFixed(2),
    offline_demo: String(offlineDemo),
  });
  const response = await fetch(`/api/v1/portfolio/user/recommendation?${parameters}`, {
    signal,
  });
  return parseJsonResponse<RecommendationResponse>(response, 'Recommendation');
}
