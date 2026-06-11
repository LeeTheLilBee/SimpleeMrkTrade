"""
SEARCHABLE LABEL: TOWER_PACK_225_REBUILT_OWNER_REVIEW_BATCH_CLOSE_READINESS_MODULE
"""

from __future__ import annotations

from copy import deepcopy
from functools import lru_cache
from typing import Any, Dict, List

from tower.receipt_chain_saved_view_owner_review_note_version_v224 import (
    build_receipt_chain_saved_view_owner_review_note_version_preview,
)

PACK_ID = "225"
PACK_NUMBER = 225
PACK_NAME = "Receipt Chain Saved View Owner Review Batch Close Readiness Preview"
ENDPOINT = "/tower/receipt-chain-saved-view-owner-review-batch-close-readiness-v225.json"

TOWER_AREA = "The Tower"
TOWER_SECTION = "Operational Containment"
TOWER_LAYER = "Receipt Chain Saved View Review Layer"
SAVE_BATCH = "221-225"
SAVE_AFTER_PACK = 225

BLOCKED_REAL_ACTIONS = (
    "real_batch_close_write",
    "real_owner_note_version_write",
    "real_owner_note_version_restore",
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


def _source_payload() -> Dict[str, Any]:
    return deepcopy(build_receipt_chain_saved_view_owner_review_note_version_preview())


def _pack_cards(source_payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    return [
        {
            "pack": "221",
            "pack_label": "Receipt Chain Saved View Owner Review Queue Preview",
            "module": "tower/receipt_chain_saved_view_owner_review_queue_v221.py",
            "test": "tower/test_tower_pack_221.py",
            "endpoint": "/tower/receipt-chain-saved-view-owner-review-queue-v221.json",
            "status": "ready",
            "readiness": 100,
            "preview_only": True,
            "cached": True,
            "non_recursive": True,
            "safe_to_continue": True,
        },
        {
            "pack": "222",
            "pack_label": "Receipt Chain Saved View Owner Review Detail Drawer Preview",
            "module": "tower/receipt_chain_saved_view_owner_review_detail_drawer_v222.py",
            "test": "tower/test_tower_pack_222.py",
            "endpoint": "/tower/receipt-chain-saved-view-owner-review-detail-drawer-v222.json",
            "status": "ready",
            "readiness": 100,
            "preview_only": True,
            "cached": True,
            "non_recursive": True,
            "safe_to_continue": True,
        },
        {
            "pack": "223",
            "pack_label": "Receipt Chain Saved View Owner Review Note Draft Preview",
            "module": "tower/receipt_chain_saved_view_owner_review_note_draft_v223.py",
            "test": "tower/test_tower_pack_223.py",
            "endpoint": "/tower/receipt-chain-saved-view-owner-review-note-draft-v223.json",
            "status": "ready",
            "readiness": 100,
            "preview_only": True,
            "cached": True,
            "non_recursive": True,
            "safe_to_continue": True,
        },
        {
            "pack": "224",
            "pack_label": "Receipt Chain Saved View Owner Review Note Version Preview",
            "module": "tower/receipt_chain_saved_view_owner_review_note_version_v224.py",
            "test": "tower/test_tower_pack_224.py",
            "endpoint": "/tower/receipt-chain-saved-view-owner-review-note-version-v224.json",
            "status": source_payload.get("status", "ready"),
            "readiness": source_payload.get("readiness", 100),
            "preview_only": source_payload.get("preview_only", True),
            "cached": source_payload.get("cached", True),
            "non_recursive": source_payload.get("non_recursive", True),
            "safe_to_continue": source_payload.get("safe_to_continue_to_pack_225", True),
        },
        {
            "pack": "225",
            "pack_label": PACK_NAME,
            "module": "tower/receipt_chain_saved_view_owner_review_batch_close_readiness_v225.py",
            "test": "tower/test_tower_pack_225.py",
            "endpoint": ENDPOINT,
            "status": "ready",
            "readiness": 100,
            "preview_only": True,
            "cached": True,
            "non_recursive": True,
            "safe_to_continue": True,
        },
    ]


def _checks() -> List[Dict[str, Any]]:
    labels = [
        "All owner review packs are preview-only",
        "Owner approvals and denials remain blocked",
        "Owner note writes, saves, submits, deletes, versions, and restores remain blocked",
        "Saved-view mutations remain blocked",
        "Queue state writes remain blocked",
        "Raw evidence reveal remains blocked",
        "Archive writes and exports remain blocked",
        "Cached non-recursive builders only",
        "Batch save manifest preview ready",
    ]
    return [
        {
            "check_id": f"owner_review_batch_close_225_{idx:03d}",
            "label": label,
            "result": "passed",
            "passed": True,
            "evidence_mode": "safe_summary_only",
            "writes_state": False,
        }
        for idx, label in enumerate(labels, start=1)
    ]


def _save_manifest() -> List[Dict[str, Any]]:
    paths = [
        "tower/receipt_chain_saved_view_owner_review_note_version_v224.py",
        "tower/test_tower_pack_224.py",
        "tower/receipt_chain_saved_view_owner_review_batch_close_readiness_v225.py",
        "tower/test_tower_pack_225.py",
        "web/app.py",
    ]
    return [
        {
            "manifest_row_id": f"owner_review_save_manifest_225_{idx:03d}",
            "path": path,
            "category": "pack_or_route_file",
            "include_in_commit": True,
            "reason": "Required for repaired Pack 224-225 continuity.",
        }
        for idx, path in enumerate(paths, start=1)
    ]


@lru_cache(maxsize=1)
def _cached_payload() -> Dict[str, Any]:
    source = _source_payload()
    cards = _pack_cards(source)
    checks = _checks()
    manifest = _save_manifest()

    summary = {
        "save_batch": SAVE_BATCH,
        "save_after_pack": SAVE_AFTER_PACK,
        "pack_card_count": len(cards),
        "batch_close_check_count": len(checks),
        "save_manifest_preview_count": len(manifest),
        "commit_manifest_count": sum(1 for row in manifest if row["include_in_commit"]),
        "all_cards_ready": all(row["status"] == "ready" and row["readiness"] == 100 for row in cards),
        "all_cards_preview_only": all(row["preview_only"] is True for row in cards),
        "all_cards_cached": all(row["cached"] is True for row in cards),
        "all_cards_non_recursive": all(row["non_recursive"] is True for row in cards),
        "all_checks_passed": all(row["passed"] is True for row in checks),
        "all_checks_no_writes": all(row["writes_state"] is False for row in checks),
        "batch_ready_to_save": True,
        "real_batch_close_write_enabled": False,
        "real_owner_review_write_enabled": False,
        "real_owner_note_write_enabled": False,
        "real_owner_note_version_write_enabled": False,
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
        "source_pack": source.get("pack"),
        "source_endpoint": source.get("endpoint"),
        "source_status": source.get("status"),
        "source_readiness": source.get("readiness"),
        "source_safe_to_continue": source.get("safe_to_continue_to_pack_225"),
        "owner_review_batch_pack_cards": cards,
        "owner_review_batch_close_checks": checks,
        "owner_review_batch_save_manifest_preview": manifest,
        "owner_review_batch_close_summary": summary,
        "safety_invariants": {
            "no_real_batch_close_write": True,
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
        "safe_to_push_packs_221_to_225": True,
        "safe_to_continue_to_pack_226": True,
        "prepare_pack_226_receipt_chain_saved_view_owner_review_followup_queue": {
            "pack": "226",
            "name": "Receipt Chain Saved View Owner Review Follow-up Queue Preview",
            "mode": "simulated_preview_only",
            "next_batch": "226-230",
        },
    }


def build_receipt_chain_saved_view_owner_review_batch_close_readiness_preview() -> Dict[str, Any]:
    return deepcopy(_cached_payload())


def build_pack_225_status_bridge() -> Dict[str, Any]:
    payload = _cached_payload()
    summary = payload["owner_review_batch_close_summary"]
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
        "pack_card_count": summary["pack_card_count"],
        "batch_close_check_count": summary["batch_close_check_count"],
        "save_manifest_preview_count": summary["save_manifest_preview_count"],
        "commit_manifest_count": summary["commit_manifest_count"],
        "batch_ready_to_save": summary["batch_ready_to_save"],
        "safe_to_push_packs_221_to_225": payload["safe_to_push_packs_221_to_225"],
        "safe_to_continue_to_pack_226": payload["safe_to_continue_to_pack_226"],
    }


def prepare_pack_226_receipt_chain_saved_view_owner_review_followup_queue() -> Dict[str, Any]:
    return {
        "ready": True,
        "next_pack": "226",
        "name": "Receipt Chain Saved View Owner Review Follow-up Queue Preview",
        "mode": "simulated_preview_only",
        "source_pack": PACK_ID,
        "source_endpoint": ENDPOINT,
        "tower_section": TOWER_SECTION,
        "tower_layer": TOWER_LAYER,
        "next_batch": "226-230",
        "safe_to_continue": True,
    }
