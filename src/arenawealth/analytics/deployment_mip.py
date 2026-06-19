"""Optional mixed-integer cash deployment planner.

The default paper policy is the deterministic fee-aware planner in
`deployment.py`. This module provides a solver-backed comparator for cash
deployment under the same concentration and economic minimum-order constraints.
Fee optimality is checked separately against the closed-form subadditive lower
bound in `planner_optimality.py`.
"""

import time
from dataclasses import dataclass

import pulp

from arenawealth.analytics.deployment import (
    MIN_ORDER_AMOUNT,
    ConcentrationLimits,
    FeeParameters,
    build_single_order,
)
from arenawealth.analytics.models import Order, PositionAnalysis


@dataclass(frozen=True)
class MIPDeploymentMetadata:
    """Solver execution metadata for reproducibility and debugging."""

    solver_name: str
    status: str  # 'OPTIMAL', 'NOT_SOLVED', 'INFEASIBLE', 'UNBOUNDED', 'UNDEFINED'
    solve_time_seconds: float
    gap_percent: float | None  # For suboptimal solutions
    deployed_amount_usd: float
    total_orders: int
    explanation: str


def plan_deployment_mip(
    candidates: list[PositionAnalysis],
    cash_usd: float,
    fee_params: FeeParameters | None = None,
    concentration_limits: ConcentrationLimits | None = None,
    solver_backend: str = "PULP_CBC_CMD",
    max_solve_time_seconds: int = 5,
) -> tuple[tuple[Order, ...], MIPDeploymentMetadata]:
    """Solve cash deployment with a mixed-integer formulation.

    Maximizes deployed cash subject to:
    - Theme concentration caps
    - Overweight limits
    - Economic minimum order ($250 floor under the default fee schedule)

    Args:
        candidates: Ranked position analyses (best to worst).
        cash_usd: Available cash to deploy.
        fee_params: Fee model used for the minimum order and returned orders.
        concentration_limits: Portfolio rules (uses defaults if None).
        solver_backend: PuLP solver ('PULP_CBC_CMD', 'PULP_HIGHS', etc).
        max_solve_time_seconds: Timeout for solver.

    Returns:
        Tuple of (orders, solver_metadata).
        Same inputs and solver settings should produce the same output.
    """
    if fee_params is None:
        fee_params = FeeParameters()
    if concentration_limits is None:
        concentration_limits = ConcentrationLimits()

    if cash_usd < MIN_ORDER_AMOUNT:
        return (
            (),
            MIPDeploymentMetadata(
                solver_name=solver_backend,
                status="NOT_SOLVED",
                solve_time_seconds=0.0,
                gap_percent=None,
                deployed_amount_usd=0.0,
                total_orders=0,
                explanation=f"Cash ${cash_usd:.2f} below economic minimum ${MIN_ORDER_AMOUNT:.2f}",
            ),
        )

    prob = pulp.LpProblem("OptimalCashDeployment", pulp.LpMaximize)

    candidate_count = len(candidates)
    allocations = [
        pulp.LpVariable(f"alloc_{candidate_index}", lowBound=0, upBound=cash_usd)
        for candidate_index in range(candidate_count)
    ]
    is_ordered = [
        pulp.LpVariable(f"order_{candidate_index}", cat=pulp.LpBinary)
        for candidate_index in range(candidate_count)
    ]

    prob += pulp.lpSum(allocations)
    prob += pulp.lpSum(allocations) <= cash_usd

    for candidate_index in range(candidate_count):
        prob += allocations[candidate_index] <= cash_usd * is_ordered[candidate_index]

    for candidate_index in range(candidate_count):
        prob += allocations[candidate_index] >= MIN_ORDER_AMOUNT * is_ordered[candidate_index]

    theme_totals = {}
    for candidate_index, candidate in enumerate(candidates):
        if candidate.holding.theme not in theme_totals:
            theme_totals[candidate.holding.theme] = 0
        theme_totals[candidate.holding.theme] += allocations[candidate_index]

    portfolio_value = sum(c.market_value for c in candidates if c.market_value)
    theme_cap_fraction = concentration_limits.theme_concentration_cap_pct / 100
    max_theme_exposure = portfolio_value * theme_cap_fraction
    for theme_total in theme_totals.values():
        prob += theme_total <= max_theme_exposure

    for candidate_index, candidate in enumerate(candidates):
        if candidate.market_value and candidate.market_value > 0:
            max_position_size = candidate.market_value * concentration_limits.overweight_multiple
            prob += allocations[candidate_index] <= max_position_size

    # Solve. msg=0 silences solver output; getSolver forwards it to the backend,
    # which works uniformly across PuLP versions without signature inspection.
    start_time = time.time()
    solver = pulp.getSolver(solver_backend, timeLimit=max_solve_time_seconds, msg=0)
    status = prob.solve(solver)
    solve_time = time.time() - start_time

    # Parse solution. PuLP reports mixed-case names ("Optimal", "Not Solved");
    # canonicalize to the uppercase contract documented on MIPDeploymentMetadata.status.
    status_name = pulp.LpStatus.get(status, "UNKNOWN").upper().replace(" ", "_")

    if status != pulp.LpStatusOptimal:
        return (
            (),
            MIPDeploymentMetadata(
                solver_name=solver_backend,
                status=status_name,
                solve_time_seconds=solve_time,
                gap_percent=None,
                deployed_amount_usd=0.0,
                total_orders=0,
                explanation=f"Solver returned {status_name}",
            ),
        )

    orders = []
    deployed = 0.0

    for candidate_index, candidate in enumerate(candidates):
        allocation = pulp.value(allocations[candidate_index])
        if allocation and allocation >= fee_params.min_order_amount_usd - 1e-6:
            order = build_single_order(candidate, allocation, fee_params)
            orders.append(order)
            deployed += allocation

    deployed_pct = 100 * deployed / cash_usd
    explanation = (
        f"Optimal solution found in {solve_time:.3f}s. "
        f"Deployed ${deployed:.2f} / ${cash_usd:.2f} ({deployed_pct:.1f}%)"
    )
    return (
        tuple(orders),
        MIPDeploymentMetadata(
            solver_name=solver_backend,
            status=status_name,
            solve_time_seconds=solve_time,
            gap_percent=None,
            deployed_amount_usd=deployed,
            total_orders=len(orders),
            explanation=explanation,
        ),
    )
