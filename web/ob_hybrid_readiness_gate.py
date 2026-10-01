from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

SCHEMA = "OB_HYBRID_READINESS_GATE_V1"
PATH = "/ob/hybrid-readiness.json"

REQUIRED_LANES = ("CONTROL", "INTEGRATED", "EXPERIMENTAL")

@dataclass(frozen=True)
class GateCheck:
    check_id: str
    label: str
    plain: str
    required: bool = True

CHECKS = (
    GateCheck("real_market_data", "Real market data", "The three simulation lanes must be driven by source-backed market data, not invented prices."),
    GateCheck("point_in_time_integrity", "No future information", "Every decision must use only information that existed at that moment."),
    GateCheck("source_provenance", "Source receipts", "Each simulated decision must be traceable to dated market/research sources."),
    GateCheck("soulaana_intake", "Soulaana actually received the data", "The evidence must show that Soulaana was allowed to read the relevant inputs."),
    GateCheck("soulaana_translation", "Soulaana explained the meaning", "Soulaana must produce a useful finding and why-it-matters explanation instead of only repeating fields."),
    GateCheck("realistic_fills", "Realistic fills", "Paper fills must account for the observed market, spreads, and reasonable slippage instead of perfect prices."),
    GateCheck("options_contract_integrity", "Correct options contracts", "Options trades must have the correct contract identity, strike, expiry, and market context when options are used."),
    GateCheck("risk_controls", "Risk controls passed", "Sizing caps, max-loss rules, exposure checks, duplicate-order checks, cooldowns, and emergency stop tests must pass."),
    GateCheck("bad_data_hold", "Bad data causes a hold", "Missing, stale, conflicting, or rejected source data must cause a hold or degraded state instead of a guess."),
    GateCheck("lane_isolation", "The three accounts stay separate", "Cash, positions, decisions, receipts, and drawdown must not leak between simulation lanes."),
    GateCheck("audit_trail", "Every decision is explainable later", "A complete receipt must show what OB knew, what Soulaana said, what was proposed, and what happened."),
    GateCheck("broker_path_rehearsal", "Hybrid order path rehearsed", "Candidate to prepared order to owner approval to broker acknowledgement/reject/partial-fill handling must be dry-run end to end."),
    GateCheck("no_unexplained_behavior", "No unexplained decisions", "There must be no unresolved trade where we cannot explain why OB acted."),
    GateCheck("evidence_volume", "Enough evidence", "The simulations must cover enough decisions and different market conditions to judge repeatability, not one lucky streak."),
    GateCheck("critical_failures_clear", "No unresolved critical failures", "There must be zero unresolved critical data, safety, accounting, or execution-path failures during the qualification window."),
)


def gate_contract() -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "required_lanes": list(REQUIRED_LANES),
        "checks": [
            {
                "check_id": c.check_id,
                "label": c.label,
                "plain": c.plain,
                "required": c.required,
            }
            for c in CHECKS
        ],
        "profit_is_not_a_gate": True,
        "hybrid_definition": "OB prepares the trade; owner approves or rejects before any live broker submission.",
        "manual_live_required_as_primary_path": False,
        "manual_live_available_as_fallback": True,
        "gate_can_unlock_hybrid": False,
        "gate_can_submit_orders": False,
        "gate_can_move_capital": False,
        "tower_clearance_required_after_qualification": True,
        "owner_approval_required_after_qualification": True,
    }


def _truth(value: Any) -> bool:
    return value is True


def _lane_names(evidence: dict[str, Any]) -> set[str]:
    lanes = evidence.get("lanes")
    if not isinstance(lanes, Iterable) or isinstance(lanes, (str, bytes, dict)):
        return set()
    names: set[str] = set()
    for lane in lanes:
        if isinstance(lane, str):
            names.add(lane.strip().upper())
        elif isinstance(lane, dict):
            name = str(lane.get("lane") or lane.get("name") or "").strip().upper()
            if name:
                names.add(name)
    return names


def evaluate_hybrid_readiness(evidence: dict[str, Any] | None = None) -> dict[str, Any]:
    evidence = evidence if isinstance(evidence, dict) else {}
    provided = evidence.get("checks")
    provided = provided if isinstance(provided, dict) else {}

    lane_names = _lane_names(evidence)
    all_lanes_present = set(REQUIRED_LANES).issubset(lane_names)

    results = []
    blockers = []

    for check in CHECKS:
        passed = _truth(provided.get(check.check_id))
        row = {
            "check_id": check.check_id,
            "label": check.label,
            "plain": check.plain,
            "passed": passed,
            "required": check.required,
        }
        results.append(row)
        if check.required and not passed:
            blockers.append({
                "check_id": check.check_id,
                "label": check.label,
                "reason": check.plain,
            })

    if not all_lanes_present:
        blockers.insert(0, {
            "check_id": "three_simulation_lanes",
            "label": "All three simulation accounts",
            "reason": "CONTROL, INTEGRATED, and EXPERIMENTAL must all be represented in the qualification evidence.",
        })

    qualified = all_lanes_present and not blockers

    if qualified:
        status = "QUALIFIED_FOR_OWNER_APPROVED_HYBRID_REVIEW"
        plain_status = "The simulations earned a Hybrid review. Hybrid is still locked until Tower clearance and owner approval."
    elif any(row["passed"] for row in results):
        status = "NEEDS_MORE_EVIDENCE"
        plain_status = "Some proof is good, but Hybrid stays closed until every required check passes."
    else:
        status = "NOT_READY"
        plain_status = "Hybrid stays closed. Qualification evidence has not been completed yet."

    return {
        "schema": SCHEMA,
        "status": status,
        "plain_status": plain_status,
        "qualified_for_review": qualified,
        "hybrid_unlocked": False,
        "broker_submission_enabled": False,
        "capital_movement_enabled": False,
        "owner_approval_required": True,
        "tower_clearance_required": True,
        "required_lanes": list(REQUIRED_LANES),
        "lanes_seen": sorted(lane_names),
        "all_required_lanes_present": all_lanes_present,
        "checks": results,
        "blockers": blockers,
        "profit_or_loss": "informational_only",
        "next_step": (
            "Tower clearance and explicit owner approval of the first owner-confirmed Hybrid pilot."
            if qualified
            else "Close the listed blockers and collect more simulation evidence."
        ),
    }


def register_hybrid_readiness_gate(app):
    if app.extensions.get("ob_hybrid_readiness_gate_v1"):
        return app

    @app.get(PATH)
    def _hybrid_readiness():
        # V1 deliberately exposes the contract/current empty evaluation only.
        # Qualification evidence will be supplied by the three-lane simulation
        # evidence assembler; this endpoint never trusts browser query claims.
        return evaluate_hybrid_readiness({
            "lanes": [],
            "checks": {},
        }), 200

    app.extensions["ob_hybrid_readiness_gate_v1"] = {
        "path": PATH,
        "schema": SCHEMA,
        "gate_can_unlock_hybrid": False,
        "gate_can_submit_orders": False,
        "gate_can_move_capital": False,
    }
    app.extensions["ob_hybrid_readiness_evaluator_v1"] = evaluate_hybrid_readiness
    return app


__all__ = [
    "SCHEMA",
    "PATH",
    "CHECKS",
    "REQUIRED_LANES",
    "gate_contract",
    "evaluate_hybrid_readiness",
    "register_hybrid_readiness_gate",
]
