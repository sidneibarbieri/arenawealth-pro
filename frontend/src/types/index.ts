export interface PositionView {
  ticker: string;
  name: string;
  shares: number;
  cost_basis_per_share: number;
  current_price: number;
  market_value: number;
  cost_basis_total: number;
  gain_loss: number;
  gain_loss_pct: number;
  weight_pct: number;
  currency: string;
}

export interface QuoteView {
  ticker: string;
  price: number;
  change: number;
  change_pct: number;
  high_52w?: number;
  low_52w?: number;
}

export interface PortfolioSummary {
  total_value: number;
  total_cost_basis: number;
  total_gain_loss: number;
  total_gain_loss_pct: number;
  position_count: number;
  currency: string;
}

export interface DashboardData {
  summary: PortfolioSummary;
  positions: PositionView[];
  quotes: QuoteView[];
}
