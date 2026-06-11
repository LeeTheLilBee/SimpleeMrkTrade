"""
SEARCHABLE LABEL: TOWER_PACK_224_REBUILT_OWNER_REVIEW_NOTE_VERSION_PREVIEW_MODULE
"""

from __future__ import annotations

from copy import deepcopy
from functools import lru_cache
from typing import Any, Dict, List

PACK_ID = "224"
PACK_NUMBER = 224
PACK_NAME = "Receipt Chain Saved View Owner Review Note Version Preview"
ENDPOINT = "/tower/receipt-chain-saved-view-owner-review-note-version-v224.json"

TOWER_AREA = "The Tower"
TOWER_SECTION = "Operational Containment"
TOWER_LAYER = "Receipt Chain Saved View Review Layer"
SAVE_BATCH = "221-225"
SAVE_AFTER_PACK = 225

BLOCKED_REAL_ACTIONS = (
    "real_owner_note_version_write",
    "real_owner_note_version_restore",
    "real_owner_note_version_apply",
    "real_owner_note_write",
    "real_owner_note_save",
    "real_owner_note_submit",
    "real_owner_note_delete",
    "real_owner_review_approve",
    "real_owner_review_deny",
    "real_saved_view_mutation",
    "real_archive_write",
    "raw_evidence_reveal",
    "real_action_execution",
)


def _version_cards() -> List[Dict[str, Any]]:
    cards = []
    for idx in range(1, 7):
        for version in (1, 2):
            cards.append({
                "version_id": f"owner_review_note_version_224_{idx:03d}_v{version}",
                "draft_id": f"owner_review_note_draft_223_{idx:03d}",
                "queue_item_id": f"owner_review_queue_221_{idx:03d}",
                "label": f"Owner review note version {version} preview {idx}",
                "version_status": "version_preview_ready",
                "version_mode": "preview_only",
                "changed_field_count": 4 + version,
                "writes_state": False,
                "executable": False,
                "raw_evidence_visible": False,
            })
    return cards


def _compare_rows(cards: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    rows = []
    fields = [
        ("summary", "safe_preview"),
        ("reason", "safe_preview"),
        ("owner_action_boundary", "safe_preview"),
        ("evidence_boundary", "redacted_pointer_only"),
    ]
    for card in cards:
        for field_name, redaction_state in fields:
            rows.append({
                "compare_row_id": f"{card['version_id']}_{field_name}",
                "version_id": card["version_id"],
                "draft_id": card["draft_id"],
                "field_name": field_name,
                "previous_preview": "Previous safe preview",
                "current_preview": "Current safe preview",
                "change_type": "simulated_preview_change",
                "redaction_state": redaction_state,
                "writes_state": False,
                "executable": False,
                "raw_evidence_visible": False,
            })
    return rows


def _actions(cards: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    actions = []
    specs = [
        ("preview", True, "preview_allowed"),
        ("restore", False, "blocked_preview_only"),
        ("save", False, "blocked_preview_only"),
        ("submit", False, "blocked_preview_only"),
        ("delete", False, "blocked_preview_only"),
        ("apply_to_review", False, "blocked_preview_only"),
    ]
    for card in cards:
        for key, enabled, result in specs:
            actions.append({
                "action_id": f"{card['version_id']}_action_{key}",
                "version_id": card["version_id"],
                "label": key.replace("_", " ").title(),
                "visible": True,
                "enabled": enabled,
                "result": result,
                "reason": "Preview-only action boundary.",
            })
    return actions


def _checkpoints() -> List[Dict[str, Any]]:
    return [
        {
            "checkpoint_id": f"owner_review_note_version_checkpoint_224_{idx:03d}",
            "label": label,
            "passed": True,
            "result": "passed",
            "evidence_mode": "safe_summary_only",
            "writes_state": False,
        }
        for idx, label in enumerate([
            "Version cards are preview-only",
            "Compare rows do not write state",
            "Restore/save/submit/delete/apply actions are blocked",
            "Raw evidence remains hidden",
            "Ready for Pack 225 batch close readiness",
        ], start=1)
    ]


@lru_cache(maxsize=1)
def _cached_payload() -> Dict[str, Any]:
    cards = _version_cards()
    rows = _compare_rows(cards)
    actions = _actions(cards)
    checkpoints = _checkpoints()

    summary = {
        "version_card_count": len(cards),
        "compare_row_count": len(rows),
        "version_action_count": len(actions),
        "checkpoint_count": len(checkpoints),
        "enabled_action_count": sum(1 for row in actions if row["enabled"]),
        "blocked_action_count": sum(1 for row in actions if not row["enabled"]),
        "all_cards_preview_only": all(row["version_mode"] == "preview_only" for row in cards),
        "all_cards_no_writes": all(row["writes_state"] is False for row in cards),
        "all_rows_no_writes": all(row["writes_state"] is False for row in rows),
        "all_actions_safe": all(row["result"] in {"preview_allowed", "blocked_preview_only"} for row in actions),
        "all_checkpoints_passed": all(row["passed"] is True for row in checkpoints),
        "note_version_preview_ready": True,
        "real_owner_note_version_write_enabled": False,
        "real_owner_note_version_restore_enabled": False,
        "real_owner_note_save_enabled": False,
        "real_owner_note_submit_enabled": False,
        "real_owner_note_delete_enabled": False,
        "real_owner_approval_enabled": False,
        "real_owner_denial_enabled": False,
        "real_saved_view_mutation_enabled": False,
        "real_archive_write_enabled": False,
        "raw_evidence_visible": False,
        "real_action_execution_enabled": False,
    }

    return {
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
        "source_pack": "223",
        "source_endpoint": "/tower/receipt-chain-saved-view-owner-review-note-draft-v223.json",
        "source_status": "ready",
        "source_readiness": 100,
        "source_safe_to_continue": True,
        "owner_note_version_cards": cards,
        "owner_note_version_compare_rows": rows,
        "owner_note_version_actions": actions,
        "owner_note_version_checkpoints": checkpoints,
        "owner_note_version_summary": summary,
        "safety_invariants": {
            "no_real_owner_review_note_version_write": True,
            "no_real_owner_review_note_version_restore": True,
            "no_real_owner_review_note_write": True,
            "no_real_owner_review_approve": True,
            "no_real_owner_review_deny": True,
            "no_real_saved_view_write": True,
            "no_archive_write": True,
            "no_raw_evidence_reveal": True,
            "no_real_action_execution": True,
            "cached_non_recursive_builder": True,
        },
        "blocked_action_matrix": [
            {"action": action, "allowed": False, "result": "blocked_preview_only"}
            for action in BLOCKED_REAL_ACTIONS
        ],
        "safe_to_continue_to_pack_225": True,
        "prepare_pack_225_saved_view_owner_review_batch_close_readiness": {
            "pack": "225",
            "name": "Receipt Chain Saved View Owner Review Batch Close Readiness Preview",
            "mode": "simulated_preview_only",
            "save_batch": SAVE_BATCH,
            "save_after_pack": SAVE_AFTER_PACK,
        },
    }


def build_receipt_chain_saved_view_owner_review_note_version_preview() -> Dict[str, Any]:
    return deepcopy(_cached_payload())


def build_pack_224_status_bridge() -> Dict[str, Any]:
    payload = _cached_payload()
    summary = payload["owner_note_version_summary"]
    return {
        "pack": payload["pack"],
        "pack_number": payload["pack_number"],
        "pack_name": payload["pack_name"],
        "status": payload["status"],
        "readiness": payload["readiness"],
        "endpoint": payload["endpoint"],
        "tower_section": payload["tower_section"],
        "tower_layer": payload["tower_layer"],
        "save_batch": payload["save_batch"],
        "save_after_pack": payload["save_after_pack"],
        "cached": payload["cached"],
        "non_recursive": payload["non_recursive"],
        "preview_only": payload["preview_only"],
        "source_pack": payload["source_pack"],
        "source_status": payload["source_status"],
        "version_card_count": summary["version_card_count"],
        "compare_row_count": summary["compare_row_count"],
        "version_action_count": summary["version_action_count"],
        "note_version_preview_ready": summary["note_version_preview_ready"],
        "safe_to_continue_to_pack_225": payload["safe_to_continue_to_pack_225"],
    }


def prepare_pack_225_saved_view_owner_review_batch_close_readiness() -> Dict[str, Any]:
    return {
        "ready": True,
        "next_pack": "225",
        "name": "Receipt Chain Saved View Owner Review Batch Close Readiness Preview",
        "mode": "simulated_preview_only",
        "source_pack": PACK_ID,
        "source_endpoint": ENDPOINT,
        "tower_section": TOWER_SECTION,
        "tower_layer": TOWER_LAYER,
        "save_batch": SAVE_BATCH,
        "save_after_pack": SAVE_AFTER_PACK,
        "safe_to_continue": True,
    }
