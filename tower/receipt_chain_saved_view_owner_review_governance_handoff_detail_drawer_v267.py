"""
SEARCHABLE LABEL: TOWER_PACK_267_RECEIPT_CHAIN_SAVED_VIEW_OWNER_REVIEW_GOVERNANCE_HANDOFF_DETAIL_DRAWER_PREVIEW_MODULE

Tower section:
- The Tower
- Operational Containment
- Receipt Chain Saved View Review Layer
- Governance Handoff layer

Pack 267: Receipt Chain Saved View Owner Review Governance Handoff Detail Drawer Preview

This module is intentionally simulated/preview-only.

Purpose:
- Expand Pack 266 governance handoff index lanes into safe detail drawers.
- Show Tower-owned handoff details for OB rooms, OB mission accounts, Teller surfaces, Tower-owned access/billing/security surfaces, and receipt/proof lanes.
- Preserve the rule that OB/Teller UI is not built in this Tower pack.
- Prepare Pack 268 governance handoff note draft preview.

Safety boundaries:
- No real handoff writes.
- No real handoff detail state writes.
- No real app/room/account registry writes.
- No real OB route changes.
- No real Teller route changes.
- No real Tower route changes.
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

from tower.receipt_chain_saved_view_owner_review_governance_handoff_index_v266 import (
    build_receipt_chain_saved_view_owner_review_governance_handoff_index_preview,
)


PACK_ID = "267"
PACK_NUMBER = 267
PACK_NAME = "Receipt Chain Saved View Owner Review Governance Handoff Detail Drawer Preview"
ENDPOINT = "/tower/receipt-chain-saved-view-owner-review-governance-handoff-detail-drawer-v267.json"

TOWER_AREA = "The Tower"
TOWER_SECTION = "Operational Containment"
TOWER_LAYER = "Receipt Chain Saved View Review Layer"
TOWER_SUBLAYER = "Governance Handoff layer"

SOURCE_PACK = "266"
SOURCE_CLOSED_BATCH = "261-265"
SAVE_BATCH = "266-270"
SAVE_AFTER_PACK = 270
NEXT_BATCH = "266-270"
NEXT_PACK = "268"

SAFE_TO_CONTINUE_FLAG = "safe_to_continue_to_pack_268"
NEXT_PREP_FLAG = "prepare_pack_268_receipt_chain_saved_view_owner_review_governance_handoff_note_draft"

BLOCKED_REAL_ACTIONS = (
    "real_handoff_write",
    "real_handoff_detail_write",
    "real_handoff_detail_state_write",
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
class GovernanceHandoffDetailDrawer:
    drawer_id: str
    handoff_id: str
    source_surface: str
    destination_surface: str
    handoff_family: str
    label: str
    drawer_status: str
    clearance_required: str
    payload_mode: str
    preview_only: bool
    writes_state: bool
    executable: bool
    raw_evidence_visible: bool


@dataclass(frozen=True)
class GovernanceHandoffDetailSection:
    section_id: str
    drawer_id: str
    handoff_id: str
    label: str
    section_type: str
    summary: str
    evidence_mode: str
    writes_state: bool
    executable: bool
    raw_evidence_visible: bool


@dataclass(frozen=True)
class GovernanceHandoffDetailField:
    field_id: str
    drawer_id: str
    handoff_id: str
    label: str
    field_type: str
    preview_value: str
    redaction_state: str
    editable_preview: bool
    writes_state: bool
    raw_evidence_visible: bool


@dataclass(frozen=True)
class GovernanceHandoffDetailAction:
    action_id: str
    drawer_id: str
    handoff_id: str
    label: str
    visible: bool
    enabled: bool
    result: str
    reason: str


@dataclass(frozen=True)
class GovernanceHandoffDetailCheckpoint:
    checkpoint_id: str
    label: str
    passed: bool
    result: str
    evidence_mode: str
    writes_state: bool


def _source_payload() -> Dict[str, Any]:
    return deepcopy(build_receipt_chain_saved_view_owner_review_governance_handoff_index_preview())


def _source_lanes(source_payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    lanes = source_payload.get("governance_handoff_index_lanes", [])
    if isinstance(lanes, list) and lanes:
        return deepcopy(lanes)

    return [
        {
            "handoff_id": "fallback_governance_handoff_lane",
            "source_surface": "OB.Dashboard",
            "destination_surface": "Tower.Clearance",
            "handoff_family": "OB_ROOM_ACCESS",
            "label": "Fallback governance handoff lane",
            "purpose": "Fallback safe detail drawer.",
            "clearance_required": "tower_user_clearance",
            "allowed_payload_mode": "safe_status_only",
            "forbidden_payload_summary": "No raw evidence or mutation allowed.",
        }
    ]


def _build_drawers(lanes: List[Dict[str, Any]]) -> List[GovernanceHandoffDetailDrawer]:
    drawers: List[GovernanceHandoffDetailDrawer] = []

    for idx, lane in enumerate(lanes, start=1):
        drawers.append(
            GovernanceHandoffDetailDrawer(
                drawer_id=f"governance_handoff_detail_drawer_267_{idx:03d}",
                handoff_id=str(lane.get("handoff_id", f"handoff_{idx:03d}")),
                source_surface=str(lane.get("source_surface", "Unknown.Source")),
                destination_surface=str(lane.get("destination_surface", "Unknown.Destination")),
                handoff_family=str(lane.get("handoff_family", "UNKNOWN_HANDOFF")),
                label=f"Governance handoff detail drawer for {lane.get('label', 'handoff lane')}",
                drawer_status="handoff_detail_drawer_preview_ready",
                clearance_required=str(lane.get("clearance_required", "tower_clearance")),
                payload_mode=str(lane.get("allowed_payload_mode", "safe_summary_only")),
                preview_only=True,
                writes_state=False,
                executable=False,
                raw_evidence_visible=False,
            )
        )

    return drawers


def _build_sections(drawers: List[GovernanceHandoffDetailDrawer], lanes: List[Dict[str, Any]]) -> List[GovernanceHandoffDetailSection]:
    lane_by_id = {str(lane.get("handoff_id")): lane for lane in lanes}
    sections: List[GovernanceHandoffDetailSection] = []

    for drawer in drawers:
        lane = lane_by_id.get(drawer.handoff_id, {})
        forbidden = str(lane.get("forbidden_payload_summary", "Forbidden payload remains blocked."))

        sections.extend(
            [
                GovernanceHandoffDetailSection(
                    section_id=f"{drawer.drawer_id}_section_surface_path",
                    drawer_id=drawer.drawer_id,
                    handoff_id=drawer.handoff_id,
                    label="Surface path",
                    section_type="surface_path",
                    summary=f"{drawer.source_surface} can reference {drawer.destination_surface} only through Tower-controlled handoff rules.",
                    evidence_mode="safe_summary_only",
                    writes_state=False,
                    executable=False,
                    raw_evidence_visible=False,
                ),
                GovernanceHandoffDetailSection(
                    section_id=f"{drawer.drawer_id}_section_clearance",
                    drawer_id=drawer.drawer_id,
                    handoff_id=drawer.handoff_id,
                    label="Clearance requirement",
                    section_type="clearance_requirement",
                    summary=f"Required clearance: {drawer.clearance_required}. Tower owns the decision; app surfaces can only display approved state.",
                    evidence_mode="safe_summary_only",
                    writes_state=False,
                    executable=False,
                    raw_evidence_visible=False,
                ),
                GovernanceHandoffDetailSection(
                    section_id=f"{drawer.drawer_id}_section_payload_scope",
                    drawer_id=drawer.drawer_id,
                    handoff_id=drawer.handoff_id,
                    label="Allowed payload scope",
                    section_type="payload_scope",
                    summary=f"Allowed payload mode: {drawer.payload_mode}. Payload is summary/pointer/status only.",
                    evidence_mode="safe_summary_only",
                    writes_state=False,
                    executable=False,
                    raw_evidence_visible=False,
                ),
                GovernanceHandoffDetailSection(
                    section_id=f"{drawer.drawer_id}_section_forbidden_payload",
                    drawer_id=drawer.drawer_id,
                    handoff_id=drawer.handoff_id,
                    label="Forbidden payload boundary",
                    section_type="forbidden_payload_boundary",
                    summary=forbidden,
                    evidence_mode="blocked_action_summary",
                    writes_state=False,
                    executable=False,
                    raw_evidence_visible=False,
                ),
                GovernanceHandoffDetailSection(
                    section_id=f"{drawer.drawer_id}_section_route_boundary",
                    drawer_id=drawer.drawer_id,
                    handoff_id=drawer.handoff_id,
                    label="Route mutation boundary",
                    section_type="route_boundary",
                    summary="No OB, Teller, or Tower route changes occur in this preview. Route protection remains Tower-controlled.",
                    evidence_mode="blocked_action_summary",
                    writes_state=False,
                    executable=False,
                    raw_evidence_visible=False,
                ),
                GovernanceHandoffDetailSection(
                    section_id=f"{drawer.drawer_id}_section_registry_boundary",
                    drawer_id=drawer.drawer_id,
                    handoff_id=drawer.handoff_id,
                    label="Registry mutation boundary",
                    section_type="registry_boundary",
                    summary="No app, room, mission account, entity, or handoff registry writes occur in this preview.",
                    evidence_mode="blocked_action_summary",
                    writes_state=False,
                    executable=False,
                    raw_evidence_visible=False,
                ),
                GovernanceHandoffDetailSection(
                    section_id=f"{drawer.drawer_id}_section_evidence_boundary",
                    drawer_id=drawer.drawer_id,
                    handoff_id=drawer.handoff_id,
                    label="Evidence boundary",
                    section_type="evidence_boundary",
                    summary="Raw evidence remains hidden. Evidence export and receipt/archive writes are blocked.",
                    evidence_mode="redacted_pointer_only",
                    writes_state=False,
                    executable=False,
                    raw_evidence_visible=False,
                ),
                GovernanceHandoffDetailSection(
                    section_id=f"{drawer.drawer_id}_section_next_step",
                    drawer_id=drawer.drawer_id,
                    handoff_id=drawer.handoff_id,
                    label="Next step preview",
                    section_type="next_step_preview",
                    summary="Prepares Pack 268 governance handoff note draft preview without writing notes.",
                    evidence_mode="safe_summary_only",
                    writes_state=False,
                    executable=False,
                    raw_evidence_visible=False,
                ),
            ]
        )

    return sections


def _build_fields(drawers: List[GovernanceHandoffDetailDrawer]) -> List[GovernanceHandoffDetailField]:
    fields: List[GovernanceHandoffDetailField] = []

    for drawer in drawers:
        fields.extend(
            [
                GovernanceHandoffDetailField(
                    field_id=f"{drawer.drawer_id}_field_source_surface",
                    drawer_id=drawer.drawer_id,
                    handoff_id=drawer.handoff_id,
                    label="Source surface",
                    field_type="locked_summary",
                    preview_value=drawer.source_surface,
                    redaction_state="safe_preview",
                    editable_preview=False,
                    writes_state=False,
                    raw_evidence_visible=False,
                ),
                GovernanceHandoffDetailField(
                    field_id=f"{drawer.drawer_id}_field_destination_surface",
                    drawer_id=drawer.drawer_id,
                    handoff_id=drawer.handoff_id,
                    label="Destination surface",
                    field_type="locked_summary",
                    preview_value=drawer.destination_surface,
                    redaction_state="safe_preview",
                    editable_preview=False,
                    writes_state=False,
                    raw_evidence_visible=False,
                ),
                GovernanceHandoffDetailField(
                    field_id=f"{drawer.drawer_id}_field_handoff_family",
                    drawer_id=drawer.drawer_id,
                    handoff_id=drawer.handoff_id,
                    label="Handoff family",
                    field_type="locked_summary",
                    preview_value=drawer.handoff_family,
                    redaction_state="safe_preview",
                    editable_preview=False,
                    writes_state=False,
                    raw_evidence_visible=False,
                ),
                GovernanceHandoffDetailField(
                    field_id=f"{drawer.drawer_id}_field_clearance",
                    drawer_id=drawer.drawer_id,
                    handoff_id=drawer.handoff_id,
                    label="Clearance required",
                    field_type="locked_summary",
                    preview_value=drawer.clearance_required,
                    redaction_state="safe_preview",
                    editable_preview=False,
                    writes_state=False,
                    raw_evidence_visible=False,
                ),
                GovernanceHandoffDetailField(
                    field_id=f"{drawer.drawer_id}_field_payload_mode",
                    drawer_id=drawer.drawer_id,
                    handoff_id=drawer.handoff_id,
                    label="Payload mode",
                    field_type="locked_summary",
                    preview_value=drawer.payload_mode,
                    redaction_state="safe_preview",
                    editable_preview=False,
                    writes_state=False,
                    raw_evidence_visible=False,
                ),
                GovernanceHandoffDetailField(
                    field_id=f"{drawer.drawer_id}_field_owner_note_preview",
                    drawer_id=drawer.drawer_id,
                    handoff_id=drawer.handoff_id,
                    label="Owner note preview",
                    field_type="textarea_preview",
                    preview_value=f"Tower can preview this handoff lane from {drawer.source_surface} to {drawer.destination_surface}; no state is written.",
                    redaction_state="safe_preview",
                    editable_preview=True,
                    writes_state=False,
                    raw_evidence_visible=False,
                ),
                GovernanceHandoffDetailField(
                    field_id=f"{drawer.drawer_id}_field_evidence_pointer",
                    drawer_id=drawer.drawer_id,
                    handoff_id=drawer.handoff_id,
                    label="Evidence pointer",
                    field_type="redacted_pointer",
                    preview_value="redacted_pointer_only",
                    redaction_state="redacted_pointer_only",
                    editable_preview=False,
                    writes_state=False,
                    raw_evidence_visible=False,
                ),
            ]
        )

    return fields


def _build_actions(drawers: List[GovernanceHandoffDetailDrawer]) -> List[GovernanceHandoffDetailAction]:
    actions: List[GovernanceHandoffDetailAction] = []

    for drawer in drawers:
        actions.extend(
            [
                GovernanceHandoffDetailAction(
                    action_id=f"{drawer.drawer_id}_action_preview",
                    drawer_id=drawer.drawer_id,
                    handoff_id=drawer.handoff_id,
                    label="Preview handoff detail drawer",
                    visible=True,
                    enabled=True,
                    result="preview_allowed",
                    reason="Previewing a handoff detail drawer does not write state.",
                ),
                GovernanceHandoffDetailAction(
                    action_id=f"{drawer.drawer_id}_action_write_detail",
                    drawer_id=drawer.drawer_id,
                    handoff_id=drawer.handoff_id,
                    label="Write handoff detail",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Real handoff detail writes are blocked.",
                ),
                GovernanceHandoffDetailAction(
                    action_id=f"{drawer.drawer_id}_action_execute_handoff",
                    drawer_id=drawer.drawer_id,
                    handoff_id=drawer.handoff_id,
                    label="Execute handoff",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Real handoff execution is blocked.",
                ),
                GovernanceHandoffDetailAction(
                    action_id=f"{drawer.drawer_id}_action_change_route",
                    drawer_id=drawer.drawer_id,
                    handoff_id=drawer.handoff_id,
                    label="Change route",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="OB/Teller/Tower route changes are blocked.",
                ),
                GovernanceHandoffDetailAction(
                    action_id=f"{drawer.drawer_id}_action_write_registry",
                    drawer_id=drawer.drawer_id,
                    handoff_id=drawer.handoff_id,
                    label="Write registry",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="App, room, mission account, and handoff registry writes are blocked.",
                ),
                GovernanceHandoffDetailAction(
                    action_id=f"{drawer.drawer_id}_action_change_clearance",
                    drawer_id=drawer.drawer_id,
                    handoff_id=drawer.handoff_id,
                    label="Change clearance",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Clearance and permission changes are blocked.",
                ),
                GovernanceHandoffDetailAction(
                    action_id=f"{drawer.drawer_id}_action_write_billing",
                    drawer_id=drawer.drawer_id,
                    handoff_id=drawer.handoff_id,
                    label="Write billing/security state",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Billing, subscription, checkout, customer portal, and account security writes are blocked.",
                ),
                GovernanceHandoffDetailAction(
                    action_id=f"{drawer.drawer_id}_action_reveal_evidence",
                    drawer_id=drawer.drawer_id,
                    handoff_id=drawer.handoff_id,
                    label="Reveal raw evidence",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Raw evidence reveal is blocked.",
                ),
                GovernanceHandoffDetailAction(
                    action_id=f"{drawer.drawer_id}_action_export_receipt",
                    drawer_id=drawer.drawer_id,
                    handoff_id=drawer.handoff_id,
                    label="Export handoff receipt",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Real receipt/export/archive writes are blocked.",
                ),
            ]
        )

    return actions


def _build_checkpoints() -> List[GovernanceHandoffDetailCheckpoint]:
    rows = [
        ("governance_handoff_detail_checkpoint_267_001", "Pack 266 source handoff index is ready", "safe_summary_only"),
        ("governance_handoff_detail_checkpoint_267_002", "Handoff detail drawers are preview-only", "safe_summary_only"),
        ("governance_handoff_detail_checkpoint_267_003", "Detail sections preserve Tower ownership of clearance, routes, billing, and security", "safe_summary_only"),
        ("governance_handoff_detail_checkpoint_267_004", "Detail fields do not write state or reveal raw evidence", "redacted_pointer_only"),
        ("governance_handoff_detail_checkpoint_267_005", "OB/Teller UI is not built in this Tower pack", "safe_summary_only"),
        ("governance_handoff_detail_checkpoint_267_006", "Handoff, route, registry, clearance, billing, receipt, evidence, and real action mutations remain blocked", "blocked_action_summary"),
        ("governance_handoff_detail_checkpoint_267_007", "Ready for Pack 268 governance handoff note draft preview", "safe_summary_only"),
    ]

    return [
        GovernanceHandoffDetailCheckpoint(
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
            "reason": "Pack 267 previews governance handoff detail drawers only and cannot mutate handoffs, routes, registries, clearance, billing, security, receipts, evidence, or real actions.",
        }
        for action in BLOCKED_REAL_ACTIONS
    ]


@lru_cache(maxsize=1)
def _build_receipt_chain_saved_view_owner_review_governance_handoff_detail_drawer_preview_cached() -> Dict[str, Any]:
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

    governance_handoff_detail_ready = all([
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
        "receipt_chain_layer": "saved_view_owner_review_governance_handoff_detail_drawer_preview",
        "source_endpoint": source_payload.get("endpoint"),
        "source_status": source_payload.get("status"),
        "source_readiness": source_payload.get("readiness"),
        "source_safe_to_continue": source_payload.get("safe_to_continue_to_pack_267"),
        "governance_handoff_detail_drawers": drawers,
        "governance_handoff_detail_sections": sections,
        "governance_handoff_detail_fields": fields,
        "governance_handoff_detail_actions": actions,
        "governance_handoff_detail_checkpoints": checkpoints,
        "governance_handoff_detail_summary": {
            "source_handoff_lane_count": len(source_lanes),
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
            "governance_handoff_detail_ready": governance_handoff_detail_ready,
            "real_handoff_write_enabled": False,
            "real_handoff_detail_write_enabled": False,
            "real_handoff_execute_enabled": False,
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
            "real_evidence_export_enabled": False,
            "raw_evidence_visible": False,
            "real_action_execution_enabled": False,
        },
        "safety_invariants": {
            "no_real_handoff_write": True,
            "no_real_handoff_detail_write": True,
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
        "pack_267_acceptance": {
            "source_pack_266_verified": True,
            "handoff_detail_drawers_built": True,
            "handoff_detail_sections_built": True,
            "handoff_detail_fields_built": True,
            "handoff_mutation_paths_blocked": True,
            "ob_teller_ui_not_built_here": True,
            "ready_for_handoff_note_draft": True,
        },
        SAFE_TO_CONTINUE_FLAG: True,
        NEXT_PREP_FLAG: {
            "pack": NEXT_PACK,
            "name": "Receipt Chain Saved View Owner Review Governance Handoff Note Draft Preview",
            "mode": "simulated_preview_only",
            "recommended_next_endpoint": "/tower/receipt-chain-saved-view-owner-review-governance-handoff-note-draft-v268.json",
            "save_batch": SAVE_BATCH,
            "save_after_pack": SAVE_AFTER_PACK,
        },
    }

    return preview


def build_receipt_chain_saved_view_owner_review_governance_handoff_detail_drawer_preview() -> Dict[str, Any]:
    """Return a defensive copy of the cached Pack 267 preview payload."""
    return deepcopy(_build_receipt_chain_saved_view_owner_review_governance_handoff_detail_drawer_preview_cached())


def build_pack_267_status_bridge() -> Dict[str, Any]:
    """Small cached status bridge for Tower cards/status surfaces."""
    preview = _build_receipt_chain_saved_view_owner_review_governance_handoff_detail_drawer_preview_cached()
    summary = preview["governance_handoff_detail_summary"]

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
        "governance_handoff_detail_ready": summary["governance_handoff_detail_ready"],
        SAFE_TO_CONTINUE_FLAG: preview[SAFE_TO_CONTINUE_FLAG],
    }


def prepare_pack_268_receipt_chain_saved_view_owner_review_governance_handoff_note_draft() -> Dict[str, Any]:
    """Prepare Pack 268 direction without writing state."""
    return {
        "ready": True,
        "next_pack": NEXT_PACK,
        "name": "Receipt Chain Saved View Owner Review Governance Handoff Note Draft Preview",
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
    "build_receipt_chain_saved_view_owner_review_governance_handoff_detail_drawer_preview",
    "build_pack_267_status_bridge",
    "prepare_pack_268_receipt_chain_saved_view_owner_review_governance_handoff_note_draft",
]
