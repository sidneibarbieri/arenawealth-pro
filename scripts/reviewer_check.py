"""One-command reviewer self-check.

Re-derives the paper's headline numbers from the frozen artifact data and
prints a pass/fail line for each, so a reviewer confirms reproduction without
reading any code. Run with: make review
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RUNS = ROOT / "paper" / "data" / "adversarial_runs"

# What the paper claims, checked against the frozen runs (Section 3).
EXPECTED_VALIDITY = {
    ("openai", "gpt-5.5", "bare"): 0.60,
    ("openai", "gpt-5.5", "policy"): 0.58,
    ("openai", "gpt-5.5", "scaffold"): 1.00,
    ("anthropic", "claude-opus-4-8", "bare"): 0.53,
    ("anthropic", "claude-opus-4-8", "policy"): 0.57,
    ("anthropic", "claude-opus-4-8", "scaffold"): 0.99,
}
RUNS_PER_ARM = 72


@dataclass(frozen=True)
class Check:
    ok: bool
    title: str
    detail: str


def arm_validity(provider: str, model: str, arm: str) -> tuple[float, int, int]:
    """Return (valid_rate, total_runs, truncated_runs) for one arm."""
    arm_dir = RUNS / provider / model / arm
    summary = json.loads((arm_dir / "audit_summary.json").read_text())
    total = sum(row["runs"] for row in summary)
    valid = sum(row["valid_runs"] for row in summary)
    manifest = json.loads((arm_dir / "run_manifest.json").read_text())
    return valid / total, total, manifest.get("truncated_runs", -1)


def check_validity_gradient() -> Check:
    lines: list[str] = []
    ok = True
    for (provider, model, arm), expected in EXPECTED_VALIDITY.items():
        rate, total, truncated = arm_validity(provider, model, arm)
        arm_ok = round(rate, 2) == expected and total == RUNS_PER_ARM and truncated == 0
        ok = ok and arm_ok
        mark = "ok" if arm_ok else "MISMATCH"
        lines.append(
            f"      {model:16s} {arm:9s} {rate:.2f} (paper {expected:.2f}), "
            f"{total} runs, truncated={truncated}  [{mark}]"
        )
    return Check(
        ok,
        "Validity gradient matches the paper (arithmetic-not-judgment)",
        "\n".join(lines),
    )


def check_no_truncation() -> Check:
    bad = [
        f"{model}/{arm}"
        for (provider, model, arm) in EXPECTED_VALIDITY
        if arm_validity(provider, model, arm)[2] != 0
    ]
    return Check(
        not bad,
        "No completion was truncated by the token budget",
        "all arms truncated=0" if not bad else f"truncated arms: {bad}",
    )


def render(checks: list[Check]) -> bool:
    print("ActionAudit -- reviewer self-check\n")
    for check in checks:
        symbol = "[PASS]" if check.ok else "[FAIL]"
        print(f"{symbol} {check.title}")
        if check.detail:
            print(check.detail)
    all_ok = all(check.ok for check in checks)
    print("\n" + ("All checks passed." if all_ok else "Some checks FAILED."))
    print("See REVIEWER_GUIDE.md for the full paper-to-artifact map.")
    return all_ok


def main() -> None:
    checks = [check_validity_gradient(), check_no_truncation()]
    raise SystemExit(0 if render(checks) else 1)


if __name__ == "__main__":
    main()
