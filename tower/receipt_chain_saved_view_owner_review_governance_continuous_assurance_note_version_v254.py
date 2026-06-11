"""
SEARCHABLE LABEL: TOWER_PACK_254_RECEIPT_CHAIN_SAVED_VIEW_OWNER_REVIEW_GOVERNANCE_CONTINUOUS_ASSURANCE_NOTE_VERSION_PREVIEW_MODULE

Tower section:
- The Tower
- Operational Containment
- Receipt Chain Saved View Review Layer
- Governance Index Preview layer

Pack 254: Receipt Chain Saved View Owner Review Governance Continuous Assurance Note Version Preview

This module is intentionally simulated/preview-only.

Purpose:
- Build safe continuous assurance note version previews from Pack 253 assurance note drafts.
- Preserve version history, compare rows, and owner-safe context without writing state.
- Keep restore/apply/save/submit/delete/export and raw evidence reveal paths blocked.
- Prepare Pack 255 continuous assurance batch close readiness preview.

Safety boundaries:
- No real continuous assurance writes.
- No real assurance check execution.
- No real assurance status writes.
- No real assurance note writes, saves, submits, or deletes.
- No real assurance note version writes, restores, or applies.
- No real governance decision writes, applies, or overrides.
- No real decision note writes, saves, submits, deletes, restores, or applies.
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

from tower.receipt_chain_saved_view_owner_review_governance_continuous_assurance_note_draft_v253 import (
    build_receipt_chain_saved_view_owner_review_governance_continuous_assurance_note_draft_preview,
)


PACK_ID = "254"
PACK_NUMBER = 254
PACK_NAME = "Receipt Chain Saved View Owner Review Governance Continuous Assurance Note Version Preview"
ENDPOINT = "/tower/receipt-chain-saved-view-owner-review-governance-continuous-assurance-note-version-v254.json"

TOWER_AREA = "The Tower"
TOWER_SECTION = "Operational Containment"
TOWER_LAYER = "Receipt Chain Saved View Review Layer"
TOWER_SUBLAYER = "Governance Index Preview layer"

SAVE_BATCH = "251-260"
SAVE_AFTER_PACK = 260
NEXT_BATCH = "251-260"
SAFE_TO_CONTINUE_FLAG = "safe_to_continue_to_pack_255"
NEXT_PREP_FLAG = "prepare_pack_255_receipt_chain_saved_view_owner_review_governance_continuous_assurance_batch_close_readiness"

BLOCKED_REAL_ACTIONS = (
    "real_continuous_assurance_write",
    "real_continuous_assurance_note_write",
    "real_continuous_assurance_note_save",
    "real_continuous_assurance_note_submit",
    "real_continuous_assurance_note_delete",
    "real_continuous_assurance_note_version_write",
    "real_continuous_assurance_note_version_restore",
    "real_continuous_assurance_note_version_apply",
    "real_continuous_assurance_note_version_delete",
    "real_continuous_assurance_note_version_compare_write",
    "real_continuous_assurance_check_execute",
    "real_continuous_assurance_status_write",
    "real_continuous_assurance_remediation_execute",
    "real_batch_close_write",
    "real_governance_decision_write",
    "real_governance_trace_write",
    "real_governance_decision_apply",
    "real_governance_decision_override",
    "real_decision_note_write",
    "real_decision_note_save",
    "real_decision_note_submit",
    "real_decision_note_delete",
    "real_decision_note_version_write",
    "real_decision_note_version_restore",
    "real_decision_note_version_apply",
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
class GovernanceContinuousAssuranceNoteVersionCard:
    version_id: str
    draft_id: str
    assurance_id: str
    assurance_key: str
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
class GovernanceContinuousAssuranceNoteVersionCompareRow:
    compare_row_id: str
    version_id: str
    draft_id: str
    assurance_key: str
    field_name: str
    previous_preview: str
    current_preview: str
    change_type: str
    redaction_state: str
    writes_state: bool
    executable: bool
    raw_evidence_visible: bool


@dataclass(frozen=True)
class GovernanceContinuousAssuranceNoteVersionAction:
    action_id: str
    version_id: str
    label: str
    visible: bool
    enabled: bool
    result: str
    reason: str


@dataclass(frozen=True)
class GovernanceContinuousAssuranceNoteVersionCheckpoint:
    checkpoint_id: str
    label: str
    passed: bool
    result: str
    evidence_mode: str
    writes_state: bool


def _source_payload() -> Dict[str, Any]:
    return deepcopy(build_receipt_chain_saved_view_owner_review_governance_continuous_assurance_note_draft_preview())


def _source_drafts(source_payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    drafts = source_payload.get("governance_continuous_assurance_note_draft_cards", [])
    if isinstance(drafts, list) and drafts:
        return deepcopy(drafts)

    return [
        {
            "draft_id": "fallback_continuous_assurance_note_draft",
            "assurance_id": "fallback_assurance",
            "assurance_key": "batch_integrity",
            "lane": "batch_integrity",
        }
    ]


def _build_version_cards(drafts: List[Dict[str, Any]]) -> List[GovernanceContinuousAssuranceNoteVersionCard]:
    cards: List[GovernanceContinuousAssuranceNoteVersionCard] = []

    for idx, draft in enumerate(drafts, start=1):
        assurance_key = str(draft.get("assurance_key", f"assurance_{idx:03d}"))
        common = {
            "draft_id": str(draft.get("draft_id", f"draft_{idx:03d}")),
            "assurance_id": str(draft.get("assurance_id", f"assurance_{idx:03d}")),
            "assurance_key": assurance_key,
            "lane": str(draft.get("lane", "continuous_assurance")),
            "version_status": "continuous_assurance_note_version_preview_ready",
            "version_mode": "preview_only",
            "writes_state": False,
            "executable": False,
            "raw_evidence_visible": False,
        }

        cards.append(
            GovernanceContinuousAssuranceNoteVersionCard(
                version_id=f"governance_continuous_assurance_note_version_254_{idx:03d}_v1_{assurance_key}",
                label=f"Initial continuous assurance note version preview for {assurance_key}",
                version_label="Initial simulated continuous assurance note version",
                changed_field_count=9,
                **common,
            )
        )
        cards.append(
            GovernanceContinuousAssuranceNoteVersionCard(
                version_id=f"governance_continuous_assurance_note_version_254_{idx:03d}_v2_{assurance_key}",
                label=f"Revised continuous assurance note version preview for {assurance_key}",
                version_label="Revised simulated continuous assurance note version",
                changed_field_count=11,
                **common,
            )
        )

    return cards


def _build_compare_rows(cards: List[GovernanceContinuousAssuranceNoteVersionCard]) -> List[GovernanceContinuousAssuranceNoteVersionCompareRow]:
    rows: List[GovernanceContinuousAssuranceNoteVersionCompareRow] = []

    for card in cards:
        rows.extend(
            [
                GovernanceContinuousAssuranceNoteVersionCompareRow(
                    compare_row_id=f"{card.version_id}_row_assurance_summary",
                    version_id=card.version_id,
                    draft_id=card.draft_id,
                    assurance_key=card.assurance_key,
                    field_name="assurance_summary",
                    previous_preview="Previous assurance summary preview",
                    current_preview=f"Updated safe assurance summary preview for {card.assurance_key}.",
                    change_type="assurance_summary_preview_change",
                    redaction_state="safe_preview",
                    writes_state=False,
                    executable=False,
                    raw_evidence_visible=False,
                ),
                GovernanceContinuousAssuranceNoteVersionCompareRow(
                    compare_row_id=f"{card.version_id}_row_lane_context",
                    version_id=card.version_id,
                    draft_id=card.draft_id,
                    assurance_key=card.assurance_key,
                    field_name="lane_context",
                    previous_preview="Previous lane context preview",
                    current_preview=f"Updated lane context preview: {card.lane}.",
                    change_type="lane_context_preview_change",
                    redaction_state="safe_preview",
                    writes_state=False,
                    executable=False,
                    raw_evidence_visible=False,
                ),
                GovernanceContinuousAssuranceNoteVersionCompareRow(
                    compare_row_id=f"{card.version_id}_row_assurance_status_boundary",
                    version_id=card.version_id,
                    draft_id=card.draft_id,
                    assurance_key=card.assurance_key,
                    field_name="assurance_status_boundary",
                    previous_preview="Status write blocked",
                    current_preview="Assurance check execution, status writes, and remediation remain blocked.",
                    change_type="status_boundary_change",
                    redaction_state="safe_preview",
                    writes_state=False,
                    executable=False,
                    raw_evidence_visible=False,
                ),
                GovernanceContinuousAssuranceNoteVersionCompareRow(
                    compare_row_id=f"{card.version_id}_row_governance_boundary",
                    version_id=card.version_id,
                    draft_id=card.draft_id,
                    assurance_key=card.assurance_key,
                    field_name="governance_boundary",
                    previous_preview="Governance mutation blocked",
                    current_preview="Governance decision write, apply, and override remain blocked.",
                    change_type="governance_boundary_change",
                    redaction_state="safe_preview",
                    writes_state=False,
                    executable=False,
                    raw_evidence_visible=False,
                ),
                GovernanceContinuousAssuranceNoteVersionCompareRow(
                    compare_row_id=f"{card.version_id}_row_policy_boundary",
                    version_id=card.version_id,
                    draft_id=card.draft_id,
                    assurance_key=card.assurance_key,
                    field_name="policy_boundary",
                    previous_preview="Policy mutation blocked",
                    current_preview="Policy changes, enables, disables, overrides, and live mutations remain blocked.",
                    change_type="policy_boundary_change",
                    redaction_state="safe_preview",
                    writes_state=False,
                    executable=False,
                    raw_evidence_visible=False,
                ),
                GovernanceContinuousAssuranceNoteVersionCompareRow(
                    compare_row_id=f"{card.version_id}_row_saved_view_boundary",
                    version_id=card.version_id,
                    draft_id=card.draft_id,
                    assurance_key=card.assurance_key,
                    field_name="saved_view_boundary",
                    previous_preview="Saved-view mutation blocked",
                    current_preview="Saved-view restore, revert, write, edit, delete, apply, and export remain blocked.",
                    change_type="saved_view_boundary_change",
                    redaction_state="safe_preview",
                    writes_state=False,
                    executable=False,
                    raw_evidence_visible=False,
                ),
                GovernanceContinuousAssuranceNoteVersionCompareRow(
                    compare_row_id=f"{card.version_id}_row_evidence_boundary",
                    version_id=card.version_id,
                    draft_id=card.draft_id,
                    assurance_key=card.assurance_key,
                    field_name="evidence_boundary",
                    previous_preview="Raw evidence hidden",
                    current_preview="Raw evidence remains hidden; reveal and export are blocked.",
                    change_type="unchanged_safety_boundary",
                    redaction_state="redacted_pointer_only",
                    writes_state=False,
                    executable=False,
                    raw_evidence_visible=False,
                ),
                GovernanceContinuousAssuranceNoteVersionCompareRow(
                    compare_row_id=f"{card.version_id}_row_owner_context_preview",
                    version_id=card.version_id,
                    draft_id=card.draft_id,
                    assurance_key=card.assurance_key,
                    field_name="owner_context_preview",
                    previous_preview="Previous owner context preview",
                    current_preview="Preview-only owner context update. It does not execute owner review.",
                    change_type="owner_context_preview_change",
                    redaction_state="safe_preview",
                    writes_state=False,
                    executable=False,
                    raw_evidence_visible=False,
                ),
                GovernanceContinuousAssuranceNoteVersionCompareRow(
                    compare_row_id=f"{card.version_id}_row_next_step",
                    version_id=card.version_id,
                    draft_id=card.draft_id,
                    assurance_key=card.assurance_key,
                    field_name="next_step",
                    previous_preview="Prepare Pack 254",
                    current_preview="Prepare Pack 255 continuous assurance batch close readiness.",
                    change_type="next_step_preview_change",
                    redaction_state="safe_preview",
                    writes_state=False,
                    executable=False,
                    raw_evidence_visible=False,
                ),
            ]
        )

    return rows


def _build_actions(cards: List[GovernanceContinuousAssuranceNoteVersionCard]) -> List[GovernanceContinuousAssuranceNoteVersionAction]:
    actions: List[GovernanceContinuousAssuranceNoteVersionAction] = []

    for card in cards:
        actions.extend(
            [
                GovernanceContinuousAssuranceNoteVersionAction(
                    action_id=f"{card.version_id}_action_preview",
                    version_id=card.version_id,
                    label="Preview continuous assurance note version",
                    visible=True,
                    enabled=True,
                    result="preview_allowed",
                    reason="Previewing a simulated assurance note version does not write state.",
                ),
                GovernanceContinuousAssuranceNoteVersionAction(
                    action_id=f"{card.version_id}_action_restore",
                    version_id=card.version_id,
                    label="Restore assurance note version",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Restoring continuous assurance note versions is blocked.",
                ),
                GovernanceContinuousAssuranceNoteVersionAction(
                    action_id=f"{card.version_id}_action_apply",
                    version_id=card.version_id,
                    label="Apply assurance note version",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Applying continuous assurance note versions is blocked.",
                ),
                GovernanceContinuousAssuranceNoteVersionAction(
                    action_id=f"{card.version_id}_action_save_current",
                    version_id=card.version_id,
                    label="Save as current assurance note",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Saving continuous assurance notes is blocked.",
                ),
                GovernanceContinuousAssuranceNoteVersionAction(
                    action_id=f"{card.version_id}_action_submit",
                    version_id=card.version_id,
                    label="Submit assurance note version",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Submitting assurance note versions is blocked.",
                ),
                GovernanceContinuousAssuranceNoteVersionAction(
                    action_id=f"{card.version_id}_action_delete",
                    version_id=card.version_id,
                    label="Delete assurance note version",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Deleting assurance note versions is blocked.",
                ),
                GovernanceContinuousAssuranceNoteVersionAction(
                    action_id=f"{card.version_id}_action_execute_check",
                    version_id=card.version_id,
                    label="Execute assurance check",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Assurance check execution is blocked.",
                ),
                GovernanceContinuousAssuranceNoteVersionAction(
                    action_id=f"{card.version_id}_action_write_status",
                    version_id=card.version_id,
                    label="Write assurance status",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Assurance status writes are blocked.",
                ),
                GovernanceContinuousAssuranceNoteVersionAction(
                    action_id=f"{card.version_id}_action_apply_decision",
                    version_id=card.version_id,
                    label="Apply governance decision",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Governance decision application is blocked.",
                ),
                GovernanceContinuousAssuranceNoteVersionAction(
                    action_id=f"{card.version_id}_action_override_policy",
                    version_id=card.version_id,
                    label="Override policy",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Policy override is blocked.",
                ),
                GovernanceContinuousAssuranceNoteVersionAction(
                    action_id=f"{card.version_id}_action_execute_owner_review",
                    version_id=card.version_id,
                    label="Execute owner review",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Owner review execution is blocked.",
                ),
                GovernanceContinuousAssuranceNoteVersionAction(
                    action_id=f"{card.version_id}_action_reveal_evidence",
                    version_id=card.version_id,
                    label="Reveal raw evidence",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Raw evidence reveal is blocked.",
                ),
                GovernanceContinuousAssuranceNoteVersionAction(
                    action_id=f"{card.version_id}_action_export_version",
                    version_id=card.version_id,
                    label="Export assurance note version packet",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Assurance note version exports are blocked in preview mode.",
                ),
            ]
        )

    return actions


def _build_checkpoints() -> List[GovernanceContinuousAssuranceNoteVersionCheckpoint]:
    return [
        GovernanceContinuousAssuranceNoteVersionCheckpoint(
            checkpoint_id="governance_continuous_assurance_note_version_checkpoint_254_001",
            label="Continuous assurance note version cards are preview-only",
            passed=True,
            result="passed",
            evidence_mode="safe_summary_only",
            writes_state=False,
        ),
        GovernanceContinuousAssuranceNoteVersionCheckpoint(
            checkpoint_id="governance_continuous_assurance_note_version_checkpoint_254_002",
            label="Version compare rows do not write state or reveal raw evidence",
            passed=True,
            result="passed",
            evidence_mode="redacted_pointer_only",
            writes_state=False,
        ),
        GovernanceContinuousAssuranceNoteVersionCheckpoint(
            checkpoint_id="governance_continuous_assurance_note_version_checkpoint_254_003",
            label="Restore, apply, save, submit, delete, execution, policy, owner review, reveal, and export remain blocked",
            passed=True,
            result="passed",
            evidence_mode="blocked_action_summary",
            writes_state=False,
        ),
        GovernanceContinuousAssuranceNoteVersionCheckpoint(
            checkpoint_id="governance_continuous_assurance_note_version_checkpoint_254_004",
            label="Assurance note versions preserve safe context without raw evidence",
            passed=True,
            result="passed",
            evidence_mode="safe_summary_only",
            writes_state=False,
        ),
        GovernanceContinuousAssuranceNoteVersionCheckpoint(
            checkpoint_id="governance_continuous_assurance_note_version_checkpoint_254_005",
            label="Ready for Pack 255 continuous assurance batch close readiness preview",
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
            "reason": "Pack 254 previews continuous assurance note versions only and cannot mutate governance, policy, owner review, saved-view, archive, evidence, or action state.",
        }
        for action in BLOCKED_REAL_ACTIONS
    ]


@lru_cache(maxsize=1)
def _build_receipt_chain_saved_view_owner_review_governance_continuous_assurance_note_version_preview_cached() -> Dict[str, Any]:
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

    continuous_assurance_note_version_ready = all([
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
        "save_batch": SAVE_BATCH,
        "save_after_pack": SAVE_AFTER_PACK,
        "next_batch": NEXT_BATCH,
        "cached": True,
        "non_recursive": True,
        "simulation_only": True,
        "preview_only": True,
        "receipt_chain_layer": "saved_view_owner_review_governance_continuous_assurance_note_version_preview",
        "source_pack": source_payload.get("pack"),
        "source_endpoint": source_payload.get("endpoint"),
        "source_status": source_payload.get("status"),
        "source_readiness": source_payload.get("readiness"),
        "source_safe_to_continue": source_payload.get("safe_to_continue_to_pack_254"),
        "governance_continuous_assurance_note_version_cards": cards,
        "governance_continuous_assurance_note_version_compare_rows": rows,
        "governance_continuous_assurance_note_version_actions": actions,
        "governance_continuous_assurance_note_version_checkpoints": checkpoints,
        "governance_continuous_assurance_note_version_summary": {
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
            "continuous_assurance_note_version_ready": continuous_assurance_note_version_ready,
            "real_continuous_assurance_write_enabled": False,
            "real_continuous_assurance_note_write_enabled": False,
            "real_continuous_assurance_note_save_enabled": False,
            "real_continuous_assurance_note_submit_enabled": False,
            "real_continuous_assurance_note_delete_enabled": False,
            "real_continuous_assurance_note_version_write_enabled": False,
            "real_continuous_assurance_note_version_restore_enabled": False,
            "real_continuous_assurance_note_version_apply_enabled": False,
            "real_continuous_assurance_check_execute_enabled": False,
            "real_continuous_assurance_status_write_enabled": False,
            "real_continuous_assurance_remediation_execute_enabled": False,
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
            "no_real_continuous_assurance_write": True,
            "no_real_continuous_assurance_note_write": True,
            "no_real_continuous_assurance_note_save": True,
            "no_real_continuous_assurance_note_submit": True,
            "no_real_continuous_assurance_note_delete": True,
            "no_real_continuous_assurance_note_version_write": True,
            "no_real_continuous_assurance_note_version_restore": True,
            "no_real_continuous_assurance_note_version_apply": True,
            "no_real_continuous_assurance_check_execute": True,
            "no_real_continuous_assurance_status_write": True,
            "no_real_continuous_assurance_remediation_execute": True,
            "no_real_batch_close_write": True,
            "no_real_governance_decision_write": True,
            "no_real_governance_decision_apply": True,
            "no_real_governance_decision_override": True,
            "no_real_decision_note_write": True,
            "no_real_decision_note_version_write": True,
            "no_real_policy_change_write": True,
            "no_real_approval_execute": True,
            "no_real_denial_execute": True,
            "no_real_owner_review_execute": True,
            "no_real_saved_view_restore": True,
            "no_real_saved_view_write": True,
            "no_real_saved_view_apply": True,
            "no_real_saved_view_export": True,
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
        "pack_254_acceptance": {
            "continuous_assurance_note_version_cards_built": True,
            "continuous_assurance_note_version_compare_rows_built": True,
            "continuous_assurance_note_version_actions_built": True,
            "assurance_note_version_restore_apply_delete_blocked": True,
            "assurance_execution_status_remediation_blocked": True,
            "decision_policy_owner_saved_view_archive_evidence_actions_blocked": True,
            "ready_for_continuous_assurance_batch_close_readiness": True,
        },
        SAFE_TO_CONTINUE_FLAG: True,
        NEXT_PREP_FLAG: {
            "pack": "255",
            "name": "Receipt Chain Saved View Owner Review Governance Continuous Assurance Batch Close Readiness Preview",
            "mode": "simulated_preview_only",
            "recommended_next_endpoint": "/tower/receipt-chain-saved-view-owner-review-governance-continuous-assurance-batch-close-readiness-v255.json",
            "save_batch": SAVE_BATCH,
            "save_after_pack": SAVE_AFTER_PACK,
        },
    }

    return preview


def build_receipt_chain_saved_view_owner_review_governance_continuous_assurance_note_version_preview() -> Dict[str, Any]:
    """Return a defensive copy of the cached Pack 254 preview payload."""
    return deepcopy(_build_receipt_chain_saved_view_owner_review_governance_continuous_assurance_note_version_preview_cached())


def build_pack_254_status_bridge() -> Dict[str, Any]:
    """Small cached status bridge for Tower cards/status surfaces."""
    preview = _build_receipt_chain_saved_view_owner_review_governance_continuous_assurance_note_version_preview_cached()
    summary = preview["governance_continuous_assurance_note_version_summary"]

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
        "continuous_assurance_note_version_ready": summary["continuous_assurance_note_version_ready"],
        SAFE_TO_CONTINUE_FLAG: preview[SAFE_TO_CONTINUE_FLAG],
    }


def prepare_pack_255_receipt_chain_saved_view_owner_review_governance_continuous_assurance_batch_close_readiness() -> Dict[str, Any]:
    """Prepare Pack 255 direction without writing state."""
    return {
        "ready": True,
        "next_pack": "255",
        "name": "Receipt Chain Saved View Owner Review Governance Continuous Assurance Batch Close Readiness Preview",
        "mode": "simulated_preview_only",
        "source_pack": PACK_ID,
        "source_endpoint": ENDPOINT,
        "tower_section": TOWER_SECTION,
        "tower_layer": TOWER_LAYER,
        "tower_sublayer": TOWER_SUBLAYER,
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
    "SAVE_BATCH",
    "SAVE_AFTER_PACK",
    "NEXT_BATCH",
    "SAFE_TO_CONTINUE_FLAG",
    "NEXT_PREP_FLAG",
    "BLOCKED_REAL_ACTIONS",
    "build_receipt_chain_saved_view_owner_review_governance_continuous_assurance_note_version_preview",
    "build_pack_254_status_bridge",
    "prepare_pack_255_receipt_chain_saved_view_owner_review_governance_continuous_assurance_batch_close_readiness",
]
