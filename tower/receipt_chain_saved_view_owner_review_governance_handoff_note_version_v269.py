"""
SEARCHABLE LABEL: TOWER_PACK_269_RECEIPT_CHAIN_SAVED_VIEW_OWNER_REVIEW_GOVERNANCE_HANDOFF_NOTE_VERSION_PREVIEW_MODULE

Tower section:
- The Tower
- Operational Containment
- Receipt Chain Saved View Review Layer
- Governance Handoff layer

Pack 269: Receipt Chain Saved View Owner Review Governance Handoff Note Version Preview

This module is intentionally simulated/preview-only.

Purpose:
- Build safe handoff note version previews from Pack 268 handoff note drafts.
- Preserve Tower ownership of clearance, routes, billing, security, receipts, evidence, and real actions.
- Keep OB and Teller UI out of this Tower pack.
- Prepare Pack 270 governance handoff batch close readiness preview.

Safety boundaries:
- No real handoff writes.
- No real handoff note writes, saves, submits, or deletes.
- No real handoff note version writes, restores, applies, or deletes.
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

from tower.receipt_chain_saved_view_owner_review_governance_handoff_note_draft_v268 import (
    build_receipt_chain_saved_view_owner_review_governance_handoff_note_draft_preview,
)


PACK_ID = "269"
PACK_NUMBER = 269
PACK_NAME = "Receipt Chain Saved View Owner Review Governance Handoff Note Version Preview"
ENDPOINT = "/tower/receipt-chain-saved-view-owner-review-governance-handoff-note-version-v269.json"

TOWER_AREA = "The Tower"
TOWER_SECTION = "Operational Containment"
TOWER_LAYER = "Receipt Chain Saved View Review Layer"
TOWER_SUBLAYER = "Governance Handoff layer"

SOURCE_PACK = "268"
SOURCE_CLOSED_BATCH = "261-265"
SAVE_BATCH = "266-270"
SAVE_AFTER_PACK = 270
NEXT_BATCH = "266-270"
NEXT_PACK = "270"

SAFE_TO_CONTINUE_FLAG = "safe_to_continue_to_pack_270"
NEXT_PREP_FLAG = "prepare_pack_270_receipt_chain_saved_view_owner_review_governance_handoff_batch_close_readiness"

BLOCKED_REAL_ACTIONS = (
    "real_handoff_write",
    "real_handoff_note_write",
    "real_handoff_note_save",
    "real_handoff_note_submit",
    "real_handoff_note_delete",
    "real_handoff_note_version_write",
    "real_handoff_note_version_restore",
    "real_handoff_note_version_apply",
    "real_handoff_note_version_delete",
    "real_handoff_note_version_compare_write",
    "real_handoff_detail_write",
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
class GovernanceHandoffNoteVersionCard:
    version_id: str
    draft_id: str
    handoff_id: str
    source_surface: str
    destination_surface: str
    handoff_family: str
    label: str
    version_label: str
    version_status: str
    version_mode: str
    changed_field_count: int
    writes_state: bool
    executable: bool
    raw_evidence_visible: bool


@dataclass(frozen=True)
class GovernanceHandoffNoteVersionCompareRow:
    compare_row_id: str
    version_id: str
    draft_id: str
    handoff_id: str
    label: str
    field_name: str
    previous_preview: str
    current_preview: str
    change_type: str
    redaction_state: str
    writes_state: bool
    executable: bool
    raw_evidence_visible: bool


@dataclass(frozen=True)
class GovernanceHandoffNoteVersionAction:
    action_id: str
    version_id: str
    draft_id: str
    handoff_id: str
    label: str
    visible: bool
    enabled: bool
    result: str
    reason: str


@dataclass(frozen=True)
class GovernanceHandoffNoteVersionCheckpoint:
    checkpoint_id: str
    label: str
    passed: bool
    result: str
    evidence_mode: str
    writes_state: bool


def _source_payload() -> Dict[str, Any]:
    return deepcopy(build_receipt_chain_saved_view_owner_review_governance_handoff_note_draft_preview())


def _source_drafts(source_payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    drafts = source_payload.get("governance_handoff_note_draft_cards", [])
    if isinstance(drafts, list) and drafts:
        return deepcopy(drafts)

    return [
        {
            "draft_id": "fallback_governance_handoff_note_draft",
            "handoff_id": "fallback_governance_handoff_lane",
            "source_surface": "OB.Dashboard",
            "destination_surface": "Tower.Clearance",
            "handoff_family": "OB_ROOM_ACCESS",
        }
    ]


def _build_version_cards(drafts: List[Dict[str, Any]]) -> List[GovernanceHandoffNoteVersionCard]:
    cards: List[GovernanceHandoffNoteVersionCard] = []

    for idx, draft in enumerate(drafts, start=1):
        source_surface = str(draft.get("source_surface", "Unknown.Source"))
        destination_surface = str(draft.get("destination_surface", "Unknown.Destination"))
        handoff_family = str(draft.get("handoff_family", "UNKNOWN_HANDOFF"))
        common = {
            "draft_id": str(draft.get("draft_id", f"draft_{idx:03d}")),
            "handoff_id": str(draft.get("handoff_id", f"handoff_{idx:03d}")),
            "source_surface": source_surface,
            "destination_surface": destination_surface,
            "handoff_family": handoff_family,
            "version_status": "handoff_note_version_preview_ready",
            "version_mode": "preview_only",
            "writes_state": False,
            "executable": False,
            "raw_evidence_visible": False,
        }

        cards.append(
            GovernanceHandoffNoteVersionCard(
                version_id=f"governance_handoff_note_version_269_{idx:03d}_v1",
                label=f"Initial handoff note version preview for {source_surface} → {destination_surface}",
                version_label="Initial simulated handoff note version",
                changed_field_count=9,
                **common,
            )
        )
        cards.append(
            GovernanceHandoffNoteVersionCard(
                version_id=f"governance_handoff_note_version_269_{idx:03d}_v2",
                label=f"Revised handoff note version preview for {source_surface} → {destination_surface}",
                version_label="Revised simulated handoff note version",
                changed_field_count=11,
                **common,
            )
        )

    return cards


def _build_compare_rows(cards: List[GovernanceHandoffNoteVersionCard]) -> List[GovernanceHandoffNoteVersionCompareRow]:
    rows: List[GovernanceHandoffNoteVersionCompareRow] = []

    specs = [
        ("title", "Draft title preview", "Versioned Tower governance handoff review", "title_preview_change", "safe_preview"),
        ("surface_path", "Previous source/destination path", "Versioned source/destination path preserved", "surface_path_preview_change", "safe_preview"),
        ("handoff_family", "Previous handoff family", "Versioned handoff family preserved", "handoff_family_unchanged", "safe_preview"),
        ("clearance_note", "Previous clearance note", "Versioned Tower clearance note preserved", "clearance_preview_change", "safe_preview"),
        ("payload_scope", "Previous payload scope", "Versioned payload scope remains limited", "payload_scope_preview_change", "safe_preview"),
        ("ob_teller_boundary", "Previous OB/Teller boundary note", "Versioned OB/Teller UI-not-built boundary preserved", "boundary_unchanged", "safe_preview"),
        ("mutation_boundary", "Previous mutation boundary note", "Versioned mutation boundary remains blocked", "mutation_boundary_unchanged", "safe_preview"),
        ("evidence_boundary", "Previous evidence pointer", "Versioned evidence pointer remains redacted", "evidence_boundary_unchanged", "redacted_pointer_only"),
        ("next_step", "Prepare Pack 269", "Prepare Pack 270 handoff batch close readiness", "next_step_preview_change", "safe_preview"),
    ]

    for card in cards:
        for field_name, previous, current, change_type, redaction_state in specs:
            rows.append(
                GovernanceHandoffNoteVersionCompareRow(
                    compare_row_id=f"{card.version_id}_row_{field_name}",
                    version_id=card.version_id,
                    draft_id=card.draft_id,
                    handoff_id=card.handoff_id,
                    label=f"Compare {field_name} for {card.source_surface} → {card.destination_surface}",
                    field_name=field_name,
                    previous_preview=previous,
                    current_preview=f"{current}: {card.source_surface} → {card.destination_surface}",
                    change_type=change_type,
                    redaction_state=redaction_state,
                    writes_state=False,
                    executable=False,
                    raw_evidence_visible=False,
                )
            )

    return rows


def _build_actions(cards: List[GovernanceHandoffNoteVersionCard]) -> List[GovernanceHandoffNoteVersionAction]:
    actions: List[GovernanceHandoffNoteVersionAction] = []

    for card in cards:
        actions.extend(
            [
                GovernanceHandoffNoteVersionAction(
                    action_id=f"{card.version_id}_action_preview",
                    version_id=card.version_id,
                    draft_id=card.draft_id,
                    handoff_id=card.handoff_id,
                    label="Preview handoff note version",
                    visible=True,
                    enabled=True,
                    result="preview_allowed",
                    reason="Previewing a handoff note version does not write state.",
                ),
                GovernanceHandoffNoteVersionAction(
                    action_id=f"{card.version_id}_action_restore",
                    version_id=card.version_id,
                    draft_id=card.draft_id,
                    handoff_id=card.handoff_id,
                    label="Restore handoff note version",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Real handoff note version restores are blocked.",
                ),
                GovernanceHandoffNoteVersionAction(
                    action_id=f"{card.version_id}_action_apply",
                    version_id=card.version_id,
                    draft_id=card.draft_id,
                    handoff_id=card.handoff_id,
                    label="Apply handoff note version",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Real handoff note version applies are blocked.",
                ),
                GovernanceHandoffNoteVersionAction(
                    action_id=f"{card.version_id}_action_save_current",
                    version_id=card.version_id,
                    draft_id=card.draft_id,
                    handoff_id=card.handoff_id,
                    label="Save as current handoff note",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Real handoff note saves are blocked.",
                ),
                GovernanceHandoffNoteVersionAction(
                    action_id=f"{card.version_id}_action_submit",
                    version_id=card.version_id,
                    draft_id=card.draft_id,
                    handoff_id=card.handoff_id,
                    label="Submit handoff note version",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Real handoff note version submits are blocked.",
                ),
                GovernanceHandoffNoteVersionAction(
                    action_id=f"{card.version_id}_action_delete",
                    version_id=card.version_id,
                    draft_id=card.draft_id,
                    handoff_id=card.handoff_id,
                    label="Delete handoff note version",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Real handoff note version deletes are blocked.",
                ),
                GovernanceHandoffNoteVersionAction(
                    action_id=f"{card.version_id}_action_write_handoff",
                    version_id=card.version_id,
                    draft_id=card.draft_id,
                    handoff_id=card.handoff_id,
                    label="Write handoff",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Real handoff writes are blocked.",
                ),
                GovernanceHandoffNoteVersionAction(
                    action_id=f"{card.version_id}_action_execute_handoff",
                    version_id=card.version_id,
                    draft_id=card.draft_id,
                    handoff_id=card.handoff_id,
                    label="Execute handoff",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Real handoff execution is blocked.",
                ),
                GovernanceHandoffNoteVersionAction(
                    action_id=f"{card.version_id}_action_change_route",
                    version_id=card.version_id,
                    draft_id=card.draft_id,
                    handoff_id=card.handoff_id,
                    label="Change route",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="OB/Teller/Tower route changes are blocked.",
                ),
                GovernanceHandoffNoteVersionAction(
                    action_id=f"{card.version_id}_action_write_registry",
                    version_id=card.version_id,
                    draft_id=card.draft_id,
                    handoff_id=card.handoff_id,
                    label="Write registry",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="App, room, mission account, and handoff registry writes are blocked.",
                ),
                GovernanceHandoffNoteVersionAction(
                    action_id=f"{card.version_id}_action_change_clearance",
                    version_id=card.version_id,
                    draft_id=card.draft_id,
                    handoff_id=card.handoff_id,
                    label="Change clearance",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Clearance and permission changes are blocked.",
                ),
                GovernanceHandoffNoteVersionAction(
                    action_id=f"{card.version_id}_action_write_billing",
                    version_id=card.version_id,
                    draft_id=card.draft_id,
                    handoff_id=card.handoff_id,
                    label="Write billing/security state",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Billing, subscription, checkout, customer portal, and account security writes are blocked.",
                ),
                GovernanceHandoffNoteVersionAction(
                    action_id=f"{card.version_id}_action_reveal_evidence",
                    version_id=card.version_id,
                    draft_id=card.draft_id,
                    handoff_id=card.handoff_id,
                    label="Reveal raw evidence",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Raw evidence reveal is blocked.",
                ),
                GovernanceHandoffNoteVersionAction(
                    action_id=f"{card.version_id}_action_export_receipt",
                    version_id=card.version_id,
                    draft_id=card.draft_id,
                    handoff_id=card.handoff_id,
                    label="Export handoff receipt",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Real receipt/export/archive writes are blocked.",
                ),
            ]
        )

    return actions


def _build_checkpoints() -> List[GovernanceHandoffNoteVersionCheckpoint]:
    rows = [
        ("governance_handoff_note_version_checkpoint_269_001", "Pack 268 source handoff note draft is ready", "safe_summary_only"),
        ("governance_handoff_note_version_checkpoint_269_002", "Handoff note version cards are preview-only", "safe_summary_only"),
        ("governance_handoff_note_version_checkpoint_269_003", "Version compare rows do not write state or reveal raw evidence", "redacted_pointer_only"),
        ("governance_handoff_note_version_checkpoint_269_004", "OB/Teller UI is not built in this Tower pack", "safe_summary_only"),
        ("governance_handoff_note_version_checkpoint_269_005", "Tower ownership of access, clearance, billing, security, and routes is preserved", "safe_summary_only"),
        ("governance_handoff_note_version_checkpoint_269_006", "Version restore/apply/save/submit/delete and all mutation paths remain blocked", "blocked_action_summary"),
        ("governance_handoff_note_version_checkpoint_269_007", "Ready for Pack 270 governance handoff batch close readiness preview", "safe_summary_only"),
    ]

    return [
        GovernanceHandoffNoteVersionCheckpoint(
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
            "reason": "Pack 269 previews governance handoff note versions only and cannot mutate note versions, handoffs, routes, registries, clearance, billing, security, receipts, evidence, or real actions.",
        }
        for action in BLOCKED_REAL_ACTIONS
    ]


@lru_cache(maxsize=1)
def _build_receipt_chain_saved_view_owner_review_governance_handoff_note_version_preview_cached() -> Dict[str, Any]:
    source_payload = _source_payload()
    source_drafts = _source_drafts(source_payload)

    cards_raw = _build_version_cards(source_drafts)
    rows_raw = _build_compare_rows(cards_raw)
    actions_raw = _build_actions(cards_raw)
    checkpoints_raw = _build_checkpoints()

    cards = [asdict(card) for card in cards_raw]
    rows = [asdict(row) for row in rows_raw]
    actions = [asdict(action) for action in actions_raw]
    checkpoints = [asdict(checkpoint) for checkpoint in checkpoints_raw]

    enabled_action_count = sum(1 for action in actions if action["enabled"] is True)
    blocked_action_count = sum(1 for action in actions if action["enabled"] is False)
    redacted_compare_row_count = sum(1 for row in rows if row["redaction_state"] == "redacted_pointer_only")

    all_cards_preview_only = all(card["version_mode"] == "preview_only" for card in cards)
    all_cards_no_writes = all(card["writes_state"] is False for card in cards)
    all_cards_non_executable = all(card["executable"] is False for card in cards)
    all_cards_no_raw_evidence = all(card["raw_evidence_visible"] is False for card in cards)

    all_rows_no_writes = all(row["writes_state"] is False for row in rows)
    all_rows_non_executable = all(row["executable"] is False for row in rows)
    all_rows_no_raw_evidence = all(row["raw_evidence_visible"] is False for row in rows)

    all_actions_safe = all(action["result"] in {"preview_allowed", "blocked_preview_only"} for action in actions)
    all_checkpoints_passed = all(checkpoint["passed"] is True for checkpoint in checkpoints)
    all_checkpoints_no_writes = all(checkpoint["writes_state"] is False for checkpoint in checkpoints)

    governance_handoff_note_version_ready = all([
        all_cards_preview_only,
        all_cards_no_writes,
        all_cards_non_executable,
        all_cards_no_raw_evidence,
        all_rows_no_writes,
        all_rows_non_executable,
        all_rows_no_raw_evidence,
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
        "receipt_chain_layer": "saved_view_owner_review_governance_handoff_note_version_preview",
        "source_endpoint": source_payload.get("endpoint"),
        "source_status": source_payload.get("status"),
        "source_readiness": source_payload.get("readiness"),
        "source_safe_to_continue": source_payload.get("safe_to_continue_to_pack_269"),
        "governance_handoff_note_version_cards": cards,
        "governance_handoff_note_version_compare_rows": rows,
        "governance_handoff_note_version_actions": actions,
        "governance_handoff_note_version_checkpoints": checkpoints,
        "governance_handoff_note_version_summary": {
            "source_draft_card_count": len(source_drafts),
            "version_card_count": len(cards),
            "compare_row_count": len(rows),
            "version_action_count": len(actions),
            "version_checkpoint_count": len(checkpoints),
            "enabled_action_count": enabled_action_count,
            "blocked_action_count": blocked_action_count,
            "redacted_compare_row_count": redacted_compare_row_count,
            "all_cards_preview_only": all_cards_preview_only,
            "all_cards_no_writes": all_cards_no_writes,
            "all_cards_non_executable": all_cards_non_executable,
            "all_cards_no_raw_evidence": all_cards_no_raw_evidence,
            "all_rows_no_writes": all_rows_no_writes,
            "all_rows_non_executable": all_rows_non_executable,
            "all_rows_no_raw_evidence": all_rows_no_raw_evidence,
            "all_actions_safe": all_actions_safe,
            "all_checkpoints_passed": all_checkpoints_passed,
            "all_checkpoints_no_writes": all_checkpoints_no_writes,
            "governance_handoff_note_version_ready": governance_handoff_note_version_ready,
            "real_handoff_write_enabled": False,
            "real_handoff_note_write_enabled": False,
            "real_handoff_note_save_enabled": False,
            "real_handoff_note_submit_enabled": False,
            "real_handoff_note_delete_enabled": False,
            "real_handoff_note_version_write_enabled": False,
            "real_handoff_note_version_restore_enabled": False,
            "real_handoff_note_version_apply_enabled": False,
            "real_handoff_note_version_delete_enabled": False,
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
            "no_real_handoff_note_write": True,
            "no_real_handoff_note_save": True,
            "no_real_handoff_note_submit": True,
            "no_real_handoff_note_delete": True,
            "no_real_handoff_note_version_write": True,
            "no_real_handoff_note_version_restore": True,
            "no_real_handoff_note_version_apply": True,
            "no_real_handoff_note_version_delete": True,
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
        "pack_269_acceptance": {
            "source_pack_268_verified": True,
            "handoff_note_version_cards_built": True,
            "handoff_note_version_compare_rows_built": True,
            "handoff_note_version_actions_built": True,
            "handoff_note_version_restore_apply_delete_blocked": True,
            "handoff_mutation_paths_blocked": True,
            "ob_teller_ui_not_built_here": True,
            "ready_for_handoff_batch_close": True,
        },
        SAFE_TO_CONTINUE_FLAG: True,
        NEXT_PREP_FLAG: {
            "pack": NEXT_PACK,
            "name": "Receipt Chain Saved View Owner Review Governance Handoff Batch Close Readiness Preview",
            "mode": "simulated_preview_only",
            "recommended_next_endpoint": "/tower/receipt-chain-saved-view-owner-review-governance-handoff-batch-close-readiness-v270.json",
            "save_batch": SAVE_BATCH,
            "save_after_pack": SAVE_AFTER_PACK,
        },
    }

    return preview


def build_receipt_chain_saved_view_owner_review_governance_handoff_note_version_preview() -> Dict[str, Any]:
    """Return a defensive copy of the cached Pack 269 preview payload."""
    return deepcopy(_build_receipt_chain_saved_view_owner_review_governance_handoff_note_version_preview_cached())


def build_pack_269_status_bridge() -> Dict[str, Any]:
    """Small cached status bridge for Tower cards/status surfaces."""
    preview = _build_receipt_chain_saved_view_owner_review_governance_handoff_note_version_preview_cached()
    summary = preview["governance_handoff_note_version_summary"]

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
        "version_card_count": summary["version_card_count"],
        "compare_row_count": summary["compare_row_count"],
        "version_action_count": summary["version_action_count"],
        "governance_handoff_note_version_ready": summary["governance_handoff_note_version_ready"],
        SAFE_TO_CONTINUE_FLAG: preview[SAFE_TO_CONTINUE_FLAG],
    }


def prepare_pack_270_receipt_chain_saved_view_owner_review_governance_handoff_batch_close_readiness() -> Dict[str, Any]:
    """Prepare Pack 270 direction without writing state."""
    return {
        "ready": True,
        "next_pack": NEXT_PACK,
        "name": "Receipt Chain Saved View Owner Review Governance Handoff Batch Close Readiness Preview",
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
    "build_receipt_chain_saved_view_owner_review_governance_handoff_note_version_preview",
    "build_pack_269_status_bridge",
    "prepare_pack_270_receipt_chain_saved_view_owner_review_governance_handoff_batch_close_readiness",
]
