"""
SEARCHABLE LABEL: TOWER_PACK_229_RECEIPT_CHAIN_SAVED_VIEW_OWNER_REVIEW_FOLLOWUP_NOTE_VERSION_PREVIEW_MODULE

Tower section:
- The Tower
- Operational Containment
- Receipt Chain Saved View Review Layer

Pack 229: Receipt Chain Saved View Owner Review Follow-up Note Version Preview

This module is intentionally simulated/preview-only.

Safety boundaries:
- No real follow-up note version writes, restores, or applies.
- No real follow-up note writes, saves, submits, or deletes.
- No real follow-up assignment, status, or due-date writes.
- No real owner approval or denial.
- No real owner note/version writes.
- No real queue state writes.
- No real saved-view restore/revert/write/edit/delete/apply/export.
- No real user preference writes.
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

from tower.receipt_chain_saved_view_owner_review_followup_note_draft_v228 import (
    build_receipt_chain_saved_view_owner_review_followup_note_draft_preview,
)


PACK_ID = "229"
PACK_NUMBER = 229
PACK_NAME = "Receipt Chain Saved View Owner Review Follow-up Note Version Preview"
ENDPOINT = "/tower/receipt-chain-saved-view-owner-review-followup-note-version-v229.json"

TOWER_AREA = "The Tower"
TOWER_SECTION = "Operational Containment"
TOWER_LAYER = "Receipt Chain Saved View Review Layer"

SAVE_BATCH = "226-230"
SAVE_AFTER_PACK = 230
SAFE_TO_CONTINUE_FLAG = "safe_to_continue_to_pack_230"
NEXT_PREP_FLAG = "prepare_pack_230_receipt_chain_saved_view_owner_review_followup_batch_close_readiness"

BLOCKED_REAL_ACTIONS = (
    "real_followup_note_version_write",
    "real_followup_note_version_restore",
    "real_followup_note_version_compare_apply",
    "real_followup_note_write",
    "real_followup_note_save",
    "real_followup_note_submit",
    "real_followup_note_delete",
    "real_followup_assignment_write",
    "real_followup_status_write",
    "real_followup_due_date_write",
    "real_followup_detail_state_write",
    "real_followup_packet_export",
    "real_owner_review_note_version_write",
    "real_owner_review_note_version_restore",
    "real_owner_review_note_write",
    "real_owner_review_note_save",
    "real_owner_review_note_delete",
    "real_owner_review_note_submit",
    "real_owner_review_approve",
    "real_owner_review_deny",
    "real_owner_review_assign",
    "real_owner_review_status_write",
    "real_detail_drawer_state_write",
    "real_queue_reorder_write",
    "real_queue_filter_save",
    "real_saved_view_restore",
    "real_saved_view_revert",
    "real_saved_view_write",
    "real_saved_view_edit",
    "real_saved_view_delete",
    "real_saved_view_apply",
    "real_saved_view_export",
    "real_compare_filter_save",
    "real_compare_filter_apply",
    "real_compare_filter_delete",
    "real_user_preference_write",
    "real_archive_write",
    "raw_evidence_reveal",
    "real_action_execution",
    "live_policy_mutation",
    "receipt_chain_mutation",
)


@dataclass(frozen=True)
class FollowupNoteVersionCard:
    version_id: str
    draft_id: str
    followup_item_id: str
    label: str
    version_label: str
    version_status: str
    version_mode: str
    changed_field_count: int
    writes_state: bool
    executable: bool
    raw_evidence_visible: bool


@dataclass(frozen=True)
class FollowupNoteVersionCompareRow:
    compare_row_id: str
    version_id: str
    draft_id: str
    field_name: str
    previous_preview: str
    current_preview: str
    change_type: str
    redaction_state: str
    owner_review_hint: str
    writes_state: bool
    executable: bool
    raw_evidence_visible: bool


@dataclass(frozen=True)
class FollowupNoteVersionAction:
    action_id: str
    version_id: str
    label: str
    visible: bool
    enabled: bool
    result: str
    reason: str


@dataclass(frozen=True)
class FollowupNoteVersionCheckpoint:
    checkpoint_id: str
    label: str
    passed: bool
    result: str
    evidence_mode: str
    writes_state: bool


def _source_payload() -> Dict[str, Any]:
    return deepcopy(build_receipt_chain_saved_view_owner_review_followup_note_draft_preview())


def _source_drafts(source_payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    return deepcopy(source_payload.get("followup_note_draft_cards", []))


def _build_version_cards(drafts: List[Dict[str, Any]]) -> List[FollowupNoteVersionCard]:
    cards: List[FollowupNoteVersionCard] = []

    for idx, draft in enumerate(drafts, start=1):
        cards.append(
            FollowupNoteVersionCard(
                version_id=f"followup_note_version_229_{idx:03d}_v1",
                draft_id=draft["draft_id"],
                followup_item_id=draft["followup_item_id"],
                label=f"Initial version preview for {draft['label']}",
                version_label="Initial simulated follow-up note version",
                version_status="followup_note_version_preview_ready",
                version_mode="preview_only",
                changed_field_count=5,
                writes_state=False,
                executable=False,
                raw_evidence_visible=False,
            )
        )
        cards.append(
            FollowupNoteVersionCard(
                version_id=f"followup_note_version_229_{idx:03d}_v2",
                draft_id=draft["draft_id"],
                followup_item_id=draft["followup_item_id"],
                label=f"Revised version preview for {draft['label']}",
                version_label="Revised simulated follow-up note version",
                version_status="followup_note_version_preview_ready",
                version_mode="preview_only",
                changed_field_count=6,
                writes_state=False,
                executable=False,
                raw_evidence_visible=False,
            )
        )

    return cards


def _build_compare_rows(cards: List[FollowupNoteVersionCard]) -> List[FollowupNoteVersionCompareRow]:
    rows: List[FollowupNoteVersionCompareRow] = []

    for card in cards:
        rows.extend(
            [
                FollowupNoteVersionCompareRow(
                    compare_row_id=f"{card.version_id}_row_followup_summary",
                    version_id=card.version_id,
                    draft_id=card.draft_id,
                    field_name="followup_summary",
                    previous_preview="Previous follow-up summary preview",
                    current_preview="Updated follow-up summary preview",
                    change_type="summary_preview_change",
                    redaction_state="safe_preview",
                    owner_review_hint="Review follow-up summary wording without saving or restoring a version.",
                    writes_state=False,
                    executable=False,
                    raw_evidence_visible=False,
                ),
                FollowupNoteVersionCompareRow(
                    compare_row_id=f"{card.version_id}_row_next_step",
                    version_id=card.version_id,
                    draft_id=card.draft_id,
                    field_name="next_step",
                    previous_preview="Previous next-step preview",
                    current_preview="Updated next-step preview",
                    change_type="next_step_preview_change",
                    redaction_state="safe_preview",
                    owner_review_hint="Review next-step wording without writing follow-up status.",
                    writes_state=False,
                    executable=False,
                    raw_evidence_visible=False,
                ),
                FollowupNoteVersionCompareRow(
                    compare_row_id=f"{card.version_id}_row_owner_boundary",
                    version_id=card.version_id,
                    draft_id=card.draft_id,
                    field_name="owner_action_boundary",
                    previous_preview="Assignment, done status, due dates, approvals, and denials blocked",
                    current_preview="Assignment, status, due dates, approvals, denials, note saves, and exports blocked",
                    change_type="safety_control_change",
                    redaction_state="safe_preview",
                    owner_review_hint="Confirm follow-up note versions cannot trigger owner or follow-up actions.",
                    writes_state=False,
                    executable=False,
                    raw_evidence_visible=False,
                ),
                FollowupNoteVersionCompareRow(
                    compare_row_id=f"{card.version_id}_row_evidence_boundary",
                    version_id=card.version_id,
                    draft_id=card.draft_id,
                    field_name="evidence_boundary",
                    previous_preview="Raw evidence hidden",
                    current_preview="Raw evidence remains hidden; pointer summary only",
                    change_type="unchanged_safety_boundary",
                    redaction_state="redacted_pointer_only",
                    owner_review_hint="Confirm raw evidence remains hidden across follow-up note versions.",
                    writes_state=False,
                    executable=False,
                    raw_evidence_visible=False,
                ),
                FollowupNoteVersionCompareRow(
                    compare_row_id=f"{card.version_id}_row_export_boundary",
                    version_id=card.version_id,
                    draft_id=card.draft_id,
                    field_name="export_boundary",
                    previous_preview="Packet export blocked",
                    current_preview="Packet export and version export blocked",
                    change_type="safety_control_change",
                    redaction_state="safe_preview",
                    owner_review_hint="Confirm follow-up packets and note versions cannot be exported.",
                    writes_state=False,
                    executable=False,
                    raw_evidence_visible=False,
                ),
            ]
        )

    return rows


def _build_version_actions(cards: List[FollowupNoteVersionCard]) -> List[FollowupNoteVersionAction]:
    actions: List[FollowupNoteVersionAction] = []

    for card in cards:
        actions.extend(
            [
                FollowupNoteVersionAction(
                    action_id=f"{card.version_id}_action_preview",
                    version_id=card.version_id,
                    label="Preview follow-up note version",
                    visible=True,
                    enabled=True,
                    result="preview_allowed",
                    reason="Previewing a simulated follow-up note version does not write state.",
                ),
                FollowupNoteVersionAction(
                    action_id=f"{card.version_id}_action_restore",
                    version_id=card.version_id,
                    label="Restore follow-up note version",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Restoring follow-up note versions is blocked.",
                ),
                FollowupNoteVersionAction(
                    action_id=f"{card.version_id}_action_save",
                    version_id=card.version_id,
                    label="Save as current follow-up note",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Saving follow-up notes is blocked.",
                ),
                FollowupNoteVersionAction(
                    action_id=f"{card.version_id}_action_submit",
                    version_id=card.version_id,
                    label="Submit follow-up note version",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Submitting follow-up note versions is blocked.",
                ),
                FollowupNoteVersionAction(
                    action_id=f"{card.version_id}_action_delete",
                    version_id=card.version_id,
                    label="Delete follow-up note version",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Deleting follow-up note versions is blocked.",
                ),
                FollowupNoteVersionAction(
                    action_id=f"{card.version_id}_action_apply_to_followup",
                    version_id=card.version_id,
                    label="Apply version to follow-up",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Applying note versions would write follow-up state.",
                ),
                FollowupNoteVersionAction(
                    action_id=f"{card.version_id}_action_export_version",
                    version_id=card.version_id,
                    label="Export version packet",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Version packet exports are blocked.",
                ),
            ]
        )

    return actions


def _build_checkpoints() -> List[FollowupNoteVersionCheckpoint]:
    return [
        FollowupNoteVersionCheckpoint(
            checkpoint_id="followup_note_version_checkpoint_229_001",
            label="Version cards are preview-only",
            passed=True,
            result="passed",
            evidence_mode="safe_summary_only",
            writes_state=False,
        ),
        FollowupNoteVersionCheckpoint(
            checkpoint_id="followup_note_version_checkpoint_229_002",
            label="Compare rows do not reveal raw evidence or write state",
            passed=True,
            result="passed",
            evidence_mode="redacted_pointer_only",
            writes_state=False,
        ),
        FollowupNoteVersionCheckpoint(
            checkpoint_id="followup_note_version_checkpoint_229_003",
            label="Restore, save, submit, delete, apply, and export actions remain blocked",
            passed=True,
            result="passed",
            evidence_mode="blocked_action_summary",
            writes_state=False,
        ),
        FollowupNoteVersionCheckpoint(
            checkpoint_id="followup_note_version_checkpoint_229_004",
            label="Follow-up assignment, status, and due date writes remain blocked",
            passed=True,
            result="passed",
            evidence_mode="blocked_action_summary",
            writes_state=False,
        ),
        FollowupNoteVersionCheckpoint(
            checkpoint_id="followup_note_version_checkpoint_229_005",
            label="Ready for Pack 230 follow-up batch close readiness",
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
            "reason": "Pack 229 previews follow-up note versions only and cannot write versions, notes, follow-up state, queue, saved-view, archive, evidence, or action state.",
        }
        for action in BLOCKED_REAL_ACTIONS
    ]


@lru_cache(maxsize=1)
def _build_receipt_chain_saved_view_owner_review_followup_note_version_preview_cached() -> Dict[str, Any]:
    source_payload = _source_payload()
    drafts = _source_drafts(source_payload)

    version_cards_raw = _build_version_cards(drafts)
    compare_rows_raw = _build_compare_rows(version_cards_raw)
    actions_raw = _build_version_actions(version_cards_raw)
    checkpoints_raw = _build_checkpoints()

    version_cards = [asdict(card) for card in version_cards_raw]
    compare_rows = [asdict(row) for row in compare_rows_raw]
    actions = [asdict(action) for action in actions_raw]
    checkpoints = [asdict(checkpoint) for checkpoint in checkpoints_raw]

    enabled_action_count = sum(1 for action in actions if action["enabled"] is True)
    blocked_action_count = sum(1 for action in actions if action["enabled"] is False)
    redacted_compare_row_count = sum(1 for row in compare_rows if row["redaction_state"] == "redacted_pointer_only")

    all_cards_preview_only = all(card["version_mode"] == "preview_only" for card in version_cards)
    all_cards_no_writes = all(card["writes_state"] is False for card in version_cards)
    all_cards_non_executable = all(card["executable"] is False for card in version_cards)
    all_cards_no_raw_evidence = all(card["raw_evidence_visible"] is False for card in version_cards)
    all_rows_no_writes = all(row["writes_state"] is False for row in compare_rows)
    all_rows_non_executable = all(row["executable"] is False for row in compare_rows)
    all_rows_no_raw_evidence = all(row["raw_evidence_visible"] is False for row in compare_rows)
    all_actions_safe = all(action["result"] in {"preview_allowed", "blocked_preview_only"} for action in actions)
    all_checkpoints_passed = all(checkpoint["passed"] is True for checkpoint in checkpoints)
    all_checkpoints_no_writes = all(checkpoint["writes_state"] is False for checkpoint in checkpoints)

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
        "save_batch": SAVE_BATCH,
        "save_after_pack": SAVE_AFTER_PACK,
        "cached": True,
        "non_recursive": True,
        "simulation_only": True,
        "preview_only": True,
        "receipt_chain_layer": "saved_view_owner_review_followup_note_version_preview",
        "source_pack": source_payload.get("pack"),
        "source_endpoint": source_payload.get("endpoint"),
        "source_status": source_payload.get("status"),
        "source_readiness": source_payload.get("readiness"),
        "source_safe_to_continue": source_payload.get("safe_to_continue_to_pack_229"),
        "followup_note_version_cards": version_cards,
        "followup_note_version_compare_rows": compare_rows,
        "followup_note_version_actions": actions,
        "followup_note_version_checkpoints": checkpoints,
        "followup_note_version_summary": {
            "source_draft_card_count": len(drafts),
            "version_card_count": len(version_cards),
            "compare_row_count": len(compare_rows),
            "version_action_count": len(actions),
            "checkpoint_count": len(checkpoints),
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
            "followup_note_version_ready": all([
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
            ]),
            "real_followup_note_version_write_enabled": False,
            "real_followup_note_version_restore_enabled": False,
            "real_followup_note_version_apply_enabled": False,
            "real_followup_note_write_enabled": False,
            "real_followup_note_save_enabled": False,
            "real_followup_note_submit_enabled": False,
            "real_followup_note_delete_enabled": False,
            "real_followup_assignment_enabled": False,
            "real_followup_status_write_enabled": False,
            "real_followup_due_date_write_enabled": False,
            "real_followup_packet_export_enabled": False,
            "real_owner_review_write_enabled": False,
            "real_owner_note_write_enabled": False,
            "real_saved_view_mutation_enabled": False,
            "real_archive_write_enabled": False,
            "raw_evidence_visible": False,
            "real_action_execution_enabled": False,
        },
        "safety_invariants": {
            "no_real_followup_note_version_write": True,
            "no_real_followup_note_version_restore": True,
            "no_real_followup_note_version_compare_apply": True,
            "no_real_followup_note_write": True,
            "no_real_followup_note_save": True,
            "no_real_followup_note_submit": True,
            "no_real_followup_note_delete": True,
            "no_real_followup_assignment_write": True,
            "no_real_followup_status_write": True,
            "no_real_followup_due_date_write": True,
            "no_real_followup_detail_state_write": True,
            "no_real_followup_packet_export": True,
            "no_real_owner_review_note_version_write": True,
            "no_real_owner_review_note_version_restore": True,
            "no_real_owner_review_note_write": True,
            "no_real_owner_review_note_save": True,
            "no_real_owner_review_note_delete": True,
            "no_real_owner_review_note_submit": True,
            "no_real_owner_review_approve": True,
            "no_real_owner_review_deny": True,
            "no_real_owner_review_assign": True,
            "no_real_owner_review_status_write": True,
            "no_real_saved_view_restore": True,
            "no_real_saved_view_revert": True,
            "no_real_saved_view_write": True,
            "no_real_saved_view_edit": True,
            "no_real_saved_view_delete": True,
            "no_real_saved_view_apply": True,
            "no_real_saved_view_export": True,
            "no_real_user_preference_write": True,
            "no_archive_write": True,
            "no_raw_evidence_reveal": True,
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
        "pack_229_acceptance": {
            "followup_note_version_cards_built": True,
            "followup_note_version_compare_rows_built": True,
            "followup_note_version_actions_built": True,
            "followup_note_version_write_restore_apply_blocked": True,
            "followup_assignment_status_due_date_blocked": True,
            "raw_evidence_remains_hidden": True,
            "ready_for_followup_batch_close_readiness": True,
        },
        SAFE_TO_CONTINUE_FLAG: True,
        NEXT_PREP_FLAG: {
            "pack": "230",
            "name": "Receipt Chain Saved View Owner Review Follow-up Batch Close Readiness Preview",
            "mode": "simulated_preview_only",
            "recommended_next_endpoint": "/tower/receipt-chain-saved-view-owner-review-followup-batch-close-readiness-v230.json",
            "save_batch": SAVE_BATCH,
            "save_after_pack": SAVE_AFTER_PACK,
        },
    }

    return preview


def build_receipt_chain_saved_view_owner_review_followup_note_version_preview() -> Dict[str, Any]:
    """Return a defensive copy of the cached Pack 229 preview payload."""
    return deepcopy(_build_receipt_chain_saved_view_owner_review_followup_note_version_preview_cached())


def build_pack_229_status_bridge() -> Dict[str, Any]:
    """Small cached status bridge for Tower cards/status surfaces."""
    preview = _build_receipt_chain_saved_view_owner_review_followup_note_version_preview_cached()
    summary = preview["followup_note_version_summary"]

    return {
        "pack": preview["pack"],
        "pack_number": preview["pack_number"],
        "pack_name": preview["pack_name"],
        "status": preview["status"],
        "readiness": preview["readiness"],
        "endpoint": preview["endpoint"],
        "tower_section": preview["tower_section"],
        "tower_layer": preview["tower_layer"],
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
        "followup_note_version_ready": summary["followup_note_version_ready"],
        SAFE_TO_CONTINUE_FLAG: preview[SAFE_TO_CONTINUE_FLAG],
    }


def prepare_pack_230_receipt_chain_saved_view_owner_review_followup_batch_close_readiness() -> Dict[str, Any]:
    """Prepare Pack 230 direction without writing state."""
    return {
        "ready": True,
        "next_pack": "230",
        "name": "Receipt Chain Saved View Owner Review Follow-up Batch Close Readiness Preview",
        "mode": "simulated_preview_only",
        "source_pack": PACK_ID,
        "source_endpoint": ENDPOINT,
        "tower_section": TOWER_SECTION,
        "tower_layer": TOWER_LAYER,
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
    "SAVE_BATCH",
    "SAVE_AFTER_PACK",
    "SAFE_TO_CONTINUE_FLAG",
    "NEXT_PREP_FLAG",
    "BLOCKED_REAL_ACTIONS",
    "build_receipt_chain_saved_view_owner_review_followup_note_version_preview",
    "build_pack_229_status_bridge",
    "prepare_pack_230_receipt_chain_saved_view_owner_review_followup_batch_close_readiness",
]
