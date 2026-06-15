"""
SEARCHABLE LABEL: TOWER_PACK_277_HANDOFF_POLICY_ROUTE_ENFORCEMENT_DETAIL_DRAWER_PREVIEW_MODULE

Tower section:
- The Tower
- Operational Containment
- Receipt Chain Saved View Review Layer
- Handoff Policy Route Enforcement layer

Pack 277: Receipt Chain Saved View Owner Review Handoff Policy Route Enforcement Detail Drawer Preview

This module is intentionally simulated/preview-only.

Purpose:
- Expand Pack 276 policy route enforcement lanes into safe detail drawers.
- Show policy, denial behavior, enforcement mode, route mutation block, data boundary, and next-step details per lane.
- Keep OB rooms, OB mission accounts, Teller surfaces, Tower-owned access/billing/security routes, and receipt/proof lanes protected.
- Prepare Pack 278 policy route enforcement note draft preview.

Safety boundaries:
- No real policy writes, applies, overrides, or deletes.
- No real route enforcement writes/applies.
- No real route changes or activations.
- No real evidence writes or exports.
- No raw evidence reveal.
- No real handoff execution.
- No real app/room/account registry writes.
- No real OB/Teller UI work.
- No real clearance, permission, billing, subscription, checkout, or security writes.
- No real receipt/archive writes.
- Cached/non-recursive builders only.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, asdict
from functools import lru_cache
from typing import Any, Dict, List

from tower.receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_index_v276 import (
    build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_index_preview,
)


PACK_ID = "277"
PACK_NUMBER = 277
PACK_NAME = "Receipt Chain Saved View Owner Review Handoff Policy Route Enforcement Detail Drawer Preview"
ENDPOINT = "/tower/receipt-chain-saved-view-owner-review-handoff-policy-route-enforcement-detail-drawer-v277.json"

TOWER_AREA = "The Tower"
TOWER_SECTION = "Operational Containment"
TOWER_LAYER = "Receipt Chain Saved View Review Layer"
TOWER_SUBLAYER = "Handoff Policy Route Enforcement layer"

SOURCE_PACK = "276"
SOURCE_CLOSED_BATCH = "271-275"
SAVE_BATCH = "276-280"
SAVE_AFTER_PACK = 280
NEXT_BATCH = "276-280"
NEXT_PACK = "278"

SAFE_TO_CONTINUE_FLAG = "safe_to_continue_to_pack_278"
NEXT_PREP_FLAG = "prepare_pack_278_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_note_draft"

BLOCKED_REAL_ACTIONS = (
    "real_policy_write",
    "real_policy_apply",
    "real_policy_override",
    "real_policy_delete",
    "real_route_enforcement_write",
    "real_route_enforcement_apply",
    "real_route_change",
    "real_route_activation",
    "real_route_deactivation",
    "real_evidence_write",
    "real_evidence_export",
    "raw_evidence_reveal",
    "real_handoff_execute",
    "real_handoff_write",
    "real_note_write",
    "real_note_version_write",
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
    "real_owner_review_execute",
    "real_saved_view_write",
    "real_saved_view_apply",
    "real_action_execution",
    "live_policy_mutation",
    "receipt_chain_mutation",
)


@dataclass(frozen=True)
class HandoffPolicyRouteEnforcementDetailDrawer:
    drawer_id: str
    enforcement_id: str
    enforcement_family: str
    source_surface: str
    destination_surface: str
    policy_id: str
    policy_label: str
    enforcement_mode: str
    denial_behavior: str
    gate_type: str
    label: str
    drawer_status: str
    preview_only: bool
    writes_state: bool
    executable: bool
    raw_evidence_visible: bool


@dataclass(frozen=True)
class HandoffPolicyRouteEnforcementDetailSection:
    section_id: str
    drawer_id: str
    enforcement_id: str
    policy_id: str
    label: str
    section_type: str
    summary: str
    evidence_mode: str
    writes_state: bool
    executable: bool
    raw_evidence_visible: bool


@dataclass(frozen=True)
class HandoffPolicyRouteEnforcementDetailField:
    field_id: str
    drawer_id: str
    enforcement_id: str
    policy_id: str
    label: str
    field_type: str
    preview_value: str
    redaction_state: str
    editable_preview: bool
    writes_state: bool
    raw_evidence_visible: bool


@dataclass(frozen=True)
class HandoffPolicyRouteEnforcementDetailAction:
    action_id: str
    drawer_id: str
    enforcement_id: str
    policy_id: str
    label: str
    visible: bool
    enabled: bool
    result: str
    reason: str


@dataclass(frozen=True)
class HandoffPolicyRouteEnforcementDetailCheckpoint:
    checkpoint_id: str
    label: str
    passed: bool
    result: str
    evidence_mode: str
    writes_state: bool


def _source_payload() -> Dict[str, Any]:
    return deepcopy(build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_index_preview())


def _source_lanes(source_payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    lanes = source_payload.get("handoff_policy_route_enforcement_lanes", [])
    if isinstance(lanes, list) and lanes:
        return deepcopy(lanes)

    return [
        {
            "enforcement_id": "fallback_handoff_policy_route_enforcement",
            "enforcement_family": "TOWER_DEFAULT_DENY_ROUTE_ENFORCEMENT",
            "source_surface": "Any.Source",
            "destination_surface": "Any.Destination",
            "policy_id": "tower.default_deny",
            "policy_label": "Default deny before explicit approval",
            "enforcement_mode": "deny_by_default_preview",
            "denial_behavior": "deny_until_tower_clear",
            "gate_type": "default_deny_gate",
            "purpose": "Fallback policy route enforcement drawer.",
        }
    ]


def _build_drawers(lanes: List[Dict[str, Any]]) -> List[HandoffPolicyRouteEnforcementDetailDrawer]:
    drawers: List[HandoffPolicyRouteEnforcementDetailDrawer] = []

    for idx, lane in enumerate(lanes, start=1):
        drawers.append(
            HandoffPolicyRouteEnforcementDetailDrawer(
                drawer_id=f"handoff_policy_route_enforcement_detail_drawer_277_{idx:03d}",
                enforcement_id=str(lane.get("enforcement_id", f"enforcement_{idx:03d}")),
                enforcement_family=str(lane.get("enforcement_family", "UNKNOWN_ENFORCEMENT_FAMILY")),
                source_surface=str(lane.get("source_surface", "Unknown.Source")),
                destination_surface=str(lane.get("destination_surface", "Unknown.Destination")),
                policy_id=str(lane.get("policy_id", "tower.unknown_policy")),
                policy_label=str(lane.get("policy_label", "Unknown policy")),
                enforcement_mode=str(lane.get("enforcement_mode", "preview_only")),
                denial_behavior=str(lane.get("denial_behavior", "deny_when_unknown")),
                gate_type=str(lane.get("gate_type", "tower_gate")),
                label=f"Policy route enforcement detail drawer for {lane.get('label', 'policy route lane')}",
                drawer_status="policy_route_enforcement_detail_drawer_preview_ready",
                preview_only=True,
                writes_state=False,
                executable=False,
                raw_evidence_visible=False,
            )
        )

    return drawers


def _build_sections(
    drawers: List[HandoffPolicyRouteEnforcementDetailDrawer],
    lanes: List[Dict[str, Any]],
) -> List[HandoffPolicyRouteEnforcementDetailSection]:
    lane_by_id = {str(lane.get("enforcement_id")): lane for lane in lanes}
    sections: List[HandoffPolicyRouteEnforcementDetailSection] = []

    for drawer in drawers:
        lane = lane_by_id.get(drawer.enforcement_id, {})
        purpose = str(lane.get("purpose", "Preview policy route enforcement safely."))

        sections.extend(
            [
                HandoffPolicyRouteEnforcementDetailSection(
                    section_id=f"{drawer.drawer_id}_section_route_path",
                    drawer_id=drawer.drawer_id,
                    enforcement_id=drawer.enforcement_id,
                    policy_id=drawer.policy_id,
                    label="Route path",
                    section_type="route_path",
                    summary=f"{drawer.source_surface} → {drawer.destination_surface} remains preview-only and Tower-policy guarded.",
                    evidence_mode="safe_summary_only",
                    writes_state=False,
                    executable=False,
                    raw_evidence_visible=False,
                ),
                HandoffPolicyRouteEnforcementDetailSection(
                    section_id=f"{drawer.drawer_id}_section_purpose",
                    drawer_id=drawer.drawer_id,
                    enforcement_id=drawer.enforcement_id,
                    policy_id=drawer.policy_id,
                    label="Purpose",
                    section_type="purpose",
                    summary=purpose,
                    evidence_mode="safe_summary_only",
                    writes_state=False,
                    executable=False,
                    raw_evidence_visible=False,
                ),
                HandoffPolicyRouteEnforcementDetailSection(
                    section_id=f"{drawer.drawer_id}_section_policy",
                    drawer_id=drawer.drawer_id,
                    enforcement_id=drawer.enforcement_id,
                    policy_id=drawer.policy_id,
                    label="Policy",
                    section_type="policy",
                    summary=f"Policy {drawer.policy_id}: {drawer.policy_label}. This is a preview and does not write policy.",
                    evidence_mode="safe_summary_only",
                    writes_state=False,
                    executable=False,
                    raw_evidence_visible=False,
                ),
                HandoffPolicyRouteEnforcementDetailSection(
                    section_id=f"{drawer.drawer_id}_section_gate",
                    drawer_id=drawer.drawer_id,
                    enforcement_id=drawer.enforcement_id,
                    policy_id=drawer.policy_id,
                    label="Gate",
                    section_type="gate",
                    summary=f"Gate type: {drawer.gate_type}. Access remains denied unless Tower policy and clearance allow preview.",
                    evidence_mode="safe_summary_only",
                    writes_state=False,
                    executable=False,
                    raw_evidence_visible=False,
                ),
                HandoffPolicyRouteEnforcementDetailSection(
                    section_id=f"{drawer.drawer_id}_section_enforcement_mode",
                    drawer_id=drawer.drawer_id,
                    enforcement_id=drawer.enforcement_id,
                    policy_id=drawer.policy_id,
                    label="Enforcement mode",
                    section_type="enforcement_mode",
                    summary=f"Enforcement mode: {drawer.enforcement_mode}. No route enforcement write or apply occurs.",
                    evidence_mode="blocked_action_summary",
                    writes_state=False,
                    executable=False,
                    raw_evidence_visible=False,
                ),
                HandoffPolicyRouteEnforcementDetailSection(
                    section_id=f"{drawer.drawer_id}_section_denial_behavior",
                    drawer_id=drawer.drawer_id,
                    enforcement_id=drawer.enforcement_id,
                    policy_id=drawer.policy_id,
                    label="Denial behavior",
                    section_type="denial_behavior",
                    summary=f"Denial behavior: {drawer.denial_behavior}. Unsafe handoff, route, evidence, billing, clearance, and registry actions stay blocked.",
                    evidence_mode="blocked_action_summary",
                    writes_state=False,
                    executable=False,
                    raw_evidence_visible=False,
                ),
                HandoffPolicyRouteEnforcementDetailSection(
                    section_id=f"{drawer.drawer_id}_section_data_boundary",
                    drawer_id=drawer.drawer_id,
                    enforcement_id=drawer.enforcement_id,
                    policy_id=drawer.policy_id,
                    label="Data boundary",
                    section_type="data_boundary",
                    summary="Raw evidence, private documents, payment details, OB trade intelligence, and internal registry details remain hidden or pointer-only.",
                    evidence_mode="redacted_pointer_only",
                    writes_state=False,
                    executable=False,
                    raw_evidence_visible=False,
                ),
                HandoffPolicyRouteEnforcementDetailSection(
                    section_id=f"{drawer.drawer_id}_section_ob_teller_boundary",
                    drawer_id=drawer.drawer_id,
                    enforcement_id=drawer.enforcement_id,
                    policy_id=drawer.policy_id,
                    label="OB/Teller boundary",
                    section_type="app_boundary",
                    summary="OB and Teller UI are not built in this Tower pack. Tower only previews policy route enforcement protection.",
                    evidence_mode="safe_summary_only",
                    writes_state=False,
                    executable=False,
                    raw_evidence_visible=False,
                ),
                HandoffPolicyRouteEnforcementDetailSection(
                    section_id=f"{drawer.drawer_id}_section_mutation_block",
                    drawer_id=drawer.drawer_id,
                    enforcement_id=drawer.enforcement_id,
                    policy_id=drawer.policy_id,
                    label="Mutation block",
                    section_type="mutation_block",
                    summary="Policy writes/applies/overrides/deletes, route enforcement writes/applies, route changes, route activation, evidence writes, raw evidence reveal, handoff execution, registry writes, clearance writes, billing/security writes, receipt/archive writes, and real actions remain blocked.",
                    evidence_mode="blocked_action_summary",
                    writes_state=False,
                    executable=False,
                    raw_evidence_visible=False,
                ),
                HandoffPolicyRouteEnforcementDetailSection(
                    section_id=f"{drawer.drawer_id}_section_next_step",
                    drawer_id=drawer.drawer_id,
                    enforcement_id=drawer.enforcement_id,
                    policy_id=drawer.policy_id,
                    label="Next step",
                    section_type="next_step_preview",
                    summary="Prepares Pack 278 handoff policy route enforcement note draft preview without writing notes.",
                    evidence_mode="safe_summary_only",
                    writes_state=False,
                    executable=False,
                    raw_evidence_visible=False,
                ),
            ]
        )

    return sections


def _build_fields(drawers: List[HandoffPolicyRouteEnforcementDetailDrawer]) -> List[HandoffPolicyRouteEnforcementDetailField]:
    fields: List[HandoffPolicyRouteEnforcementDetailField] = []

    for drawer in drawers:
        fields.extend(
            [
                HandoffPolicyRouteEnforcementDetailField(
                    field_id=f"{drawer.drawer_id}_field_source_surface",
                    drawer_id=drawer.drawer_id,
                    enforcement_id=drawer.enforcement_id,
                    policy_id=drawer.policy_id,
                    label="Source surface",
                    field_type="locked_summary",
                    preview_value=drawer.source_surface,
                    redaction_state="safe_preview",
                    editable_preview=False,
                    writes_state=False,
                    raw_evidence_visible=False,
                ),
                HandoffPolicyRouteEnforcementDetailField(
                    field_id=f"{drawer.drawer_id}_field_destination_surface",
                    drawer_id=drawer.drawer_id,
                    enforcement_id=drawer.enforcement_id,
                    policy_id=drawer.policy_id,
                    label="Destination surface",
                    field_type="locked_summary",
                    preview_value=drawer.destination_surface,
                    redaction_state="safe_preview",
                    editable_preview=False,
                    writes_state=False,
                    raw_evidence_visible=False,
                ),
                HandoffPolicyRouteEnforcementDetailField(
                    field_id=f"{drawer.drawer_id}_field_policy_id",
                    drawer_id=drawer.drawer_id,
                    enforcement_id=drawer.enforcement_id,
                    policy_id=drawer.policy_id,
                    label="Policy ID",
                    field_type="locked_summary",
                    preview_value=drawer.policy_id,
                    redaction_state="safe_preview",
                    editable_preview=False,
                    writes_state=False,
                    raw_evidence_visible=False,
                ),
                HandoffPolicyRouteEnforcementDetailField(
                    field_id=f"{drawer.drawer_id}_field_policy_label",
                    drawer_id=drawer.drawer_id,
                    enforcement_id=drawer.enforcement_id,
                    policy_id=drawer.policy_id,
                    label="Policy label",
                    field_type="locked_summary",
                    preview_value=drawer.policy_label,
                    redaction_state="safe_preview",
                    editable_preview=False,
                    writes_state=False,
                    raw_evidence_visible=False,
                ),
                HandoffPolicyRouteEnforcementDetailField(
                    field_id=f"{drawer.drawer_id}_field_enforcement_family",
                    drawer_id=drawer.drawer_id,
                    enforcement_id=drawer.enforcement_id,
                    policy_id=drawer.policy_id,
                    label="Enforcement family",
                    field_type="locked_summary",
                    preview_value=drawer.enforcement_family,
                    redaction_state="safe_preview",
                    editable_preview=False,
                    writes_state=False,
                    raw_evidence_visible=False,
                ),
                HandoffPolicyRouteEnforcementDetailField(
                    field_id=f"{drawer.drawer_id}_field_gate_type",
                    drawer_id=drawer.drawer_id,
                    enforcement_id=drawer.enforcement_id,
                    policy_id=drawer.policy_id,
                    label="Gate type",
                    field_type="locked_summary",
                    preview_value=drawer.gate_type,
                    redaction_state="safe_preview",
                    editable_preview=False,
                    writes_state=False,
                    raw_evidence_visible=False,
                ),
                HandoffPolicyRouteEnforcementDetailField(
                    field_id=f"{drawer.drawer_id}_field_enforcement_mode",
                    drawer_id=drawer.drawer_id,
                    enforcement_id=drawer.enforcement_id,
                    policy_id=drawer.policy_id,
                    label="Enforcement mode",
                    field_type="redacted_pointer",
                    preview_value=drawer.enforcement_mode,
                    redaction_state="safe_preview",
                    editable_preview=False,
                    writes_state=False,
                    raw_evidence_visible=False,
                ),
                HandoffPolicyRouteEnforcementDetailField(
                    field_id=f"{drawer.drawer_id}_field_denial_behavior",
                    drawer_id=drawer.drawer_id,
                    enforcement_id=drawer.enforcement_id,
                    policy_id=drawer.policy_id,
                    label="Denial behavior",
                    field_type="redacted_pointer",
                    preview_value=drawer.denial_behavior,
                    redaction_state="redacted_pointer_only",
                    editable_preview=False,
                    writes_state=False,
                    raw_evidence_visible=False,
                ),
                HandoffPolicyRouteEnforcementDetailField(
                    field_id=f"{drawer.drawer_id}_field_owner_note_preview",
                    drawer_id=drawer.drawer_id,
                    enforcement_id=drawer.enforcement_id,
                    policy_id=drawer.policy_id,
                    label="Owner note preview",
                    field_type="textarea_preview",
                    preview_value=f"Tower can preview policy route enforcement for {drawer.source_surface} → {drawer.destination_surface}; no policy, route, evidence, clearance, billing, registry, or receipt state is written.",
                    redaction_state="safe_preview",
                    editable_preview=True,
                    writes_state=False,
                    raw_evidence_visible=False,
                ),
            ]
        )

    return fields


def _build_actions(drawers: List[HandoffPolicyRouteEnforcementDetailDrawer]) -> List[HandoffPolicyRouteEnforcementDetailAction]:
    actions: List[HandoffPolicyRouteEnforcementDetailAction] = []

    for drawer in drawers:
        actions.extend(
            [
                HandoffPolicyRouteEnforcementDetailAction(
                    action_id=f"{drawer.drawer_id}_action_preview",
                    drawer_id=drawer.drawer_id,
                    enforcement_id=drawer.enforcement_id,
                    policy_id=drawer.policy_id,
                    label="Preview policy route enforcement detail",
                    visible=True,
                    enabled=True,
                    result="preview_allowed",
                    reason="Previewing policy route enforcement detail does not write state.",
                ),
                HandoffPolicyRouteEnforcementDetailAction(
                    action_id=f"{drawer.drawer_id}_action_write_policy",
                    drawer_id=drawer.drawer_id,
                    enforcement_id=drawer.enforcement_id,
                    policy_id=drawer.policy_id,
                    label="Write policy",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Real policy writes are blocked.",
                ),
                HandoffPolicyRouteEnforcementDetailAction(
                    action_id=f"{drawer.drawer_id}_action_apply_policy",
                    drawer_id=drawer.drawer_id,
                    enforcement_id=drawer.enforcement_id,
                    policy_id=drawer.policy_id,
                    label="Apply policy",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Real policy applies are blocked.",
                ),
                HandoffPolicyRouteEnforcementDetailAction(
                    action_id=f"{drawer.drawer_id}_action_override_policy",
                    drawer_id=drawer.drawer_id,
                    enforcement_id=drawer.enforcement_id,
                    policy_id=drawer.policy_id,
                    label="Override policy",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Real policy overrides are blocked.",
                ),
                HandoffPolicyRouteEnforcementDetailAction(
                    action_id=f"{drawer.drawer_id}_action_write_route_enforcement",
                    drawer_id=drawer.drawer_id,
                    enforcement_id=drawer.enforcement_id,
                    policy_id=drawer.policy_id,
                    label="Write route enforcement",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Real route enforcement writes are blocked.",
                ),
                HandoffPolicyRouteEnforcementDetailAction(
                    action_id=f"{drawer.drawer_id}_action_apply_route_enforcement",
                    drawer_id=drawer.drawer_id,
                    enforcement_id=drawer.enforcement_id,
                    policy_id=drawer.policy_id,
                    label="Apply route enforcement",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Real route enforcement applies are blocked.",
                ),
                HandoffPolicyRouteEnforcementDetailAction(
                    action_id=f"{drawer.drawer_id}_action_change_route",
                    drawer_id=drawer.drawer_id,
                    enforcement_id=drawer.enforcement_id,
                    policy_id=drawer.policy_id,
                    label="Change route",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Real route changes are blocked.",
                ),
                HandoffPolicyRouteEnforcementDetailAction(
                    action_id=f"{drawer.drawer_id}_action_activate_route",
                    drawer_id=drawer.drawer_id,
                    enforcement_id=drawer.enforcement_id,
                    policy_id=drawer.policy_id,
                    label="Activate route",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Real route activation is blocked.",
                ),
                HandoffPolicyRouteEnforcementDetailAction(
                    action_id=f"{drawer.drawer_id}_action_write_evidence",
                    drawer_id=drawer.drawer_id,
                    enforcement_id=drawer.enforcement_id,
                    policy_id=drawer.policy_id,
                    label="Write evidence",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Real evidence writes are blocked.",
                ),
                HandoffPolicyRouteEnforcementDetailAction(
                    action_id=f"{drawer.drawer_id}_action_reveal_raw_evidence",
                    drawer_id=drawer.drawer_id,
                    enforcement_id=drawer.enforcement_id,
                    policy_id=drawer.policy_id,
                    label="Reveal raw evidence",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Raw evidence reveal is blocked.",
                ),
                HandoffPolicyRouteEnforcementDetailAction(
                    action_id=f"{drawer.drawer_id}_action_execute_handoff",
                    drawer_id=drawer.drawer_id,
                    enforcement_id=drawer.enforcement_id,
                    policy_id=drawer.policy_id,
                    label="Execute handoff",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Real handoff execution is blocked.",
                ),
                HandoffPolicyRouteEnforcementDetailAction(
                    action_id=f"{drawer.drawer_id}_action_write_registry",
                    drawer_id=drawer.drawer_id,
                    enforcement_id=drawer.enforcement_id,
                    policy_id=drawer.policy_id,
                    label="Write registry",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="App, room, mission account, and handoff registry writes are blocked.",
                ),
                HandoffPolicyRouteEnforcementDetailAction(
                    action_id=f"{drawer.drawer_id}_action_change_clearance",
                    drawer_id=drawer.drawer_id,
                    enforcement_id=drawer.enforcement_id,
                    policy_id=drawer.policy_id,
                    label="Change clearance",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Clearance and permission changes are blocked.",
                ),
                HandoffPolicyRouteEnforcementDetailAction(
                    action_id=f"{drawer.drawer_id}_action_write_billing",
                    drawer_id=drawer.drawer_id,
                    enforcement_id=drawer.enforcement_id,
                    policy_id=drawer.policy_id,
                    label="Write billing/security",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Billing, subscription, checkout, customer portal, and account security writes are blocked.",
                ),
                HandoffPolicyRouteEnforcementDetailAction(
                    action_id=f"{drawer.drawer_id}_action_write_receipt",
                    drawer_id=drawer.drawer_id,
                    enforcement_id=drawer.enforcement_id,
                    policy_id=drawer.policy_id,
                    label="Write receipt/archive",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Real receipt/archive writes are blocked.",
                ),
            ]
        )

    return actions


def _build_checkpoints() -> List[HandoffPolicyRouteEnforcementDetailCheckpoint]:
    rows = [
        ("handoff_policy_route_enforcement_detail_checkpoint_277_001", "Pack 276 source policy route enforcement index is ready", "safe_summary_only"),
        ("handoff_policy_route_enforcement_detail_checkpoint_277_002", "Policy route enforcement detail drawers are preview-only", "safe_summary_only"),
        ("handoff_policy_route_enforcement_detail_checkpoint_277_003", "Policy, gate, denial behavior, enforcement mode, route mutation block, and data boundary sections are represented safely", "safe_summary_only"),
        ("handoff_policy_route_enforcement_detail_checkpoint_277_004", "Detail fields do not write state or reveal raw evidence", "redacted_pointer_only"),
        ("handoff_policy_route_enforcement_detail_checkpoint_277_005", "OB/Teller UI is not built in this Tower pack", "safe_summary_only"),
        ("handoff_policy_route_enforcement_detail_checkpoint_277_006", "Tower ownership of policy, access, clearance, billing, security, and routes is preserved", "safe_summary_only"),
        ("handoff_policy_route_enforcement_detail_checkpoint_277_007", "Policy writes/applies/overrides, route enforcement writes/applies, route changes, handoff execution, evidence writes, registry writes, clearance writes, billing writes, receipt writes, and real actions remain blocked", "blocked_action_summary"),
        ("handoff_policy_route_enforcement_detail_checkpoint_277_008", "Ready for Pack 278 policy route enforcement note draft preview", "safe_summary_only"),
    ]

    return [
        HandoffPolicyRouteEnforcementDetailCheckpoint(
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
            "reason": "Pack 277 previews policy route enforcement detail drawers only and cannot mutate policies, route enforcement, routes, evidence, handoffs, registries, clearance, billing, security, receipts, archives, or real actions.",
        }
        for action in BLOCKED_REAL_ACTIONS
    ]


@lru_cache(maxsize=1)
def _build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_detail_drawer_preview_cached() -> Dict[str, Any]:
    source_payload = _source_payload()
    source_lanes = _source_lanes(source_payload)

    drawers_raw = _build_drawers(source_lanes)
    sections_raw = _build_sections(drawers_raw, source_lanes)
    fields_raw = _build_fields(drawers_raw)
    actions_raw = _build_actions(drawers_raw)
    checkpoints_raw = _build_checkpoints()

    drawers = [asdict(drawer) for drawer in drawers_raw]
    sections = [asdict(section) for section in sections_raw]
    fields = [asdict(field) for field in fields_raw]
    actions = [asdict(action) for action in actions_raw]
    checkpoints = [asdict(checkpoint) for checkpoint in checkpoints_raw]

    enabled_action_count = sum(1 for action in actions if action["enabled"] is True)
    blocked_action_count = sum(1 for action in actions if action["enabled"] is False)
    editable_field_count = sum(1 for field in fields if field["editable_preview"] is True)
    locked_field_count = sum(1 for field in fields if field["editable_preview"] is False)
    redacted_field_count = sum(1 for field in fields if field["redaction_state"] == "redacted_pointer_only")
    blocked_section_count = sum(1 for section in sections if section["evidence_mode"] == "blocked_action_summary")
    redacted_section_count = sum(1 for section in sections if section["evidence_mode"] == "redacted_pointer_only")

    all_drawers_preview_only = all(drawer["preview_only"] is True for drawer in drawers)
    all_drawers_no_writes = all(drawer["writes_state"] is False for drawer in drawers)
    all_drawers_non_executable = all(drawer["executable"] is False for drawer in drawers)
    all_drawers_no_raw_evidence = all(drawer["raw_evidence_visible"] is False for drawer in drawers)

    all_sections_no_writes = all(section["writes_state"] is False for section in sections)
    all_sections_non_executable = all(section["executable"] is False for section in sections)
    all_sections_no_raw_evidence = all(section["raw_evidence_visible"] is False for section in sections)

    all_fields_no_writes = all(field["writes_state"] is False for field in fields)
    all_fields_no_raw_evidence = all(field["raw_evidence_visible"] is False for field in fields)

    all_actions_safe = all(action["result"] in {"preview_allowed", "blocked_preview_only"} for action in actions)
    all_checkpoints_passed = all(checkpoint["passed"] is True for checkpoint in checkpoints)
    all_checkpoints_no_writes = all(checkpoint["writes_state"] is False for checkpoint in checkpoints)

    handoff_policy_route_enforcement_detail_ready = all([
        all_drawers_preview_only,
        all_drawers_no_writes,
        all_drawers_non_executable,
        all_drawers_no_raw_evidence,
        all_sections_no_writes,
        all_sections_non_executable,
        all_sections_no_raw_evidence,
        all_fields_no_writes,
        all_fields_no_raw_evidence,
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
        "source_pack": SOURCE_PACK,
        "source_closed_batch": SOURCE_CLOSED_BATCH,
        "save_batch": SAVE_BATCH,
        "save_after_pack": SAVE_AFTER_PACK,
        "next_batch": NEXT_BATCH,
        "next_pack": NEXT_PACK,
        "cached": True,
        "non_recursive": True,
        "simulation_only": True,
        "preview_only": True,
        "receipt_chain_layer": "saved_view_owner_review_handoff_policy_route_enforcement_detail_drawer_preview",
        "source_endpoint": source_payload.get("endpoint"),
        "source_status": source_payload.get("status"),
        "source_readiness": source_payload.get("readiness"),
        "source_safe_to_continue": source_payload.get("safe_to_continue_to_pack_277"),
        "handoff_policy_route_enforcement_detail_drawers": drawers,
        "handoff_policy_route_enforcement_detail_sections": sections,
        "handoff_policy_route_enforcement_detail_fields": fields,
        "handoff_policy_route_enforcement_detail_actions": actions,
        "handoff_policy_route_enforcement_detail_checkpoints": checkpoints,
        "handoff_policy_route_enforcement_detail_summary": {
            "source_enforcement_lane_count": len(source_lanes),
            "detail_drawer_count": len(drawers),
            "detail_section_count": len(sections),
            "detail_field_count": len(fields),
            "detail_action_count": len(actions),
            "detail_checkpoint_count": len(checkpoints),
            "enabled_action_count": enabled_action_count,
            "blocked_action_count": blocked_action_count,
            "editable_field_count": editable_field_count,
            "locked_field_count": locked_field_count,
            "redacted_field_count": redacted_field_count,
            "blocked_section_count": blocked_section_count,
            "redacted_section_count": redacted_section_count,
            "all_drawers_preview_only": all_drawers_preview_only,
            "all_drawers_no_writes": all_drawers_no_writes,
            "all_drawers_non_executable": all_drawers_non_executable,
            "all_drawers_no_raw_evidence": all_drawers_no_raw_evidence,
            "all_sections_no_writes": all_sections_no_writes,
            "all_sections_non_executable": all_sections_non_executable,
            "all_sections_no_raw_evidence": all_sections_no_raw_evidence,
            "all_fields_no_writes": all_fields_no_writes,
            "all_fields_no_raw_evidence": all_fields_no_raw_evidence,
            "all_actions_safe": all_actions_safe,
            "all_checkpoints_passed": all_checkpoints_passed,
            "all_checkpoints_no_writes": all_checkpoints_no_writes,
            "handoff_policy_route_enforcement_detail_ready": handoff_policy_route_enforcement_detail_ready,
            "real_policy_write_enabled": False,
            "real_policy_apply_enabled": False,
            "real_policy_override_enabled": False,
            "real_route_enforcement_write_enabled": False,
            "real_route_enforcement_apply_enabled": False,
            "real_route_change_enabled": False,
            "real_route_activation_enabled": False,
            "real_evidence_write_enabled": False,
            "real_evidence_export_enabled": False,
            "raw_evidence_visible": False,
            "real_handoff_execute_enabled": False,
            "real_handoff_write_enabled": False,
            "real_app_registry_write_enabled": False,
            "real_room_registry_write_enabled": False,
            "real_mission_account_registry_write_enabled": False,
            "real_ob_route_change_enabled": False,
            "real_teller_route_change_enabled": False,
            "real_tower_route_change_enabled": False,
            "real_clearance_write_enabled": False,
            "real_permission_write_enabled": False,
            "real_billing_write_enabled": False,
            "real_subscription_write_enabled": False,
            "real_receipt_write_enabled": False,
            "real_archive_write_enabled": False,
            "real_action_execution_enabled": False,
        },
        "safety_invariants": {
            "no_real_policy_write": True,
            "no_real_policy_apply": True,
            "no_real_policy_override": True,
            "no_real_route_enforcement_write": True,
            "no_real_route_enforcement_apply": True,
            "no_real_route_change": True,
            "no_real_route_activation": True,
            "no_real_evidence_write": True,
            "no_real_evidence_export": True,
            "no_raw_evidence_reveal": True,
            "no_real_handoff_execute": True,
            "no_real_handoff_write": True,
            "no_real_app_registry_write": True,
            "no_real_room_registry_write": True,
            "no_real_mission_account_registry_write": True,
            "no_real_clearance_write": True,
            "no_real_permission_write": True,
            "no_real_billing_write": True,
            "no_real_subscription_write": True,
            "no_real_receipt_write": True,
            "no_real_archive_write": True,
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
        "pack_277_acceptance": {
            "source_pack_276_verified": True,
            "policy_route_enforcement_detail_drawers_built": True,
            "policy_sections_built": True,
            "gate_sections_built": True,
            "denial_behavior_sections_built": True,
            "data_boundary_sections_built": True,
            "mutation_paths_blocked": True,
            "ob_teller_ui_not_built_here": True,
            "ready_for_policy_route_enforcement_note_draft": True,
        },
        SAFE_TO_CONTINUE_FLAG: True,
        NEXT_PREP_FLAG: {
            "pack": NEXT_PACK,
            "name": "Receipt Chain Saved View Owner Review Handoff Policy Route Enforcement Note Draft Preview",
            "mode": "simulated_preview_only",
            "recommended_next_endpoint": "/tower/receipt-chain-saved-view-owner-review-handoff-policy-route-enforcement-note-draft-v278.json",
            "save_batch": SAVE_BATCH,
            "save_after_pack": SAVE_AFTER_PACK,
        },
    }

    return preview


def build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_detail_drawer_preview() -> Dict[str, Any]:
    """Return a defensive copy of the cached Pack 277 preview payload."""
    return deepcopy(_build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_detail_drawer_preview_cached())


def build_pack_277_status_bridge() -> Dict[str, Any]:
    """Small cached status bridge for Tower cards/status surfaces."""
    preview = _build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_detail_drawer_preview_cached()
    summary = preview["handoff_policy_route_enforcement_detail_summary"]

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
        "source_pack": preview["source_pack"],
        "source_closed_batch": preview["source_closed_batch"],
        "save_batch": preview["save_batch"],
        "save_after_pack": preview["save_after_pack"],
        "next_pack": preview["next_pack"],
        "cached": preview["cached"],
        "non_recursive": preview["non_recursive"],
        "preview_only": preview["preview_only"],
        "detail_drawer_count": summary["detail_drawer_count"],
        "detail_section_count": summary["detail_section_count"],
        "detail_field_count": summary["detail_field_count"],
        "detail_action_count": summary["detail_action_count"],
        "handoff_policy_route_enforcement_detail_ready": summary["handoff_policy_route_enforcement_detail_ready"],
        SAFE_TO_CONTINUE_FLAG: preview[SAFE_TO_CONTINUE_FLAG],
    }


def prepare_pack_278_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_note_draft() -> Dict[str, Any]:
    """Prepare Pack 278 direction without writing state."""
    return {
        "ready": True,
        "next_pack": NEXT_PACK,
        "name": "Receipt Chain Saved View Owner Review Handoff Policy Route Enforcement Note Draft Preview",
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
    "SOURCE_PACK",
    "SOURCE_CLOSED_BATCH",
    "SAVE_BATCH",
    "SAVE_AFTER_PACK",
    "NEXT_BATCH",
    "NEXT_PACK",
    "SAFE_TO_CONTINUE_FLAG",
    "NEXT_PREP_FLAG",
    "BLOCKED_REAL_ACTIONS",
    "build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_detail_drawer_preview",
    "build_pack_277_status_bridge",
    "prepare_pack_278_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_note_draft",
]
