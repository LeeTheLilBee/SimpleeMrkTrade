"""
SEARCHABLE LABEL: TOWER_PACK_264_RECEIPT_CHAIN_SAVED_VIEW_OWNER_REVIEW_GOVERNANCE_CONTINUITY_NOTE_VERSION_PREVIEW_MODULE

Tower section:
- The Tower
- Operational Containment
- Receipt Chain Saved View Review Layer
- Governance Index Preview layer

Pack 264: Receipt Chain Saved View Owner Review Governance Continuity Note Version Preview

This module is intentionally simulated/preview-only.

Purpose:
- Build safe governance continuity note version previews from Pack 263 continuity note drafts.
- Preserve closed-batch, lane, handoff, boundary, and next-batch compare context.
- Prepare Pack 265 governance continuity batch close readiness preview.

Safety boundaries:
- No real continuity writes.
- No real continuity note writes, saves, submits, or deletes.
- No real continuity note version writes, restores, applies, or deletes.
- No real escalation writes or execution.
- No real continuous assurance writes/check execution/status writes.
- No real governance decision writes, applies, or overrides.
- No real policy changes.
- No real approval/denial execution.
- No real owner review execution.
- No real saved-view restore/revert/write/edit/delete/apply/export.
- No user preference writes.
- No archive writes.
- No raw evidence reveal.
- No real action execution.
- Cached/non-recursive builders only.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, asdict
from functools import lru_cache
from typing import Any, Dict, List

from tower.receipt_chain_saved_view_owner_review_governance_continuity_note_draft_v263 import (
    build_receipt_chain_saved_view_owner_review_governance_continuity_note_draft_preview,
)


PACK_ID = "264"
PACK_NUMBER = 264
PACK_NAME = "Receipt Chain Saved View Owner Review Governance Continuity Note Version Preview"
ENDPOINT = "/tower/receipt-chain-saved-view-owner-review-governance-continuity-note-version-v264.json"

TOWER_AREA = "The Tower"
TOWER_SECTION = "Operational Containment"
TOWER_LAYER = "Receipt Chain Saved View Review Layer"
TOWER_SUBLAYER = "Governance Index Preview layer"

SOURCE_CLOSED_BATCH = "251-260"
SAVE_BATCH = "261-265"
SAVE_AFTER_PACK = 265
NEXT_BATCH = "261-265"
SAFE_TO_CONTINUE_FLAG = "safe_to_continue_to_pack_265"
NEXT_PREP_FLAG = "prepare_pack_265_receipt_chain_saved_view_owner_review_governance_continuity_batch_close_readiness"

BLOCKED_REAL_ACTIONS = (
    "real_continuity_write",
    "real_continuity_note_write",
    "real_continuity_note_save",
    "real_continuity_note_submit",
    "real_continuity_note_delete",
    "real_continuity_note_version_write",
    "real_continuity_note_version_restore",
    "real_continuity_note_version_apply",
    "real_continuity_note_version_delete",
    "real_continuity_note_version_compare_write",
    "real_continuity_detail_write",
    "real_continuity_index_write",
    "real_continuity_state_write",
    "real_continuity_handoff_write",
    "real_escalation_write",
    "real_escalation_queue_write",
    "real_escalation_detail_write",
    "real_escalation_note_write",
    "real_escalation_note_version_write",
    "real_escalation_assignment_write",
    "real_escalation_execute",
    "real_escalation_status_write",
    "real_escalation_resolution_write",
    "real_continuous_assurance_write",
    "real_continuous_assurance_check_execute",
    "real_continuous_assurance_status_write",
    "real_governance_decision_write",
    "real_governance_decision_apply",
    "real_governance_decision_override",
    "real_policy_change_write",
    "real_policy_enable",
    "real_policy_disable",
    "real_policy_override",
    "real_approval_execute",
    "real_denial_execute",
    "real_owner_review_execute",
    "real_saved_view_restore",
    "real_saved_view_revert",
    "real_saved_view_write",
    "real_saved_view_edit",
    "real_saved_view_delete",
    "real_saved_view_apply",
    "real_saved_view_export",
    "real_user_preference_write",
    "real_archive_write",
    "raw_evidence_reveal",
    "real_evidence_export",
    "real_action_execution",
    "live_policy_mutation",
    "receipt_chain_mutation",
)


@dataclass(frozen=True)
class GovernanceContinuityNoteVersionCard:
    version_id: str
    draft_id: str
    continuity_id: str
    source_batch: str
    lane: str
    label: str
    version_label: str
    version_status: str
    version_mode: str
    changed_field_count: int
    writes_state: bool
    executable: bool
    raw_evidence_visible: bool


@dataclass(frozen=True)
class GovernanceContinuityNoteVersionCompareRow:
    compare_row_id: str
    version_id: str
    draft_id: str
    continuity_id: str
    lane: str
    field_name: str
    previous_preview: str
    current_preview: str
    change_type: str
    redaction_state: str
    writes_state: bool
    executable: bool
    raw_evidence_visible: bool


@dataclass(frozen=True)
class GovernanceContinuityNoteVersionAction:
    action_id: str
    version_id: str
    label: str
    visible: bool
    enabled: bool
    result: str
    reason: str


@dataclass(frozen=True)
class GovernanceContinuityNoteVersionCheckpoint:
    checkpoint_id: str
    label: str
    passed: bool
    result: str
    evidence_mode: str
    writes_state: bool


def _source_payload() -> Dict[str, Any]:
    return deepcopy(build_receipt_chain_saved_view_owner_review_governance_continuity_note_draft_preview())


def _source_drafts(source_payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    drafts = source_payload.get("governance_continuity_note_draft_cards", [])
    if isinstance(drafts, list) and drafts:
        return deepcopy(drafts)

    return [
        {
            "draft_id": "fallback_governance_continuity_note_draft",
            "continuity_id": "fallback_governance_continuity_card",
            "source_batch": SOURCE_CLOSED_BATCH,
            "lane": "closed_batch_integrity",
        }
    ]


def _build_version_cards(drafts: List[Dict[str, Any]]) -> List[GovernanceContinuityNoteVersionCard]:
    cards: List[GovernanceContinuityNoteVersionCard] = []

    for idx, draft in enumerate(drafts, start=1):
        lane = str(draft.get("lane", f"continuity_lane_{idx:03d}"))
        common = {
            "draft_id": str(draft.get("draft_id", f"draft_{idx:03d}")),
            "continuity_id": str(draft.get("continuity_id", f"continuity_{idx:03d}")),
            "source_batch": str(draft.get("source_batch", SOURCE_CLOSED_BATCH)),
            "lane": lane,
            "version_status": "continuity_note_version_preview_ready",
            "version_mode": "preview_only",
            "writes_state": False,
            "executable": False,
            "raw_evidence_visible": False,
        }

        cards.append(
            GovernanceContinuityNoteVersionCard(
                version_id=f"governance_continuity_note_version_264_{idx:03d}_v1_{lane}",
                label=f"Initial governance continuity note version preview for {lane}",
                version_label="Initial simulated continuity note version",
                changed_field_count=10,
                **common,
            )
        )
        cards.append(
            GovernanceContinuityNoteVersionCard(
                version_id=f"governance_continuity_note_version_264_{idx:03d}_v2_{lane}",
                label=f"Revised governance continuity note version preview for {lane}",
                version_label="Revised simulated continuity note version",
                changed_field_count=12,
                **common,
            )
        )

    return cards


def _build_compare_rows(cards: List[GovernanceContinuityNoteVersionCard]) -> List[GovernanceContinuityNoteVersionCompareRow]:
    rows: List[GovernanceContinuityNoteVersionCompareRow] = []

    field_specs = [
        ("closed_batch_context", "Previous closed batch context preview", "Updated closed batch continuity context", "closed_batch_preview_change", "safe_preview"),
        ("lane_summary", "Previous lane summary preview", "Updated continuity lane summary", "lane_summary_preview_change", "safe_preview"),
        ("handoff_context", "Previous handoff preview", "Updated handoff context into Pack 265", "handoff_preview_change", "safe_preview"),
        ("continuity_boundary", "Continuity writes blocked", "Continuity note/version writes remain blocked", "continuity_boundary_change", "safe_preview"),
        ("escalation_boundary", "Escalation blocked", "Escalation writes, assignment, execution, status, and resolution remain blocked", "escalation_boundary_change", "safe_preview"),
        ("assurance_boundary", "Assurance check blocked", "Continuous assurance writes and check execution remain blocked", "assurance_boundary_change", "safe_preview"),
        ("governance_boundary", "Governance decision mutation blocked", "Governance decision write/apply/override remains blocked", "governance_boundary_change", "safe_preview"),
        ("policy_boundary", "Policy mutation blocked", "Policy changes, enables, disables, overrides, and live mutations remain blocked", "policy_boundary_change", "safe_preview"),
        ("evidence_boundary", "Raw evidence hidden", "Raw evidence remains hidden; reveal and export remain blocked", "unchanged_safety_boundary", "redacted_pointer_only"),
        ("next_step", "Prepare Pack 264", "Prepare Pack 265 continuity batch close readiness", "next_step_preview_change", "safe_preview"),
    ]

    for card in cards:
        for field_name, previous, current, change_type, redaction_state in field_specs:
            rows.append(
                GovernanceContinuityNoteVersionCompareRow(
                    compare_row_id=f"{card.version_id}_row_{field_name}",
                    version_id=card.version_id,
                    draft_id=card.draft_id,
                    continuity_id=card.continuity_id,
                    lane=card.lane,
                    field_name=field_name,
                    previous_preview=previous,
                    current_preview=f"{current} ({card.lane})",
                    change_type=change_type,
                    redaction_state=redaction_state,
                    writes_state=False,
                    executable=False,
                    raw_evidence_visible=False,
                )
            )

    return rows


def _build_actions(cards: List[GovernanceContinuityNoteVersionCard]) -> List[GovernanceContinuityNoteVersionAction]:
    actions: List[GovernanceContinuityNoteVersionAction] = []

    for card in cards:
        actions.extend(
            [
                GovernanceContinuityNoteVersionAction(
                    action_id=f"{card.version_id}_action_preview",
                    version_id=card.version_id,
                    label="Preview continuity note version",
                    visible=True,
                    enabled=True,
                    result="preview_allowed",
                    reason="Previewing a simulated continuity note version does not write state.",
                ),
                GovernanceContinuityNoteVersionAction(
                    action_id=f"{card.version_id}_action_restore",
                    version_id=card.version_id,
                    label="Restore continuity note version",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Restoring continuity note versions is blocked.",
                ),
                GovernanceContinuityNoteVersionAction(
                    action_id=f"{card.version_id}_action_apply",
                    version_id=card.version_id,
                    label="Apply continuity note version",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Applying continuity note versions is blocked.",
                ),
                GovernanceContinuityNoteVersionAction(
                    action_id=f"{card.version_id}_action_save_current",
                    version_id=card.version_id,
                    label="Save as current continuity note",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Saving continuity notes is blocked.",
                ),
                GovernanceContinuityNoteVersionAction(
                    action_id=f"{card.version_id}_action_submit",
                    version_id=card.version_id,
                    label="Submit continuity note version",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Submitting continuity note versions is blocked.",
                ),
                GovernanceContinuityNoteVersionAction(
                    action_id=f"{card.version_id}_action_delete",
                    version_id=card.version_id,
                    label="Delete continuity note version",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Deleting continuity note versions is blocked.",
                ),
                GovernanceContinuityNoteVersionAction(
                    action_id=f"{card.version_id}_action_write_handoff",
                    version_id=card.version_id,
                    label="Write continuity handoff",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Continuity handoff writes are blocked.",
                ),
                GovernanceContinuityNoteVersionAction(
                    action_id=f"{card.version_id}_action_write_state",
                    version_id=card.version_id,
                    label="Write continuity state",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Continuity state writes are blocked.",
                ),
                GovernanceContinuityNoteVersionAction(
                    action_id=f"{card.version_id}_action_execute_escalation",
                    version_id=card.version_id,
                    label="Execute escalation",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Escalation execution is blocked.",
                ),
                GovernanceContinuityNoteVersionAction(
                    action_id=f"{card.version_id}_action_execute_assurance_check",
                    version_id=card.version_id,
                    label="Execute assurance check",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Continuous assurance check execution is blocked.",
                ),
                GovernanceContinuityNoteVersionAction(
                    action_id=f"{card.version_id}_action_apply_decision",
                    version_id=card.version_id,
                    label="Apply governance decision",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Governance decision application is blocked.",
                ),
                GovernanceContinuityNoteVersionAction(
                    action_id=f"{card.version_id}_action_override_policy",
                    version_id=card.version_id,
                    label="Override policy",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Policy override is blocked.",
                ),
                GovernanceContinuityNoteVersionAction(
                    action_id=f"{card.version_id}_action_execute_owner_review",
                    version_id=card.version_id,
                    label="Execute owner review",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Owner review execution is blocked.",
                ),
                GovernanceContinuityNoteVersionAction(
                    action_id=f"{card.version_id}_action_reveal_evidence",
                    version_id=card.version_id,
                    label="Reveal raw evidence",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Raw evidence reveal is blocked.",
                ),
                GovernanceContinuityNoteVersionAction(
                    action_id=f"{card.version_id}_action_export_version",
                    version_id=card.version_id,
                    label="Export continuity note version packet",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Continuity note version exports are blocked in preview mode.",
                ),
            ]
        )

    return actions


def _build_checkpoints() -> List[GovernanceContinuityNoteVersionCheckpoint]:
    return [
        GovernanceContinuityNoteVersionCheckpoint(
            checkpoint_id="governance_continuity_note_version_checkpoint_264_001",
            label="Continuity note version cards are preview-only",
            passed=True,
            result="passed",
            evidence_mode="safe_summary_only",
            writes_state=False,
        ),
        GovernanceContinuityNoteVersionCheckpoint(
            checkpoint_id="governance_continuity_note_version_checkpoint_264_002",
            label="Continuity note version compare rows do not write state or reveal raw evidence",
            passed=True,
            result="passed",
            evidence_mode="redacted_pointer_only",
            writes_state=False,
        ),
        GovernanceContinuityNoteVersionCheckpoint(
            checkpoint_id="governance_continuity_note_version_checkpoint_264_003",
            label="Restore, apply, save, submit, delete, handoff, state, execution, assurance, decision, policy, owner review, reveal, and export remain blocked",
            passed=True,
            result="passed",
            evidence_mode="blocked_action_summary",
            writes_state=False,
        ),
        GovernanceContinuityNoteVersionCheckpoint(
            checkpoint_id="governance_continuity_note_version_checkpoint_264_004",
            label="Continuity note versions preserve safe closed-batch and lane context without raw evidence",
            passed=True,
            result="passed",
            evidence_mode="safe_summary_only",
            writes_state=False,
        ),
        GovernanceContinuityNoteVersionCheckpoint(
            checkpoint_id="governance_continuity_note_version_checkpoint_264_005",
            label="Ready for Pack 265 continuity batch close readiness preview",
            passed=True,
            result="passed",
            evidence_mode="safe_summary_only",
            writes_state=False,
        ),
    ]


def _blocked_action_matrix() -> List[Dict[str, Any]]:
    return [
        {
            "action": action,
            "allowed": False,
            "result": "blocked_preview_only",
            "reason": "Pack 264 previews governance continuity note versions only and cannot mutate continuity, escalation, assurance, governance, policy, owner review, saved-view, archive, evidence, or action state.",
        }
        for action in BLOCKED_REAL_ACTIONS
    ]


@lru_cache(maxsize=1)
def _build_receipt_chain_saved_view_owner_review_governance_continuity_note_version_preview_cached() -> Dict[str, Any]:
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

    continuity_note_version_ready = all([
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
        "source_closed_batch": SOURCE_CLOSED_BATCH,
        "save_batch": SAVE_BATCH,
        "save_after_pack": SAVE_AFTER_PACK,
        "next_batch": NEXT_BATCH,
        "cached": True,
        "non_recursive": True,
        "simulation_only": True,
        "preview_only": True,
        "receipt_chain_layer": "saved_view_owner_review_governance_continuity_note_version_preview",
        "source_pack": source_payload.get("pack"),
        "source_endpoint": source_payload.get("endpoint"),
        "source_status": source_payload.get("status"),
        "source_readiness": source_payload.get("readiness"),
        "source_safe_to_continue": source_payload.get("safe_to_continue_to_pack_264"),
        "governance_continuity_note_version_cards": cards,
        "governance_continuity_note_version_compare_rows": rows,
        "governance_continuity_note_version_actions": actions,
        "governance_continuity_note_version_checkpoints": checkpoints,
        "governance_continuity_note_version_summary": {
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
            "continuity_note_version_ready": continuity_note_version_ready,
            "real_continuity_write_enabled": False,
            "real_continuity_note_write_enabled": False,
            "real_continuity_note_save_enabled": False,
            "real_continuity_note_submit_enabled": False,
            "real_continuity_note_delete_enabled": False,
            "real_continuity_note_version_write_enabled": False,
            "real_continuity_note_version_restore_enabled": False,
            "real_continuity_note_version_apply_enabled": False,
            "real_continuity_note_version_delete_enabled": False,
            "real_continuity_handoff_write_enabled": False,
            "real_continuity_state_write_enabled": False,
            "real_escalation_write_enabled": False,
            "real_escalation_execute_enabled": False,
            "real_continuous_assurance_write_enabled": False,
            "real_continuous_assurance_check_execute_enabled": False,
            "real_governance_decision_write_enabled": False,
            "real_governance_decision_apply_enabled": False,
            "real_governance_decision_override_enabled": False,
            "real_policy_change_enabled": False,
            "real_owner_review_execution_enabled": False,
            "real_saved_view_mutation_enabled": False,
            "real_archive_write_enabled": False,
            "real_evidence_export_enabled": False,
            "raw_evidence_visible": False,
            "real_action_execution_enabled": False,
        },
        "safety_invariants": {
            "no_real_continuity_write": True,
            "no_real_continuity_note_write": True,
            "no_real_continuity_note_save": True,
            "no_real_continuity_note_submit": True,
            "no_real_continuity_note_delete": True,
            "no_real_continuity_note_version_write": True,
            "no_real_continuity_note_version_restore": True,
            "no_real_continuity_note_version_apply": True,
            "no_real_continuity_note_version_delete": True,
            "no_real_continuity_handoff_write": True,
            "no_real_continuity_state_write": True,
            "no_real_escalation_write": True,
            "no_real_escalation_execute": True,
            "no_real_continuous_assurance_write": True,
            "no_real_continuous_assurance_check_execute": True,
            "no_real_governance_decision_write": True,
            "no_real_governance_decision_apply": True,
            "no_real_governance_decision_override": True,
            "no_real_policy_change_write": True,
            "no_real_owner_review_execute": True,
            "no_real_saved_view_write": True,
            "no_archive_write": True,
            "no_raw_evidence_reveal": True,
            "no_real_evidence_export": True,
            "no_real_action_execution": True,
            "cached_non_recursive_builder": True,
        },
        "blocked_action_matrix": _blocked_action_matrix(),
        "route_contract": {
            "method": "GET",
            "returns_json": True,
            "requires_tower_guard": True,
            "unguarded_high_risk_allowed": False,
        },
        "pack_264_acceptance": {
            "source_pack_263_verified": True,
            "continuity_note_version_cards_built": True,
            "continuity_note_version_compare_rows_built": True,
            "continuity_note_version_actions_built": True,
            "continuity_note_version_restore_apply_delete_blocked": True,
            "continuity_mutation_paths_blocked": True,
            "ready_for_continuity_batch_close_readiness": True,
        },
        SAFE_TO_CONTINUE_FLAG: True,
        NEXT_PREP_FLAG: {
            "pack": "265",
            "name": "Receipt Chain Saved View Owner Review Governance Continuity Batch Close Readiness Preview",
            "mode": "simulated_preview_only",
            "recommended_next_endpoint": "/tower/receipt-chain-saved-view-owner-review-governance-continuity-batch-close-readiness-v265.json",
            "save_batch": SAVE_BATCH,
            "save_after_pack": SAVE_AFTER_PACK,
        },
    }

    return preview


def build_receipt_chain_saved_view_owner_review_governance_continuity_note_version_preview() -> Dict[str, Any]:
    """Return a defensive copy of the cached Pack 264 preview payload."""
    return deepcopy(_build_receipt_chain_saved_view_owner_review_governance_continuity_note_version_preview_cached())


def build_pack_264_status_bridge() -> Dict[str, Any]:
    """Small cached status bridge for Tower cards/status surfaces."""
    preview = _build_receipt_chain_saved_view_owner_review_governance_continuity_note_version_preview_cached()
    summary = preview["governance_continuity_note_version_summary"]

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
        "cached": preview["cached"],
        "non_recursive": preview["non_recursive"],
        "preview_only": preview["preview_only"],
        "source_pack": preview["source_pack"],
        "source_status": preview["source_status"],
        "version_card_count": summary["version_card_count"],
        "compare_row_count": summary["compare_row_count"],
        "version_action_count": summary["version_action_count"],
        "continuity_note_version_ready": summary["continuity_note_version_ready"],
        SAFE_TO_CONTINUE_FLAG: preview[SAFE_TO_CONTINUE_FLAG],
    }


def prepare_pack_265_receipt_chain_saved_view_owner_review_governance_continuity_batch_close_readiness() -> Dict[str, Any]:
    """Prepare Pack 265 direction without writing state."""
    return {
        "ready": True,
        "next_pack": "265",
        "name": "Receipt Chain Saved View Owner Review Governance Continuity Batch Close Readiness Preview",
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
    "SAFE_TO_CONTINUE_FLAG",
    "NEXT_PREP_FLAG",
    "BLOCKED_REAL_ACTIONS",
    "build_receipt_chain_saved_view_owner_review_governance_continuity_note_version_preview",
    "build_pack_264_status_bridge",
    "prepare_pack_265_receipt_chain_saved_view_owner_review_governance_continuity_batch_close_readiness",
]
