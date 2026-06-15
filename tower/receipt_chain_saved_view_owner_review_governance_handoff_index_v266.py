"""
SEARCHABLE LABEL: TOWER_PACK_266_RECEIPT_CHAIN_SAVED_VIEW_OWNER_REVIEW_GOVERNANCE_HANDOFF_INDEX_PREVIEW_MODULE

Tower section:
- The Tower
- Operational Containment
- Receipt Chain Saved View Review Layer
- Governance Handoff layer

Pack 266: Receipt Chain Saved View Owner Review Governance Handoff Index Preview

This module is intentionally simulated/preview-only.

Purpose:
- Start the 266-270 Governance Handoff layer after Pack 261-265 continuity close.
- Build a Tower-owned index of protected handoff lanes.
- Include OB protected rooms, OB mission accounts, Teller protected surfaces, owner/admin surfaces, and receipt/proof surfaces.
- Prepare Pack 267 handoff detail drawer preview.

Safety boundaries:
- No real handoff writes.
- No real app/room/account registry writes.
- No real OB route changes.
- No real Teller route changes.
- No real clearance or permission changes.
- No billing/security writes.
- No receipt/archive/evidence writes.
- No raw evidence reveal.
- No real action execution.
- Cached/non-recursive builders only.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, asdict
from functools import lru_cache
from typing import Any, Dict, List

from tower.receipt_chain_saved_view_owner_review_governance_continuity_batch_close_readiness_v265 import (
    build_receipt_chain_saved_view_owner_review_governance_continuity_batch_close_readiness_preview,
)


PACK_ID = "266"
PACK_NUMBER = 266
PACK_NAME = "Receipt Chain Saved View Owner Review Governance Handoff Index Preview"
ENDPOINT = "/tower/receipt-chain-saved-view-owner-review-governance-handoff-index-v266.json"

TOWER_AREA = "The Tower"
TOWER_SECTION = "Operational Containment"
TOWER_LAYER = "Receipt Chain Saved View Review Layer"
TOWER_SUBLAYER = "Governance Handoff layer"

SOURCE_CLOSED_BATCH = "261-265"
SAVE_BATCH = "266-270"
SAVE_AFTER_PACK = 270
NEXT_BATCH = "266-270"
NEXT_PACK = "267"

SAFE_TO_CONTINUE_FLAG = "safe_to_continue_to_pack_267"
NEXT_PREP_FLAG = "prepare_pack_267_receipt_chain_saved_view_owner_review_governance_handoff_detail_drawer"

OB_PROTECTED_ROOMS = (
    "OB.Dashboard",
    "OB.MarketMap",
    "OB.SymbolPage",
    "OB.TradeCenter",
    "OB.ReviewCenter",
    "OB.OwnerConsole",
)

OB_SUPPORTING_SURFACES = (
    "OB.NotificationsDropdown",
    "OB.SettingsDrawer",
    "OB.ModeChip",
    "OB.TowerStatusChip",
    "OB.Search",
    "OB.Breadcrumbs",
    "OB.SoulaanaDrawerPanels",
    "OB.LockedContentSurfaces",
)

OB_MISSION_ACCOUNTS = (
    "OB.PersonalAccount",
    "OB.TrustAccount",
    "OB.SimpleeWorldBusinessAccount",
    "OB.SimpleeOnTheGoATMAccount",
    "OB.SimpleePropertyApartmentAccount",
    "OB.ProofDemoAccount",
)

TELLER_PROTECTED_SURFACES = (
    "Teller.EmployeePortal",
    "Teller.ManagerPortal",
    "Teller.OwnerDashboard",
    "Teller.Payroll",
    "Teller.BillingSubscriptionStatus",
    "Teller.BusinessEntitySwitching",
    "Teller.PaperworkProofPackets",
    "Teller.FoundationCharityWorkflows",
)

TOWER_OWNED_SURFACES = (
    "Tower.Login",
    "Tower.SignupInviteAcceptance",
    "Tower.PasswordChange",
    "Tower.AccountSecurity",
    "Tower.Billing",
    "Tower.Subscription",
    "Tower.Upgrade",
    "Tower.Checkout",
    "Tower.CustomerPortal",
    "Tower.PlanAccessManagement",
    "Tower.Clearance",
    "Tower.ModePermissions",
)

BLOCKED_REAL_ACTIONS = (
    "real_handoff_write",
    "real_handoff_execute",
    "real_handoff_route_change",
    "real_app_registry_write",
    "real_room_registry_write",
    "real_mission_account_registry_write",
    "real_ob_route_change",
    "real_teller_route_change",
    "real_tower_route_change",
    "real_clearance_write",
    "real_permission_write",
    "real_mode_permission_write",
    "real_billing_write",
    "real_subscription_write",
    "real_checkout_write",
    "real_customer_portal_write",
    "real_account_security_write",
    "real_receipt_write",
    "real_archive_write",
    "real_evidence_export",
    "raw_evidence_reveal",
    "real_owner_review_execute",
    "real_policy_change_write",
    "real_policy_override",
    "real_saved_view_write",
    "real_saved_view_apply",
    "real_user_preference_write",
    "real_action_execution",
    "live_policy_mutation",
    "receipt_chain_mutation",
)


@dataclass(frozen=True)
class GovernanceHandoffIndexLane:
    handoff_id: str
    source_surface: str
    destination_surface: str
    handoff_family: str
    label: str
    purpose: str
    clearance_required: str
    allowed_payload_mode: str
    forbidden_payload_summary: str
    preview_only: bool
    writes_state: bool
    executable: bool
    raw_evidence_visible: bool


@dataclass(frozen=True)
class GovernanceHandoffBoundaryRule:
    rule_id: str
    handoff_id: str
    label: str
    rule_type: str
    allowed: bool
    blocked: bool
    reason: str
    writes_state: bool


@dataclass(frozen=True)
class GovernanceHandoffIndexAction:
    action_id: str
    handoff_id: str
    label: str
    visible: bool
    enabled: bool
    result: str
    reason: str


@dataclass(frozen=True)
class GovernanceHandoffIndexCheckpoint:
    checkpoint_id: str
    label: str
    passed: bool
    result: str
    evidence_mode: str
    writes_state: bool


def _source_payload() -> Dict[str, Any]:
    return deepcopy(build_receipt_chain_saved_view_owner_review_governance_continuity_batch_close_readiness_preview())


def _build_handoff_lanes() -> List[GovernanceHandoffIndexLane]:
    lane_specs = [
        (
            "ob_room_to_tower_clearance",
            "OB.Dashboard",
            "Tower.Clearance",
            "OB_ROOM_ACCESS",
            "OB room access asks Tower for clearance",
            "OB can display access state but Tower owns access decisions.",
            "tower_user_clearance",
            "safe_status_only",
            "No credential, billing secret, permission mutation, or raw security evidence may pass into OB.",
        ),
        (
            "ob_market_map_to_symbol_page",
            "OB.MarketMap",
            "OB.SymbolPage",
            "OB_INTERNAL_NAV",
            "Market Map star opens Symbol Page",
            "A symbol click can route to the protected Symbol Page through Tower-guarded navigation.",
            "ob_member_or_owner",
            "symbol_reference_only",
            "No private strategy internals or execution permission mutation may pass through navigation.",
        ),
        (
            "ob_trade_center_to_symbol_page",
            "OB.TradeCenter",
            "OB.SymbolPage",
            "OB_INTERNAL_NAV",
            "Trade Center row opens Symbol Page",
            "Positions, signals, watchlist rows, candidates, My Plays, and linked portfolio rows can drill into Symbol Page.",
            "ob_member_or_owner",
            "symbol_trade_context_summary",
            "No broker credentials, real execution request, or cross-account trade copy command may pass.",
        ),
        (
            "ob_review_center_to_symbol_page",
            "OB.ReviewCenter",
            "OB.SymbolPage",
            "OB_INTERNAL_NAV",
            "Review Center drill-down opens Symbol Page",
            "Reports, trade replay, receipts, proof/demo records, and performance drill-downs can reference Symbol Page safely.",
            "ob_member_or_owner",
            "review_summary_pointer",
            "No public proof exposure, raw private account evidence, or excluded/quarantined row mutation may pass.",
        ),
        (
            "ob_owner_console_to_tower_owner_review",
            "OB.OwnerConsole",
            "Tower.OwnerReview",
            "OWNER_ADMIN_REVIEW",
            "OB Owner Console escalates to Tower owner review",
            "Owner Console can surface system truth and route owner/admin review to Tower.",
            "tower_owner_clearance",
            "owner_summary_and_receipt_pointer",
            "No owner-only action execution, policy mutation, or evidence reveal may happen inside OB.",
        ),
        (
            "ob_mission_account_to_tower_clearance",
            "OB.MissionAccount",
            "Tower.Clearance",
            "MISSION_ACCOUNT_ACCESS",
            "OB mission account asks Tower for mission clearance",
            "Every OB capital mission account must be cleared by Tower before viewing, mode changes, withdrawals, or account actions.",
            "mission_account_clearance",
            "mission_account_status_summary",
            "No account purpose, entity, withdrawal, strategy, or mode permission may be changed by OB alone.",
        ),
        (
            "ob_trust_account_to_tower_risk",
            "OB.TrustAccount",
            "Tower.RiskPermission",
            "MISSION_ACCOUNT_RISK",
            "Trust OB Account risk permission",
            "Trust account must use stronger conservative controls and preserve long-term capital stewardship.",
            "trust_account_clearance",
            "risk_permission_summary",
            "No reckless options behavior, low-reserve action, or personal/business mixing may pass.",
        ),
        (
            "ob_atm_account_to_teller_business_context",
            "OB.SimpleeOnTheGoATMAccount",
            "Teller.BusinessEntitySwitching",
            "OB_TO_TELLER_BUSINESS_HANDOFF",
            "ATM OB Account asks Teller for business context",
            "ATM mission can request entity/paperwork/proof status through Tower-controlled Teller handoff.",
            "tower_owner_or_business_clearance",
            "business_status_only",
            "No trade signals, candidate scores, live execution logic, or proprietary market intelligence may pass to Teller.",
        ),
        (
            "ob_apartment_account_to_teller_business_context",
            "OB.SimpleePropertyApartmentAccount",
            "Teller.BusinessEntitySwitching",
            "OB_TO_TELLER_BUSINESS_HANDOFF",
            "Apartment OB Account asks Teller for property business context",
            "Apartment mission can request entity/paperwork/proof/reserve status through Tower-controlled Teller handoff.",
            "tower_owner_or_business_clearance",
            "business_status_only",
            "No trade signals, candidate scores, live execution logic, or proprietary market intelligence may pass to Teller.",
        ),
        (
            "ob_proof_demo_to_tower_receipts",
            "OB.ProofDemoAccount",
            "Tower.ReceiptsArchive",
            "PROOF_RECEIPT_HANDOFF",
            "Proof/Demo OB Account routes proof records to Tower receipts",
            "Proof/demo account can produce safe internal proof records without exposing private account data.",
            "owner_or_proof_clearance",
            "redacted_proof_summary",
            "No private personal/trust/business data, raw brokerage data, or public proof route may pass.",
        ),
        (
            "teller_billing_to_ob_access_chip",
            "Teller.BillingSubscriptionStatus",
            "OB.TowerStatusChip",
            "TELLER_TO_OB_STATUS_HANDOFF",
            "Teller billing status updates OB access chip",
            "Teller can provide paid/unpaid/active/inactive status to Tower, which OB may display as locked/allowed state.",
            "tower_billing_clearance",
            "billing_status_only",
            "No payment method details, payroll records, or Teller workflow internals may pass to OB.",
        ),
        (
            "teller_proof_to_tower_receipts",
            "Teller.PaperworkProofPackets",
            "Tower.ReceiptsArchive",
            "TELLER_PROOF_RECEIPT_HANDOFF",
            "Teller proof packets route to Tower receipts",
            "Teller proof packets can be tracked in Tower receipts without entering OB intelligence surfaces.",
            "tower_owner_or_manager_clearance",
            "proof_packet_status_and_receipt_pointer",
            "No payroll-sensitive fields, employee private records, or raw documents may pass to OB.",
        ),
    ]

    return [
        GovernanceHandoffIndexLane(
            handoff_id=f"governance_handoff_index_266_{idx:03d}_{key}",
            source_surface=source,
            destination_surface=destination,
            handoff_family=family,
            label=label,
            purpose=purpose,
            clearance_required=clearance,
            allowed_payload_mode=payload_mode,
            forbidden_payload_summary=forbidden,
            preview_only=True,
            writes_state=False,
            executable=False,
            raw_evidence_visible=False,
        )
        for idx, (key, source, destination, family, label, purpose, clearance, payload_mode, forbidden) in enumerate(lane_specs, start=1)
    ]


def _build_boundary_rules(lanes: List[GovernanceHandoffIndexLane]) -> List[GovernanceHandoffBoundaryRule]:
    rules: List[GovernanceHandoffBoundaryRule] = []

    for lane in lanes:
        rules.extend(
            [
                GovernanceHandoffBoundaryRule(
                    rule_id=f"{lane.handoff_id}_rule_clearance_required",
                    handoff_id=lane.handoff_id,
                    label="Tower clearance required",
                    rule_type="clearance_gate",
                    allowed=True,
                    blocked=False,
                    reason=f"Allowed only after {lane.clearance_required}.",
                    writes_state=False,
                ),
                GovernanceHandoffBoundaryRule(
                    rule_id=f"{lane.handoff_id}_rule_payload_limited",
                    handoff_id=lane.handoff_id,
                    label="Payload is limited to safe mode",
                    rule_type="payload_scope",
                    allowed=True,
                    blocked=False,
                    reason=f"Allowed payload mode: {lane.allowed_payload_mode}.",
                    writes_state=False,
                ),
                GovernanceHandoffBoundaryRule(
                    rule_id=f"{lane.handoff_id}_rule_no_raw_evidence",
                    handoff_id=lane.handoff_id,
                    label="Raw evidence reveal blocked",
                    rule_type="evidence_boundary",
                    allowed=False,
                    blocked=True,
                    reason="Raw evidence reveal is blocked in handoff index preview.",
                    writes_state=False,
                ),
                GovernanceHandoffBoundaryRule(
                    rule_id=f"{lane.handoff_id}_rule_no_mutation",
                    handoff_id=lane.handoff_id,
                    label="Handoff mutation blocked",
                    rule_type="mutation_boundary",
                    allowed=False,
                    blocked=True,
                    reason="No handoff writes, registry writes, clearance writes, route changes, billing writes, or real action execution are allowed.",
                    writes_state=False,
                ),
                GovernanceHandoffBoundaryRule(
                    rule_id=f"{lane.handoff_id}_rule_forbidden_payload",
                    handoff_id=lane.handoff_id,
                    label="Forbidden payload remains blocked",
                    rule_type="forbidden_payload_boundary",
                    allowed=False,
                    blocked=True,
                    reason=lane.forbidden_payload_summary,
                    writes_state=False,
                ),
            ]
        )

    return rules


def _build_actions(lanes: List[GovernanceHandoffIndexLane]) -> List[GovernanceHandoffIndexAction]:
    actions: List[GovernanceHandoffIndexAction] = []

    for lane in lanes:
        actions.extend(
            [
                GovernanceHandoffIndexAction(
                    action_id=f"{lane.handoff_id}_action_preview",
                    handoff_id=lane.handoff_id,
                    label="Preview handoff lane",
                    visible=True,
                    enabled=True,
                    result="preview_allowed",
                    reason="Previewing a handoff lane does not write state.",
                ),
                GovernanceHandoffIndexAction(
                    action_id=f"{lane.handoff_id}_action_write_handoff",
                    handoff_id=lane.handoff_id,
                    label="Write handoff",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Real handoff writes are blocked.",
                ),
                GovernanceHandoffIndexAction(
                    action_id=f"{lane.handoff_id}_action_execute_handoff",
                    handoff_id=lane.handoff_id,
                    label="Execute handoff",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Real handoff execution is blocked.",
                ),
                GovernanceHandoffIndexAction(
                    action_id=f"{lane.handoff_id}_action_change_route",
                    handoff_id=lane.handoff_id,
                    label="Change route",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="OB/Teller/Tower route changes are blocked.",
                ),
                GovernanceHandoffIndexAction(
                    action_id=f"{lane.handoff_id}_action_change_clearance",
                    handoff_id=lane.handoff_id,
                    label="Change clearance",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Clearance changes are blocked.",
                ),
                GovernanceHandoffIndexAction(
                    action_id=f"{lane.handoff_id}_action_reveal_evidence",
                    handoff_id=lane.handoff_id,
                    label="Reveal raw evidence",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Raw evidence reveal is blocked.",
                ),
                GovernanceHandoffIndexAction(
                    action_id=f"{lane.handoff_id}_action_export_receipt",
                    handoff_id=lane.handoff_id,
                    label="Export handoff receipt",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Real receipt/export writes are blocked.",
                ),
            ]
        )

    return actions


def _build_checkpoints() -> List[GovernanceHandoffIndexCheckpoint]:
    rows = [
        ("governance_handoff_index_checkpoint_266_001", "Pack 265 source continuity batch close is ready", "safe_summary_only"),
        ("governance_handoff_index_checkpoint_266_002", "OB protected rooms are represented as protected handoff surfaces", "safe_summary_only"),
        ("governance_handoff_index_checkpoint_266_003", "OB mission accounts are represented as protected mission surfaces", "safe_summary_only"),
        ("governance_handoff_index_checkpoint_266_004", "Teller protected surfaces are represented without mixing OB intelligence into Teller", "safe_summary_only"),
        ("governance_handoff_index_checkpoint_266_005", "Tower-owned access/security/billing surfaces remain Tower-owned", "safe_summary_only"),
        ("governance_handoff_index_checkpoint_266_006", "Raw evidence, route mutation, registry mutation, clearance mutation, billing mutation, and real action execution remain blocked", "blocked_action_summary"),
        ("governance_handoff_index_checkpoint_266_007", "Ready for Pack 267 governance handoff detail drawer preview", "safe_summary_only"),
    ]

    return [
        GovernanceHandoffIndexCheckpoint(
            checkpoint_id=checkpoint_id,
            label=label,
            passed=True,
            result="passed",
            evidence_mode=evidence_mode,
            writes_state=False,
        )
        for checkpoint_id, label, evidence_mode in rows
    ]


def _blocked_action_matrix() -> List[Dict[str, Any]]:
    return [
        {
            "action": action,
            "allowed": False,
            "result": "blocked_preview_only",
            "reason": "Pack 266 previews governance handoff lanes only and cannot mutate handoffs, routes, registries, clearance, billing, security, receipts, evidence, or real actions.",
        }
        for action in BLOCKED_REAL_ACTIONS
    ]


@lru_cache(maxsize=1)
def _build_receipt_chain_saved_view_owner_review_governance_handoff_index_preview_cached() -> Dict[str, Any]:
    source_payload = _source_payload()

    lanes_raw = _build_handoff_lanes()
    rules_raw = _build_boundary_rules(lanes_raw)
    actions_raw = _build_actions(lanes_raw)
    checkpoints_raw = _build_checkpoints()

    lanes = [asdict(lane) for lane in lanes_raw]
    rules = [asdict(rule) for rule in rules_raw]
    actions = [asdict(action) for action in actions_raw]
    checkpoints = [asdict(checkpoint) for checkpoint in checkpoints_raw]

    enabled_action_count = sum(1 for action in actions if action["enabled"] is True)
    blocked_action_count = sum(1 for action in actions if action["enabled"] is False)
    allowed_rule_count = sum(1 for rule in rules if rule["allowed"] is True)
    blocked_rule_count = sum(1 for rule in rules if rule["blocked"] is True)

    handoff_families = sorted({lane["handoff_family"] for lane in lanes})
    ob_room_lane_count = sum(1 for lane in lanes if lane["source_surface"] in OB_PROTECTED_ROOMS or lane["destination_surface"] in OB_PROTECTED_ROOMS)
    mission_account_lane_count = sum(1 for lane in lanes if "Account" in lane["source_surface"] or "MissionAccount" in lane["source_surface"])
    teller_lane_count = sum(1 for lane in lanes if lane["source_surface"].startswith("Teller.") or lane["destination_surface"].startswith("Teller."))
    tower_lane_count = sum(1 for lane in lanes if lane["source_surface"].startswith("Tower.") or lane["destination_surface"].startswith("Tower."))

    all_lanes_preview_only = all(lane["preview_only"] is True for lane in lanes)
    all_lanes_no_writes = all(lane["writes_state"] is False for lane in lanes)
    all_lanes_non_executable = all(lane["executable"] is False for lane in lanes)
    all_lanes_no_raw_evidence = all(lane["raw_evidence_visible"] is False for lane in lanes)
    all_rules_no_writes = all(rule["writes_state"] is False for rule in rules)
    all_actions_safe = all(action["result"] in {"preview_allowed", "blocked_preview_only"} for action in actions)
    all_checkpoints_passed = all(checkpoint["passed"] is True for checkpoint in checkpoints)
    all_checkpoints_no_writes = all(checkpoint["writes_state"] is False for checkpoint in checkpoints)

    governance_handoff_index_ready = all([
        all_lanes_preview_only,
        all_lanes_no_writes,
        all_lanes_non_executable,
        all_lanes_no_raw_evidence,
        all_rules_no_writes,
        all_actions_safe,
        all_checkpoints_passed,
        all_checkpoints_no_writes,
    ])

    preview = {
        "pack": PACK_ID,
        "pack_number": PACK_NUMBER,
        "pack_name": PACK_NAME,
        "status": "ready",
        "readiness": 100,
        "endpoint": ENDPOINT,
        "tower_area": TOWER_AREA,
        "tower_section": TOWER_SECTION,
        "tower_layer": TOWER_LAYER,
        "tower_sublayer": TOWER_SUBLAYER,
        "source_closed_batch": SOURCE_CLOSED_BATCH,
        "save_batch": SAVE_BATCH,
        "save_after_pack": SAVE_AFTER_PACK,
        "next_batch": NEXT_BATCH,
        "next_pack": NEXT_PACK,
        "cached": True,
        "non_recursive": True,
        "simulation_only": True,
        "preview_only": True,
        "receipt_chain_layer": "saved_view_owner_review_governance_handoff_index_preview",
        "source_pack": source_payload.get("pack"),
        "source_endpoint": source_payload.get("endpoint"),
        "source_status": source_payload.get("status"),
        "source_readiness": source_payload.get("readiness"),
        "source_safe_to_continue": source_payload.get("safe_to_continue_to_pack_266"),
        "source_safe_to_push": source_payload.get("safe_to_push_packs_261_to_265"),
        "ob_reference_only": {
            "ob_ui_not_built_here": True,
            "ob_protected_rooms": list(OB_PROTECTED_ROOMS),
            "ob_supporting_surfaces": list(OB_SUPPORTING_SURFACES),
            "ob_mission_accounts": list(OB_MISSION_ACCOUNTS),
            "tower_protection_purpose": "Tower protects OB rooms and mission accounts without building OB UI in this pack.",
        },
        "teller_reference_only": {
            "teller_ui_not_built_here": True,
            "teller_protected_surfaces": list(TELLER_PROTECTED_SURFACES),
            "tower_protection_purpose": "Tower protects Teller surfaces and handoffs without mixing OB intelligence into Teller.",
        },
        "tower_owned_surfaces": list(TOWER_OWNED_SURFACES),
        "governance_handoff_index_lanes": lanes,
        "governance_handoff_boundary_rules": rules,
        "governance_handoff_index_actions": actions,
        "governance_handoff_index_checkpoints": checkpoints,
        "governance_handoff_index_summary": {
            "handoff_lane_count": len(lanes),
            "boundary_rule_count": len(rules),
            "handoff_action_count": len(actions),
            "handoff_checkpoint_count": len(checkpoints),
            "enabled_action_count": enabled_action_count,
            "blocked_action_count": blocked_action_count,
            "allowed_rule_count": allowed_rule_count,
            "blocked_rule_count": blocked_rule_count,
            "handoff_families": handoff_families,
            "ob_room_lane_count": ob_room_lane_count,
            "mission_account_lane_count": mission_account_lane_count,
            "teller_lane_count": teller_lane_count,
            "tower_lane_count": tower_lane_count,
            "all_lanes_preview_only": all_lanes_preview_only,
            "all_lanes_no_writes": all_lanes_no_writes,
            "all_lanes_non_executable": all_lanes_non_executable,
            "all_lanes_no_raw_evidence": all_lanes_no_raw_evidence,
            "all_rules_no_writes": all_rules_no_writes,
            "all_actions_safe": all_actions_safe,
            "all_checkpoints_passed": all_checkpoints_passed,
            "all_checkpoints_no_writes": all_checkpoints_no_writes,
            "governance_handoff_index_ready": governance_handoff_index_ready,
            "real_handoff_write_enabled": False,
            "real_handoff_execute_enabled": False,
            "real_app_registry_write_enabled": False,
            "real_room_registry_write_enabled": False,
            "real_mission_account_registry_write_enabled": False,
            "real_ob_route_change_enabled": False,
            "real_teller_route_change_enabled": False,
            "real_clearance_write_enabled": False,
            "real_permission_write_enabled": False,
            "real_billing_write_enabled": False,
            "real_subscription_write_enabled": False,
            "real_receipt_write_enabled": False,
            "real_archive_write_enabled": False,
            "real_evidence_export_enabled": False,
            "raw_evidence_visible": False,
            "real_action_execution_enabled": False,
        },
        "safety_invariants": {
            "no_real_handoff_write": True,
            "no_real_handoff_execute": True,
            "no_real_route_change": True,
            "no_real_app_registry_write": True,
            "no_real_room_registry_write": True,
            "no_real_mission_account_registry_write": True,
            "no_real_clearance_write": True,
            "no_real_permission_write": True,
            "no_real_billing_write": True,
            "no_real_subscription_write": True,
            "no_real_receipt_write": True,
            "no_real_archive_write": True,
            "no_raw_evidence_reveal": True,
            "no_real_evidence_export": True,
            "no_real_action_execution": True,
            "cached_non_recursive_builder": True,
            "ob_ui_not_built_in_tower_pack": True,
            "teller_ui_not_built_in_tower_pack": True,
        },
        "blocked_action_matrix": _blocked_action_matrix(),
        "route_contract": {
            "method": "GET",
            "returns_json": True,
            "requires_tower_guard": True,
            "unguarded_high_risk_allowed": False,
        },
        "pack_266_acceptance": {
            "source_pack_265_verified": True,
            "ob_protected_rooms_indexed_for_tower_protection": True,
            "ob_mission_accounts_indexed_for_tower_protection": True,
            "teller_surfaces_indexed_for_tower_protection": True,
            "tower_owned_access_billing_security_surfaces_indexed": True,
            "handoff_boundary_rules_built": True,
            "handoff_mutation_paths_blocked": True,
            "ready_for_handoff_detail_drawer": True,
        },
        SAFE_TO_CONTINUE_FLAG: True,
        NEXT_PREP_FLAG: {
            "pack": NEXT_PACK,
            "name": "Receipt Chain Saved View Owner Review Governance Handoff Detail Drawer Preview",
            "mode": "simulated_preview_only",
            "recommended_next_endpoint": "/tower/receipt-chain-saved-view-owner-review-governance-handoff-detail-drawer-v267.json",
            "save_batch": SAVE_BATCH,
            "save_after_pack": SAVE_AFTER_PACK,
        },
    }

    return preview


def build_receipt_chain_saved_view_owner_review_governance_handoff_index_preview() -> Dict[str, Any]:
    """Return a defensive copy of the cached Pack 266 preview payload."""
    return deepcopy(_build_receipt_chain_saved_view_owner_review_governance_handoff_index_preview_cached())


def build_pack_266_status_bridge() -> Dict[str, Any]:
    """Small cached status bridge for Tower cards/status surfaces."""
    preview = _build_receipt_chain_saved_view_owner_review_governance_handoff_index_preview_cached()
    summary = preview["governance_handoff_index_summary"]

    return {
        "pack": preview["pack"],
        "pack_number": preview["pack_number"],
        "pack_name": preview["pack_name"],
        "status": preview["status"],
        "readiness": preview["readiness"],
        "endpoint": preview["endpoint"],
        "tower_section": preview["tower_section"],
        "tower_layer": preview["tower_layer"],
        "tower_sublayer": preview["tower_sublayer"],
        "source_closed_batch": preview["source_closed_batch"],
        "save_batch": preview["save_batch"],
        "save_after_pack": preview["save_after_pack"],
        "next_pack": preview["next_pack"],
        "cached": preview["cached"],
        "non_recursive": preview["non_recursive"],
        "preview_only": preview["preview_only"],
        "source_pack": preview["source_pack"],
        "source_status": preview["source_status"],
        "handoff_lane_count": summary["handoff_lane_count"],
        "boundary_rule_count": summary["boundary_rule_count"],
        "handoff_action_count": summary["handoff_action_count"],
        "governance_handoff_index_ready": summary["governance_handoff_index_ready"],
        SAFE_TO_CONTINUE_FLAG: preview[SAFE_TO_CONTINUE_FLAG],
    }


def prepare_pack_267_receipt_chain_saved_view_owner_review_governance_handoff_detail_drawer() -> Dict[str, Any]:
    """Prepare Pack 267 direction without writing state."""
    return {
        "ready": True,
        "next_pack": NEXT_PACK,
        "name": "Receipt Chain Saved View Owner Review Governance Handoff Detail Drawer Preview",
        "mode": "simulated_preview_only",
        "source_pack": PACK_ID,
        "source_endpoint": ENDPOINT,
        "tower_section": TOWER_SECTION,
        "tower_layer": TOWER_LAYER,
        "tower_sublayer": TOWER_SUBLAYER,
        "source_closed_batch": SOURCE_CLOSED_BATCH,
        "save_batch": SAVE_BATCH,
        "save_after_pack": SAVE_AFTER_PACK,
        "blocked_real_actions": list(BLOCKED_REAL_ACTIONS),
        "safe_to_continue": True,
    }


__all__ = [
    "PACK_ID",
    "PACK_NUMBER",
    "PACK_NAME",
    "ENDPOINT",
    "TOWER_AREA",
    "TOWER_SECTION",
    "TOWER_LAYER",
    "TOWER_SUBLAYER",
    "SOURCE_CLOSED_BATCH",
    "SAVE_BATCH",
    "SAVE_AFTER_PACK",
    "NEXT_BATCH",
    "NEXT_PACK",
    "SAFE_TO_CONTINUE_FLAG",
    "NEXT_PREP_FLAG",
    "OB_PROTECTED_ROOMS",
    "OB_SUPPORTING_SURFACES",
    "OB_MISSION_ACCOUNTS",
    "TELLER_PROTECTED_SURFACES",
    "TOWER_OWNED_SURFACES",
    "BLOCKED_REAL_ACTIONS",
    "build_receipt_chain_saved_view_owner_review_governance_handoff_index_preview",
    "build_pack_266_status_bridge",
    "prepare_pack_267_receipt_chain_saved_view_owner_review_governance_handoff_detail_drawer",
]
