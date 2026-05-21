export interface PositionView {
  ticker: string;
  name: string;
  shares: number;
  current_price: number;
  market_value: number;
  gain_loss: number;
  gain_loss_pct: number;
  cost_basis: number;
  currency: string;
  fcf_yield: number;
  roic: number;
  fcf_cagr: number;
  score: number;
  buy_signal: boolean;
  weight_pct: number;
}

export interface PortfolioSummary {
  total_positions: number;
  total_market_value: number;
  total_gain_loss: number;
  total_gain_loss_pct: number;
  buy_signals: number;
  avg_score: number;
  avg_fcf_yield: number;
  avg_roic: number;
  winners: number;
  losers: number;
  best_performer: string;
  worst_performer: string;
  position_count: number;
  total_value: number;
  total_cost_basis: number;
}

export interface PortfolioAnalysis {
  portfolio_grade: string;
  grade: string;
  quality_score: number;
  diversification: string;
  risk_level: string;
  recommendation: string;
}

export interface DashboardData {
  positions: PositionView[];
  summary: PortfolioSummary;
  analysis: PortfolioAnalysis;
}
