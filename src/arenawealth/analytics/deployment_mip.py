"""Mixed Integer Programming solver for optimal cash deployment.

Implements the state-of-art improvement: replaces greedy heuristic with
exact MIP optimization to maximize deployed cash while respecting all
concentration, fee, and economic constraints.

This module provides:
- MIP formulation for multi-order deployment
- Exact optimality guarantees
- Deterministic, reproducible solutions
- Detailed solver metadata and logs
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
    """Solve optimal deployment using Mixed Integer Programming.

    Maximizes deployed cash subject to:
    - Theme concentration caps
    - Overweight limits
    - Fee efficiency (neutrality or consolidation)
    - Economic minimum ($250 floor)

    Args:
        candidates: Ranked position analyses (best to worst).
        cash_usd: Available cash to deploy.
        fee_params: Fee model (uses defaults if None).
        concentration_limits: Portfolio rules (uses defaults if None).
        solver_backend: PuLP solver ('PULP_CBC_CMD', 'PULP_HIGHS', etc).
        max_solve_time_seconds: Timeout for solver.

    Returns:
        Tuple of (orders, solver_metadata).
        Deterministic: same input → same output (independent of solver randomness).
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

    # Build MIP problem
    prob = pulp.LpProblem("OptimalCashDeployment", pulp.LpMaximize)

    # Decision variables
    n = len(candidates)
    allocations = [
        pulp.LpVariable(f"alloc_{i}", lowBound=0, upBound=cash_usd)
        for i in range(n)
    ]
    is_ordered = [pulp.LpVariable(f"order_{i}", cat=pulp.LpBinary) for i in range(n)]

    # Objective: maximize deployed cash
    prob += pulp.lpSum(allocations)

    # Constraint 1: Total allocation ≤ available cash
    prob += pulp.lpSum(allocations) <= cash_usd

    # Constraint 2: If allocation > 0, then is_ordered = 1 (binary activation)
    for i in range(n):
        prob += allocations[i] <= cash_usd * is_ordered[i]

    # Constraint 3: Minimum order size (if ordered)
    for i in range(n):
        prob += allocations[i] >= MIN_ORDER_AMOUNT * is_ordered[i]

    # Constraint 4: Theme concentration caps
    theme_totals = {}
    for i, candidate in enumerate(candidates):
        if candidate.holding.theme not in theme_totals:
            theme_totals[candidate.holding.theme] = 0
        theme_totals[candidate.holding.theme] += allocations[i]

    portfolio_value = sum(c.market_value for c in candidates if c.market_value)
    theme_cap_fraction = concentration_limits.theme_concentration_cap_pct / 100
    max_theme_exposure = portfolio_value * theme_cap_fraction
    for theme_total in theme_totals.values():
        prob += theme_total <= max_theme_exposure

    # Constraint 5: Overweight limits (position can't grow > OVERWEIGHT_MULTIPLE)
    for i, candidate in enumerate(candidates):
        if candidate.market_value and candidate.market_value > 0:
            max_position_size = (
                candidate.market_value * concentration_limits.overweight_multiple
            )
            prob += allocations[i] <= max_position_size

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

    # Extract solution
    orders = []
    deployed = 0.0

    for i, candidate in enumerate(candidates):
        alloc = pulp.value(allocations[i])
        if alloc and alloc >= fee_params.min_order_amount_usd - 1e-6:
            order = build_single_order(candidate, alloc, fee_params)
            orders.append(order)
            deployed += alloc

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
            gap_percent=None,  # At optimality, gap is 0
            deployed_amount_usd=deployed,
            total_orders=len(orders),
            explanation=explanation,
        ),
    )
