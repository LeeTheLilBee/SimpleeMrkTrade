"""
SEARCHABLE LABEL: TOWER_PACK_238_RECEIPT_CHAIN_SAVED_VIEW_OWNER_REVIEW_CROSS_BATCH_NOTE_DRAFT_PREVIEW_MODULE

Tower section:
- The Tower
- Operational Containment
- Receipt Chain Saved View Review Layer

Pack 238: Receipt Chain Saved View Owner Review Cross-Batch Note Draft Preview

This module is intentionally simulated/preview-only.

Purpose:
- Build safe note draft previews from Pack 237 cross-batch detail drawers.
- Preserve cross-batch review context across 221-225, 226-230, and 231-235.
- Prepare Pack 239 cross-batch note version preview.

Safety boundaries:
- No real cross-batch note writes, saves, submits, or deletes.
- No real drawer state writes.
- No real cross-batch index, link, status, or checkpoint writes.
- No real continuity, follow-up, or owner review writes.
- No real owner approval or denial.
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

from tower.receipt_chain_saved_view_owner_review_cross_batch_detail_drawer_v237 import (
    build_receipt_chain_saved_view_owner_review_cross_batch_detail_drawer_preview,
)


PACK_ID = "238"
PACK_NUMBER = 238
PACK_NAME = "Receipt Chain Saved View Owner Review Cross-Batch Note Draft Preview"
ENDPOINT = "/tower/receipt-chain-saved-view-owner-review-cross-batch-note-draft-v238.json"

TOWER_AREA = "The Tower"
TOWER_SECTION = "Operational Containment"
TOWER_LAYER = "Receipt Chain Saved View Review Layer"

SAVE_BATCH = "236-240"
SAVE_AFTER_PACK = 240
SAFE_TO_CONTINUE_FLAG = "safe_to_continue_to_pack_239"
NEXT_PREP_FLAG = "prepare_pack_239_receipt_chain_saved_view_owner_review_cross_batch_note_version"

BLOCKED_REAL_ACTIONS = (
    "real_cross_batch_note_write",
    "real_cross_batch_note_save",
    "real_cross_batch_note_submit",
    "real_cross_batch_note_delete",
    "real_cross_batch_note_version_write",
    "real_cross_batch_note_version_restore",
    "real_cross_batch_detail_state_write",
    "real_cross_batch_index_write",
    "real_cross_batch_link_write",
    "real_cross_batch_status_write",
    "real_cross_batch_checkpoint_write",
    "real_batch_close_write",
    "real_continuity_note_version_write",
    "real_continuity_note_write",
    "real_continuity_assignment_write",
    "real_continuity_status_write",
    "real_continuity_queue_write",
    "real_continuity_checkpoint_write",
    "real_followup_assignment_write",
    "real_followup_status_write",
    "real_followup_note_write",
    "real_followup_note_version_write",
    "real_owner_review_note_version_write",
    "real_owner_review_note_write",
    "real_owner_review_approve",
    "real_owner_review_deny",
    "real_owner_review_assign",
    "real_owner_review_status_write",
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
class CrossBatchNoteDraftCard:
    draft_id: str
    drawer_id: str
    batch_range: str
    batch_label: str
    batch_role: str
    label: str
    draft_status: str
    draft_mode: str
    template_type: str
    character_count_preview: int
    writes_state: bool
    executable: bool
    raw_evidence_visible: bool


@dataclass(frozen=True)
class CrossBatchNoteDraftField:
    field_id: str
    draft_id: str
    label: str
    field_type: str
    preview_value: str
    redaction_state: str
    editable_preview: bool
    writes_state: bool
    raw_evidence_visible: bool


@dataclass(frozen=True)
class CrossBatchNoteDraftAction:
    action_id: str
    draft_id: str
    label: str
    visible: bool
    enabled: bool
    result: str
    reason: str


@dataclass(frozen=True)
class CrossBatchNoteDraftCheckpoint:
    checkpoint_id: str
    label: str
    passed: bool
    result: str
    evidence_mode: str
    writes_state: bool


def _source_payload() -> Dict[str, Any]:
    return deepcopy(build_receipt_chain_saved_view_owner_review_cross_batch_detail_drawer_preview())


def _source_headers(source_payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    return deepcopy(source_payload.get("cross_batch_detail_headers", []))


def _build_draft_cards(headers: List[Dict[str, Any]]) -> List[CrossBatchNoteDraftCard]:
    cards: List[CrossBatchNoteDraftCard] = []

    for idx, header in enumerate(headers, start=1):
        cards.append(
            CrossBatchNoteDraftCard(
                draft_id=f"cross_batch_note_draft_238_{idx:03d}",
                drawer_id=header["drawer_id"],
                batch_range=header["batch_range"],
                batch_label=header["batch_label"],
                batch_role=header["batch_role"],
                label=f"Cross-batch note draft preview for {header['batch_label']} {header['batch_range']}",
                draft_status="cross_batch_note_draft_preview_ready",
                draft_mode="preview_only",
                template_type="owner_cross_batch_review_note",
                character_count_preview=310 + idx * 29,
                writes_state=False,
                executable=False,
                raw_evidence_visible=False,
            )
        )

    return cards


def _build_draft_fields(cards: List[CrossBatchNoteDraftCard]) -> List[CrossBatchNoteDraftField]:
    fields: List[CrossBatchNoteDraftField] = []

    for card in cards:
        fields.extend(
            [
                CrossBatchNoteDraftField(
                    field_id=f"{card.draft_id}_field_batch_summary",
                    draft_id=card.draft_id,
                    label="Batch summary",
                    field_type="textarea_preview",
                    preview_value=f"Preview note for {card.batch_label} {card.batch_range}. No note is written.",
                    redaction_state="safe_preview",
                    editable_preview=True,
                    writes_state=False,
                    raw_evidence_visible=False,
                ),
                CrossBatchNoteDraftField(
                    field_id=f"{card.draft_id}_field_cross_batch_context",
                    draft_id=card.draft_id,
                    label="Cross-batch context",
                    field_type="textarea_preview",
                    preview_value="Preview-only context linking owner review, follow-up, and continuity batches.",
                    redaction_state="safe_preview",
                    editable_preview=True,
                    writes_state=False,
                    raw_evidence_visible=False,
                ),
                CrossBatchNoteDraftField(
                    field_id=f"{card.draft_id}_field_repair_bridge",
                    draft_id=card.draft_id,
                    label="Repair bridge context",
                    field_type="textarea_preview",
                    preview_value="Preview-only note field preserving repaired 224-225 dependency bridge context.",
                    redaction_state="safe_preview",
                    editable_preview=True,
                    writes_state=False,
                    raw_evidence_visible=False,
                ),
                CrossBatchNoteDraftField(
                    field_id=f"{card.draft_id}_field_next_step",
                    draft_id=card.draft_id,
                    label="Next step preview",
                    field_type="textarea_preview",
                    preview_value="Preview-only next step toward cross-batch note version review.",
                    redaction_state="safe_preview",
                    editable_preview=True,
                    writes_state=False,
                    raw_evidence_visible=False,
                ),
                CrossBatchNoteDraftField(
                    field_id=f"{card.draft_id}_field_write_boundary",
                    draft_id=card.draft_id,
                    label="Write boundary",
                    field_type="locked_summary",
                    preview_value="Cross-batch note writes, saves, submits, deletes, version writes, index writes, links, status, saved-view actions, exports, and raw evidence reveal are blocked.",
                    redaction_state="safe_preview",
                    editable_preview=False,
                    writes_state=False,
                    raw_evidence_visible=False,
                ),
                CrossBatchNoteDraftField(
                    field_id=f"{card.draft_id}_field_evidence_boundary",
                    draft_id=card.draft_id,
                    label="Evidence boundary",
                    field_type="locked_summary",
                    preview_value="Raw evidence remains hidden. Only safe summaries and pointers are represented.",
                    redaction_state="redacted_pointer_only",
                    editable_preview=False,
                    writes_state=False,
                    raw_evidence_visible=False,
                ),
            ]
        )

    return fields


def _build_draft_actions(cards: List[CrossBatchNoteDraftCard]) -> List[CrossBatchNoteDraftAction]:
    actions: List[CrossBatchNoteDraftAction] = []

    for card in cards:
        actions.extend(
            [
                CrossBatchNoteDraftAction(
                    action_id=f"{card.draft_id}_action_preview",
                    draft_id=card.draft_id,
                    label="Preview cross-batch note draft",
                    visible=True,
                    enabled=True,
                    result="preview_allowed",
                    reason="Previewing a simulated cross-batch note draft does not write state.",
                ),
                CrossBatchNoteDraftAction(
                    action_id=f"{card.draft_id}_action_save",
                    draft_id=card.draft_id,
                    label="Save cross-batch note",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Saving cross-batch notes is blocked.",
                ),
                CrossBatchNoteDraftAction(
                    action_id=f"{card.draft_id}_action_submit",
                    draft_id=card.draft_id,
                    label="Submit cross-batch note",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Submitting cross-batch notes is blocked.",
                ),
                CrossBatchNoteDraftAction(
                    action_id=f"{card.draft_id}_action_delete",
                    draft_id=card.draft_id,
                    label="Delete cross-batch note draft",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Deleting cross-batch note drafts is blocked.",
                ),
                CrossBatchNoteDraftAction(
                    action_id=f"{card.draft_id}_action_write_index",
                    draft_id=card.draft_id,
                    label="Write note to cross-batch index",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Cross-batch index writes are blocked.",
                ),
                CrossBatchNoteDraftAction(
                    action_id=f"{card.draft_id}_action_link_batches",
                    draft_id=card.draft_id,
                    label="Create link from note",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Cross-batch link writes are blocked.",
                ),
                CrossBatchNoteDraftAction(
                    action_id=f"{card.draft_id}_action_export_note",
                    draft_id=card.draft_id,
                    label="Export note packet",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Exports are blocked in preview mode.",
                ),
                CrossBatchNoteDraftAction(
                    action_id=f"{card.draft_id}_action_apply_saved_view",
                    draft_id=card.draft_id,
                    label="Apply saved view",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Saved-view apply actions are blocked.",
                ),
            ]
        )

    return actions


def _build_checkpoints() -> List[CrossBatchNoteDraftCheckpoint]:
    return [
        CrossBatchNoteDraftCheckpoint(
            checkpoint_id="cross_batch_note_draft_checkpoint_238_001",
            label="Cross-batch note draft cards are preview-only",
            passed=True,
            result="passed",
            evidence_mode="safe_summary_only",
            writes_state=False,
        ),
        CrossBatchNoteDraftCheckpoint(
            checkpoint_id="cross_batch_note_draft_checkpoint_238_002",
            label="Draft fields do not write state or reveal raw evidence",
            passed=True,
            result="passed",
            evidence_mode="redacted_pointer_only",
            writes_state=False,
        ),
        CrossBatchNoteDraftCheckpoint(
            checkpoint_id="cross_batch_note_draft_checkpoint_238_003",
            label="Save, submit, delete, index write, link write, export, and saved-view actions remain blocked",
            passed=True,
            result="passed",
            evidence_mode="blocked_action_summary",
            writes_state=False,
        ),
        CrossBatchNoteDraftCheckpoint(
            checkpoint_id="cross_batch_note_draft_checkpoint_238_004",
            label="Repair bridge note context remains safe preview-only",
            passed=True,
            result="passed",
            evidence_mode="safe_summary_only",
            writes_state=False,
        ),
        CrossBatchNoteDraftCheckpoint(
            checkpoint_id="cross_batch_note_draft_checkpoint_238_005",
            label="Ready for Pack 239 cross-batch note version preview",
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
            "reason": "Pack 238 previews cross-batch note drafts only and cannot write notes, index, links, review, queue, saved-view, archive, evidence, or action state.",
        }
        for action in BLOCKED_REAL_ACTIONS
    ]


@lru_cache(maxsize=1)
def _build_receipt_chain_saved_view_owner_review_cross_batch_note_draft_preview_cached() -> Dict[str, Any]:
    source_payload = _source_payload()
    headers = _source_headers(source_payload)

    cards_raw = _build_draft_cards(headers)
    fields_raw = _build_draft_fields(cards_raw)
    actions_raw = _build_draft_actions(cards_raw)
    checkpoints_raw = _build_checkpoints()

    cards = [asdict(card) for card in cards_raw]
    fields = [asdict(field) for field in fields_raw]
    actions = [asdict(action) for action in actions_raw]
    checkpoints = [asdict(checkpoint) for checkpoint in checkpoints_raw]

    enabled_action_count = sum(1 for action in actions if action["enabled"] is True)
    blocked_action_count = sum(1 for action in actions if action["enabled"] is False)
    editable_field_count = sum(1 for field in fields if field["editable_preview"] is True)
    locked_field_count = sum(1 for field in fields if field["editable_preview"] is False)
    redacted_field_count = sum(1 for field in fields if field["redaction_state"] == "redacted_pointer_only")

    all_cards_preview_only = all(card["draft_mode"] == "preview_only" for card in cards)
    all_cards_no_writes = all(card["writes_state"] is False for card in cards)
    all_cards_non_executable = all(card["executable"] is False for card in cards)
    all_cards_no_raw_evidence = all(card["raw_evidence_visible"] is False for card in cards)
    all_fields_no_writes = all(field["writes_state"] is False for field in fields)
    all_fields_no_raw_evidence = all(field["raw_evidence_visible"] is False for field in fields)
    all_actions_safe = all(action["result"] in {"preview_allowed", "blocked_preview_only"} for action in actions)
    all_checkpoints_passed = all(checkpoint["passed"] is True for checkpoint in checkpoints)
    all_checkpoints_no_writes = all(checkpoint["writes_state"] is False for checkpoint in checkpoints)

    cross_batch_note_draft_ready = all([
        all_cards_preview_only,
        all_cards_no_writes,
        all_cards_non_executable,
        all_cards_no_raw_evidence,
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
        "save_batch": SAVE_BATCH,
        "save_after_pack": SAVE_AFTER_PACK,
        "cached": True,
        "non_recursive": True,
        "simulation_only": True,
        "preview_only": True,
        "receipt_chain_layer": "saved_view_owner_review_cross_batch_note_draft_preview",
        "source_pack": source_payload.get("pack"),
        "source_endpoint": source_payload.get("endpoint"),
        "source_status": source_payload.get("status"),
        "source_readiness": source_payload.get("readiness"),
        "source_safe_to_continue": source_payload.get("safe_to_continue_to_pack_238"),
        "cross_batch_note_draft_cards": cards,
        "cross_batch_note_draft_fields": fields,
        "cross_batch_note_draft_actions": actions,
        "cross_batch_note_draft_checkpoints": checkpoints,
        "cross_batch_note_draft_summary": {
            "source_detail_drawer_count": len(headers),
            "draft_card_count": len(cards),
            "draft_field_count": len(fields),
            "draft_action_count": len(actions),
            "checkpoint_count": len(checkpoints),
            "enabled_action_count": enabled_action_count,
            "blocked_action_count": blocked_action_count,
            "editable_field_count": editable_field_count,
            "locked_field_count": locked_field_count,
            "redacted_field_count": redacted_field_count,
            "all_cards_preview_only": all_cards_preview_only,
            "all_cards_no_writes": all_cards_no_writes,
            "all_cards_non_executable": all_cards_non_executable,
            "all_cards_no_raw_evidence": all_cards_no_raw_evidence,
            "all_fields_no_writes": all_fields_no_writes,
            "all_fields_no_raw_evidence": all_fields_no_raw_evidence,
            "all_actions_safe": all_actions_safe,
            "all_checkpoints_passed": all_checkpoints_passed,
            "all_checkpoints_no_writes": all_checkpoints_no_writes,
            "cross_batch_note_draft_ready": cross_batch_note_draft_ready,
            "real_cross_batch_note_write_enabled": False,
            "real_cross_batch_note_save_enabled": False,
            "real_cross_batch_note_submit_enabled": False,
            "real_cross_batch_note_delete_enabled": False,
            "real_cross_batch_note_version_write_enabled": False,
            "real_cross_batch_index_write_enabled": False,
            "real_cross_batch_link_write_enabled": False,
            "real_cross_batch_status_write_enabled": False,
            "real_review_write_enabled": False,
            "real_saved_view_mutation_enabled": False,
            "real_archive_write_enabled": False,
            "raw_evidence_visible": False,
            "real_action_execution_enabled": False,
        },
        "safety_invariants": {
            "no_real_cross_batch_note_write": True,
            "no_real_cross_batch_note_save": True,
            "no_real_cross_batch_note_submit": True,
            "no_real_cross_batch_note_delete": True,
            "no_real_cross_batch_note_version_write": True,
            "no_real_cross_batch_note_version_restore": True,
            "no_real_cross_batch_detail_state_write": True,
            "no_real_cross_batch_index_write": True,
            "no_real_cross_batch_link_write": True,
            "no_real_cross_batch_status_write": True,
            "no_real_cross_batch_checkpoint_write": True,
            "no_real_batch_close_write": True,
            "no_real_continuity_write": True,
            "no_real_followup_write": True,
            "no_real_owner_review_write": True,
            "no_real_owner_review_approve": True,
            "no_real_owner_review_deny": True,
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
        "pack_238_acceptance": {
            "cross_batch_note_draft_cards_built": True,
            "cross_batch_note_draft_fields_built": True,
            "cross_batch_note_draft_actions_built": True,
            "cross_batch_note_write_save_submit_delete_blocked": True,
            "cross_batch_index_link_status_export_blocked": True,
            "ready_for_cross_batch_note_version": True,
        },
        SAFE_TO_CONTINUE_FLAG: True,
        NEXT_PREP_FLAG: {
            "pack": "239",
            "name": "Receipt Chain Saved View Owner Review Cross-Batch Note Version Preview",
            "mode": "simulated_preview_only",
            "recommended_next_endpoint": "/tower/receipt-chain-saved-view-owner-review-cross-batch-note-version-v239.json",
            "save_batch": SAVE_BATCH,
            "save_after_pack": SAVE_AFTER_PACK,
        },
    }

    return preview


def build_receipt_chain_saved_view_owner_review_cross_batch_note_draft_preview() -> Dict[str, Any]:
    """Return a defensive copy of the cached Pack 238 preview payload."""
    return deepcopy(_build_receipt_chain_saved_view_owner_review_cross_batch_note_draft_preview_cached())


def build_pack_238_status_bridge() -> Dict[str, Any]:
    """Small cached status bridge for Tower cards/status surfaces."""
    preview = _build_receipt_chain_saved_view_owner_review_cross_batch_note_draft_preview_cached()
    summary = preview["cross_batch_note_draft_summary"]

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
        "draft_card_count": summary["draft_card_count"],
        "draft_field_count": summary["draft_field_count"],
        "draft_action_count": summary["draft_action_count"],
        "cross_batch_note_draft_ready": summary["cross_batch_note_draft_ready"],
        SAFE_TO_CONTINUE_FLAG: preview[SAFE_TO_CONTINUE_FLAG],
    }


def prepare_pack_239_receipt_chain_saved_view_owner_review_cross_batch_note_version() -> Dict[str, Any]:
    """Prepare Pack 239 direction without writing state."""
    return {
        "ready": True,
        "next_pack": "239",
        "name": "Receipt Chain Saved View Owner Review Cross-Batch Note Version Preview",
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
    "build_receipt_chain_saved_view_owner_review_cross_batch_note_draft_preview",
    "build_pack_238_status_bridge",
    "prepare_pack_239_receipt_chain_saved_view_owner_review_cross_batch_note_version",
]
