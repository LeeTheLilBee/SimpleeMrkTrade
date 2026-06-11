"""
SEARCHABLE LABEL: TOWER_PACK_223_RECEIPT_CHAIN_SAVED_VIEW_OWNER_REVIEW_NOTE_DRAFT_PREVIEW_MODULE

Tower section:
- The Tower
- Operational Containment
- Receipt Chain Saved View Review Layer

Pack 223: Receipt Chain Saved View Owner Review Note Draft Preview

This module is intentionally simulated/preview-only.

Safety boundaries:
- No real owner notes written.
- No real owner approval or denial.
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

from tower.receipt_chain_saved_view_owner_review_detail_drawer_v222 import (
    build_receipt_chain_saved_view_owner_review_detail_drawer_preview,
)


PACK_ID = "223"
PACK_NUMBER = 223
PACK_NAME = "Receipt Chain Saved View Owner Review Note Draft Preview"
ENDPOINT = "/tower/receipt-chain-saved-view-owner-review-note-draft-v223.json"

TOWER_AREA = "The Tower"
TOWER_SECTION = "Operational Containment"
TOWER_LAYER = "Receipt Chain Saved View Review Layer"

SAVE_BATCH = "221-225"
SAVE_AFTER_PACK = 225
SAFE_TO_CONTINUE_FLAG = "safe_to_continue_to_pack_224"
NEXT_PREP_FLAG = "prepare_pack_224_saved_view_owner_review_note_version_preview"

BLOCKED_REAL_ACTIONS = (
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
class OwnerNoteDraftCard:
    draft_id: str
    queue_item_id: str
    drawer_id: str
    review_key: str
    label: str
    draft_status: str
    draft_mode: str
    template_type: str
    character_count_preview: int
    writes_state: bool
    executable: bool


@dataclass(frozen=True)
class OwnerNoteDraftField:
    field_id: str
    draft_id: str
    label: str
    field_type: str
    preview_value: str
    redaction_state: str
    editable_preview: bool
    writes_state: bool


@dataclass(frozen=True)
class OwnerNoteDraftAction:
    action_id: str
    draft_id: str
    label: str
    visible: bool
    enabled: bool
    result: str
    reason: str


@dataclass(frozen=True)
class OwnerNoteDraftSafetyCheck:
    check_id: str
    label: str
    passed: bool
    result: str
    evidence_mode: str
    writes_state: bool


def _source_payload() -> Dict[str, Any]:
    return deepcopy(build_receipt_chain_saved_view_owner_review_detail_drawer_preview())


def _source_headers(source_payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    return deepcopy(source_payload.get("detail_drawer_headers", []))


def _build_note_draft_cards(headers: List[Dict[str, Any]]) -> List[OwnerNoteDraftCard]:
    cards: List[OwnerNoteDraftCard] = []

    for idx, header in enumerate(headers, start=1):
        cards.append(
            OwnerNoteDraftCard(
                draft_id=f"owner_note_draft_223_{idx:03d}",
                queue_item_id=header["queue_item_id"],
                drawer_id=header["drawer_id"],
                review_key=header["review_key"],
                label=f"Draft note preview for {header['label']}",
                draft_status="draft_preview_ready",
                draft_mode="preview_only",
                template_type="owner_review_note_summary",
                character_count_preview=180 + idx * 11,
                writes_state=False,
                executable=False,
            )
        )

    return cards


def _build_note_draft_fields(cards: List[OwnerNoteDraftCard]) -> List[OwnerNoteDraftField]:
    fields: List[OwnerNoteDraftField] = []

    for card in cards:
        fields.extend(
            [
                OwnerNoteDraftField(
                    field_id=f"{card.draft_id}_field_summary",
                    draft_id=card.draft_id,
                    label="Owner review summary",
                    field_type="textarea_preview",
                    preview_value="Preview-only owner review summary. No note is written or saved.",
                    redaction_state="safe_preview",
                    editable_preview=True,
                    writes_state=False,
                ),
                OwnerNoteDraftField(
                    field_id=f"{card.draft_id}_field_reason",
                    draft_id=card.draft_id,
                    label="Reason",
                    field_type="textarea_preview",
                    preview_value="Preview-only reason field for later owner review note drafting.",
                    redaction_state="safe_preview",
                    editable_preview=True,
                    writes_state=False,
                ),
                OwnerNoteDraftField(
                    field_id=f"{card.draft_id}_field_evidence_boundary",
                    draft_id=card.draft_id,
                    label="Evidence boundary",
                    field_type="locked_summary",
                    preview_value="Raw evidence remains hidden; only safe pointer summaries are available.",
                    redaction_state="redacted_pointer_only",
                    editable_preview=False,
                    writes_state=False,
                ),
                OwnerNoteDraftField(
                    field_id=f"{card.draft_id}_field_decision_boundary",
                    draft_id=card.draft_id,
                    label="Decision boundary",
                    field_type="locked_summary",
                    preview_value="Approve, deny, submit, save, and delete are blocked in preview mode.",
                    redaction_state="safe_preview",
                    editable_preview=False,
                    writes_state=False,
                ),
            ]
        )

    return fields


def _build_note_draft_actions(cards: List[OwnerNoteDraftCard]) -> List[OwnerNoteDraftAction]:
    actions: List[OwnerNoteDraftAction] = []

    for card in cards:
        actions.extend(
            [
                OwnerNoteDraftAction(
                    action_id=f"{card.draft_id}_action_preview",
                    draft_id=card.draft_id,
                    label="Preview draft",
                    visible=True,
                    enabled=True,
                    result="preview_allowed",
                    reason="Previewing a simulated draft does not write note state.",
                ),
                OwnerNoteDraftAction(
                    action_id=f"{card.draft_id}_action_save",
                    draft_id=card.draft_id,
                    label="Save note",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Saving owner notes is blocked in Pack 223.",
                ),
                OwnerNoteDraftAction(
                    action_id=f"{card.draft_id}_action_submit",
                    draft_id=card.draft_id,
                    label="Submit note",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Submitting owner notes is blocked in Pack 223.",
                ),
                OwnerNoteDraftAction(
                    action_id=f"{card.draft_id}_action_delete",
                    draft_id=card.draft_id,
                    label="Delete note draft",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Deleting owner note drafts is blocked in Pack 223.",
                ),
                OwnerNoteDraftAction(
                    action_id=f"{card.draft_id}_action_approve_with_note",
                    draft_id=card.draft_id,
                    label="Approve with note",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Approval execution is blocked in this preview lane.",
                ),
                OwnerNoteDraftAction(
                    action_id=f"{card.draft_id}_action_deny_with_note",
                    draft_id=card.draft_id,
                    label="Deny with note",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Denial execution is blocked in this preview lane.",
                ),
            ]
        )

    return actions


def _build_safety_checks() -> List[OwnerNoteDraftSafetyCheck]:
    return [
        OwnerNoteDraftSafetyCheck(
            check_id="owner_note_draft_check_223_001",
            label="Draft cards are preview-only",
            passed=True,
            result="passed",
            evidence_mode="safe_summary_only",
            writes_state=False,
        ),
        OwnerNoteDraftSafetyCheck(
            check_id="owner_note_draft_check_223_002",
            label="Draft fields do not write state",
            passed=True,
            result="passed",
            evidence_mode="safe_summary_only",
            writes_state=False,
        ),
        OwnerNoteDraftSafetyCheck(
            check_id="owner_note_draft_check_223_003",
            label="Draft actions block save, submit, delete, approve, and deny",
            passed=True,
            result="passed",
            evidence_mode="blocked_action_summary",
            writes_state=False,
        ),
        OwnerNoteDraftSafetyCheck(
            check_id="owner_note_draft_check_223_004",
            label="Raw evidence remains hidden",
            passed=True,
            result="passed",
            evidence_mode="redacted_pointer_only",
            writes_state=False,
        ),
        OwnerNoteDraftSafetyCheck(
            check_id="owner_note_draft_check_223_005",
            label="Ready for Pack 224 note version preview",
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
            "reason": "Pack 223 previews owner review note drafts only and cannot write notes, queue, saved-view, archive, evidence, or action state.",
        }
        for action in BLOCKED_REAL_ACTIONS
    ]


@lru_cache(maxsize=1)
def _build_receipt_chain_saved_view_owner_review_note_draft_preview_cached() -> Dict[str, Any]:
    source_payload = _source_payload()
    headers = _source_headers(source_payload)

    draft_cards_raw = _build_note_draft_cards(headers)
    draft_fields_raw = _build_note_draft_fields(draft_cards_raw)
    draft_actions_raw = _build_note_draft_actions(draft_cards_raw)
    safety_checks_raw = _build_safety_checks()

    draft_cards = [asdict(card) for card in draft_cards_raw]
    draft_fields = [asdict(field) for field in draft_fields_raw]
    draft_actions = [asdict(action) for action in draft_actions_raw]
    safety_checks = [asdict(check) for check in safety_checks_raw]

    enabled_action_count = sum(1 for action in draft_actions if action["enabled"] is True)
    blocked_action_count = sum(1 for action in draft_actions if action["enabled"] is False)
    editable_preview_field_count = sum(1 for field in draft_fields if field["editable_preview"] is True)
    locked_field_count = sum(1 for field in draft_fields if field["editable_preview"] is False)

    all_cards_preview_only = all(card["draft_mode"] == "preview_only" for card in draft_cards)
    all_cards_no_writes = all(card["writes_state"] is False for card in draft_cards)
    all_cards_non_executable = all(card["executable"] is False for card in draft_cards)
    all_fields_no_writes = all(field["writes_state"] is False for field in draft_fields)
    all_actions_safe = all(action["result"] in {"preview_allowed", "blocked_preview_only"} for action in draft_actions)
    all_checks_passed = all(check["passed"] is True for check in safety_checks)
    all_checks_no_writes = all(check["writes_state"] is False for check in safety_checks)

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
        "receipt_chain_layer": "saved_view_owner_review_note_draft_preview",
        "source_pack": source_payload.get("pack"),
        "source_endpoint": source_payload.get("endpoint"),
        "source_status": source_payload.get("status"),
        "source_readiness": source_payload.get("readiness"),
        "source_safe_to_continue": source_payload.get("safe_to_continue_to_pack_223"),
        "owner_note_draft_cards": draft_cards,
        "owner_note_draft_fields": draft_fields,
        "owner_note_draft_actions": draft_actions,
        "owner_note_draft_safety_checks": safety_checks,
        "owner_note_draft_summary": {
            "source_detail_drawer_count": len(headers),
            "draft_card_count": len(draft_cards),
            "draft_field_count": len(draft_fields),
            "draft_action_count": len(draft_actions),
            "safety_check_count": len(safety_checks),
            "enabled_action_count": enabled_action_count,
            "blocked_action_count": blocked_action_count,
            "editable_preview_field_count": editable_preview_field_count,
            "locked_field_count": locked_field_count,
            "all_cards_preview_only": all_cards_preview_only,
            "all_cards_no_writes": all_cards_no_writes,
            "all_cards_non_executable": all_cards_non_executable,
            "all_fields_no_writes": all_fields_no_writes,
            "all_actions_safe": all_actions_safe,
            "all_checks_passed": all_checks_passed,
            "all_checks_no_writes": all_checks_no_writes,
            "note_draft_preview_ready": all([
                all_cards_preview_only,
                all_cards_no_writes,
                all_cards_non_executable,
                all_fields_no_writes,
                all_actions_safe,
                all_checks_passed,
                all_checks_no_writes,
            ]),
            "real_owner_note_write_enabled": False,
            "real_owner_note_save_enabled": False,
            "real_owner_note_submit_enabled": False,
            "real_owner_note_delete_enabled": False,
            "real_owner_approval_enabled": False,
            "real_owner_denial_enabled": False,
            "real_queue_state_write_enabled": False,
            "real_saved_view_mutation_enabled": False,
            "real_archive_write_enabled": False,
            "raw_evidence_visible": False,
            "real_action_execution_enabled": False,
        },
        "safety_invariants": {
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
        "pack_223_acceptance": {
            "note_draft_cards_built": True,
            "note_draft_fields_built": True,
            "note_draft_actions_built": True,
            "note_write_save_submit_delete_blocked": True,
            "owner_decision_actions_blocked": True,
            "ready_for_note_version_preview": True,
        },
        SAFE_TO_CONTINUE_FLAG: True,
        NEXT_PREP_FLAG: {
            "pack": "224",
            "name": "Receipt Chain Saved View Owner Review Note Version Preview",
            "mode": "simulated_preview_only",
            "recommended_next_endpoint": "/tower/receipt-chain-saved-view-owner-review-note-version-v224.json",
            "save_batch": SAVE_BATCH,
            "save_after_pack": SAVE_AFTER_PACK,
        },
    }

    return preview


def build_receipt_chain_saved_view_owner_review_note_draft_preview() -> Dict[str, Any]:
    """Return a defensive copy of the cached Pack 223 preview payload."""
    return deepcopy(_build_receipt_chain_saved_view_owner_review_note_draft_preview_cached())


def build_pack_223_status_bridge() -> Dict[str, Any]:
    """Small cached status bridge for Tower cards/status surfaces."""
    preview = _build_receipt_chain_saved_view_owner_review_note_draft_preview_cached()
    summary = preview["owner_note_draft_summary"]

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
        "note_draft_preview_ready": summary["note_draft_preview_ready"],
        SAFE_TO_CONTINUE_FLAG: preview[SAFE_TO_CONTINUE_FLAG],
    }


def prepare_pack_224_saved_view_owner_review_note_version_preview() -> Dict[str, Any]:
    """Prepare Pack 224 direction without writing state."""
    return {
        "ready": True,
        "next_pack": "224",
        "name": "Receipt Chain Saved View Owner Review Note Version Preview",
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
    "build_receipt_chain_saved_view_owner_review_note_draft_preview",
    "build_pack_223_status_bridge",
    "prepare_pack_224_saved_view_owner_review_note_version_preview",
]
