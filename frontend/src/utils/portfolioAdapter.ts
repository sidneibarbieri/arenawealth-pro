/** Maps REST `/api/v1/portfolio/user` payloads into dashboard ``types`` models. */

import type { PortfolioSummary, PositionView } from '../types'

export interface ApiPortfolioSummary {
  total_market_value: number
  total_cost_basis: number
  total_gain_loss: number
  total_gain_loss_pct: number
  position_count: number
  currency: string
}

export interface ApiPositionRow {
  ticker: string
  name: string
  shares: number
  current_price: number
  cost_basis_per_share: number
  market_value: number
  cost_basis_total: number
  gain_loss: number
  gain_loss_pct: number
  weight_pct: number
  currency: string
}

export function toPositionView(p: ApiPositionRow): PositionView {
  return {
    ticker: p.ticker,
    name: p.name,
    shares: p.shares,
    current_price: p.current_price,
    market_value: p.market_value,
    gain_loss: p.gain_loss,
    gain_loss_pct: p.gain_loss_pct,
    cost_basis: p.cost_basis_total,
    currency: p.currency,
    fcf_yield: 0,
    roic: 0,
    fcf_cagr: 0,
    score: 0,
    buy_signal: false,
    weight_pct: p.weight_pct,
  }
}

export function toPortfolioSummary(
  s: ApiPortfolioSummary,
  positions: PositionView[],
): PortfolioSummary {
  const winners = positions.filter((x) => x.gain_loss >= 0).length
  const losers = positions.length - winners
  const byRet = [...positions].sort((a, b) => b.gain_loss_pct - a.gain_loss_pct)
  return {
    total_positions: Math.max(s.position_count, positions.length),
    total_market_value: s.total_market_value,
    total_gain_loss: s.total_gain_loss,
    total_gain_loss_pct: s.total_gain_loss_pct,
    buy_signals: positions.filter((x) => x.buy_signal).length,
    avg_score: 0,
    avg_fcf_yield: 0,
    avg_roic: 0,
    winners,
    losers,
    best_performer: byRet[0]?.ticker ?? '',
    worst_performer: byRet.at(-1)?.ticker ?? '',
    position_count: s.position_count,
    total_value: s.total_market_value,
    total_cost_basis: s.total_cost_basis,
  }
}

export function recalculateSummaryFromPositions(
  positions: PositionView[],
): PortfolioSummary {
  const total_market_value = positions.reduce((acc, p) => acc + p.market_value, 0)
  const total_cost_basis = positions.reduce((acc, p) => acc + p.cost_basis, 0)
  const total_gain_loss = total_market_value - total_cost_basis
  const total_gain_loss_pct =
    total_cost_basis > 0 ? (total_gain_loss / total_cost_basis) * 100 : 0
  return toPortfolioSummary(
    {
      total_market_value,
      total_cost_basis,
      total_gain_loss,
      total_gain_loss_pct,
      position_count: positions.length,
      currency: positions[0]?.currency ?? 'USD',
    },
    positions,
  )
}
