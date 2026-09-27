"""OBML021–025: first owner Manual Live L1 lifecycle without circular fill gates.

This is a source-only boundary/sequence contract. It does not authenticate
Tower, broker, financial provider, or a human's decision. In particular it
never creates a live mode grant from a checklist or client-provided Boolean.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from web.ob_manual_live_beta_gate_report import REQUIRED_EXTERNAL_GATES

SCHEMA_VERSION = "OBML_OWNER_L1_FIRST_LIVE_PHASES_V1"

# Reuse the existing canonical gate identifiers rather than creating a
# competing clearance decision. These are the pre-access dependencies.
BEFORE_L1_MODE_ACCESS = (
    "TOWER_PURPOSE_BOUND_AUTHENTICATION",
    "TOWER_HOSTED_OWNER_CROSSING",
    "PROVIDER_ACCOUNT_AND_OPTIONS_PERMISSIONS",
    "PROVIDER_SETTLEMENT_AND_PROTECTED_FLOORS",
    "CURRENT_SOURCE_RISK_AND_MARKET",
    "PRODUCTION_OPERATING_APPROVAL",
)
BEFORE_EACH_HUMAN_ORDER = (
    "HUMAN_REVIEW_CENTER_DECISION",
    "PROVIDER_ACCOUNT_AND_OPTIONS_PERMISSIONS",
    "PROVIDER_SETTLEMENT_AND_PROTECTED_FLOORS",
    "CURRENT_SOURCE_RISK_AND_MARKET",
)
AFTER_HUMAN_ORDER = ("EXTERNAL_MANUAL_ORDER_RECONCILIATION",)

# A fill receipt is only possible AFTER a human actually places an order at
# the broker. Requiring a fill before an owner's very first review permission
# would be an impossible circular condition; never waive reconciliation.
KNOWN_EXTERNAL = frozenset(item[0] for item in REQUIRED_EXTERNAL_GATES)
if set(BEFORE_L1_MODE_ACCESS + BEFORE_EACH_HUMAN_ORDER + AFTER_HUMAN_ORDER) != KNOWN_EXTERNAL:
    raise RuntimeError("Owner L1 phase classification must cover every canonical external gate")
if set(BEFORE_L1_MODE_ACCESS) & set(AFTER_HUMAN_ORDER):
    raise RuntimeError("Post-order receipt cannot be a prerequisite to first mode access")


@dataclass(frozen=True)
class OwnerL1Phase:
    name: Literal["MODE_ACCESS", "EACH_HUMAN_ORDER", "POST_ORDER_RECONCILIATION"]
    state: str
    required_gate_ids: tuple[str, ...]
    authority: str
    action_allowed: bool


def owner_l1_first_live_phase_contract() -> dict[str, object]:
    """Return a canonical pending checklist; deliberately NEVER grant trading.

    A different future authenticated Tower issuer and OB receiver must
    independently verify each pre-access item. No object, browser status,
    simulated report, hypothetical fill, or owner declaration passed to this
    source-only function can elevate any state.
    """
    phases = (
        OwnerL1Phase(
            "MODE_ACCESS", "HOLD_INDEPENDENT_PRE_ACCESS_PROOF",
            BEFORE_L1_MODE_ACCESS, "TOWER_AND_INDEPENDENT_EXTERNAL_AUTHORITIES", False,
        ),
        OwnerL1Phase(
            "EACH_HUMAN_ORDER", "HOLD_FRESH_OWNER_REVIEW_AND_RECHECK",
            BEFORE_EACH_HUMAN_ORDER, "OWNER_REVIEW_CENTER_AND_CANONICAL_CURRENT_SOURCES", False,
        ),
        OwnerL1Phase(
            "POST_ORDER_RECONCILIATION", "NOT_DUE_BEFORE_HUMAN_BROKER_PLACEMENT",
            AFTER_HUMAN_ORDER, "INDEPENDENT_BROKER_PROVIDER_RECEIPT", False,
        ),
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "scope": "OWNER_ONLY_MANUAL_LIVE_LEVEL_1",
        "phase_records": tuple({
            "phase": item.name,
            "state": item.state,
            "required_gate_ids": item.required_gate_ids,
            "authority": item.authority,
            "action_allowed": item.action_allowed,
        } for item in phases),
        "all_external_gate_ids_covered": True,
        "post_fill_is_not_a_pre_first_order_requirement": True,
        "post_fill_reconciliation_is_still_mandatory": True,
        "mode_permission_is_not_order_permission": True,
        "each_order_requires_a_new_owner_review_and_fresh_rechecks": True,
        "execution_model": "HUMAN_PLACES_ORDER_AT_INDEPENDENT_BROKER_ONLY",
        "signed_namespace_is_tower_owner_grant": False,
        "generic_tower_step_up_is_obml_purpose_step_up": False,
        "simulation_or_beta_checklist_is_live_permission": False,
        "actual_tower_issuer_receiver_verified": False,
        "authenticated_broker_options_and_capital_verified": False,
        "real_manual_live_activated": False,
        "broker_api_order_submission": False,
        "automatic_contract_selection": False,
        "hybrid_or_automated_execution": False,
        "protected_floor_release": False,
        "capital_movement": False,
        "tester_manual_live_access": False,
        "direct_buybox_balance_access": False,
        "source_only_not_an_activation_endpoint": True,
    }
