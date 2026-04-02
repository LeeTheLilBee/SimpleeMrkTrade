
"""
SECTION 17H — RISK PHILOSOPHY

This module defines the core risk philosophy of the system.

It is NOT just documentation.
It is designed to be referenced by other engines to enforce discipline.

Future usage:
- aggression control overrides
- capital gating
- rejection tightening
- recovery mode behavior
"""


# 🔹 CORE PHILOSOPHY TEXT (SYSTEM SOURCE OF TRUTH)

RISK_PHILOSOPHY = {
    "core_principles": [
        "Not all valid setups deserve capital",
        "Fewer high-quality trades outperform frequent activity",
        "Timing is required for execution, not just setup quality",
        "Correlation increases hidden risk",
        "Capital must be preserved when edge is unclear",
    ],
    "priority_rules": [
        "The best idea is more important than many good ideas",
        "Weak setups must not compete with strong ones",
        "Capital should concentrate where edge is highest",
    ],
    "restraint_rules": [
        "If no setups meet quality thresholds, do nothing",
        "If timing is not clean, wait",
        "If structure is weak, reject",
        "If trap risk is high, avoid",
    ],
    "aggression_rules": [
        "Aggression must be earned through edge and timing",
        "Strong setups with clean timing allow higher aggression",
        "Moderate setups require controlled exposure",
        "Weak setups should not receive capital",
    ],
    "portfolio_rules": [
        "Avoid stacking similar trades in the same cluster",
        "New trades must improve overall portfolio quality",
        "Exposure should be intentional, not accidental",
    ],
}


# 🔹 OPTIONAL: ENFORCEMENT HELPERS (THIS MAKES IT REAL)

def should_force_hold(decisions: list) -> bool:
    """
    Enforces 'do nothing' philosophy.

    Returns True if no decision is strong enough.
    """
    ready_now = [d for d in decisions if d.get("ready_state") == "ready_now"]
    return len(ready_now) == 0


def should_reduce_aggression(decision: dict) -> bool:
    """
    Applies discipline to weak setups.
    """
    if decision.get("edge_score", 0) < 70:
        return True

    if decision.get("timing_score", 0) < 50:
        return True

    if decision.get("ready_state") != "ready_now":
        return True

    return False


def is_capital_worthy(decision: dict) -> bool:
    """
    Determines if a trade deserves capital at all.
    """
    if not decision.get("eligible"):
        return False

    if decision.get("ready_state") != "ready_now":
        return False

    if decision.get("edge_score", 0) < 75:
        return False

    return True
