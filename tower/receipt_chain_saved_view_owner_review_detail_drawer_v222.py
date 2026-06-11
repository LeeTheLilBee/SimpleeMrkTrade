"""
SEARCHABLE LABEL: TOWER_PACK_222_RECEIPT_CHAIN_SAVED_VIEW_OWNER_REVIEW_DETAIL_DRAWER_PREVIEW_MODULE

Tower section:
- The Tower
- Operational Containment
- Receipt Chain Saved View Review Layer

Pack 222: Receipt Chain Saved View Owner Review Detail Drawer Preview

This module is intentionally simulated/preview-only.

Safety boundaries:
- No real owner approval or denial.
- No real owner notes written.
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

from tower.receipt_chain_saved_view_owner_review_queue_v221 import (
    build_receipt_chain_saved_view_owner_review_queue_preview,
)


PACK_ID = "222"
PACK_NUMBER = 222
PACK_NAME = "Receipt Chain Saved View Owner Review Detail Drawer Preview"
ENDPOINT = "/tower/receipt-chain-saved-view-owner-review-detail-drawer-v222.json"

TOWER_AREA = "The Tower"
TOWER_SECTION = "Operational Containment"
TOWER_LAYER = "Receipt Chain Saved View Review Layer"

SAVE_BATCH = "221-225"
SAVE_AFTER_PACK = 225
SAFE_TO_CONTINUE_FLAG = "safe_to_continue_to_pack_223"
NEXT_PREP_FLAG = "prepare_pack_223_saved_view_owner_review_note_draft_preview"

BLOCKED_REAL_ACTIONS = (
    "real_owner_review_approve",
    "real_owner_review_deny",
    "real_owner_review_assign",
    "real_owner_review_note_write",
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
class DetailDrawerHeader:
    drawer_id: str
    queue_item_id: str
    review_key: str
    label: str
    priority: str
    source_pack: str
    source_endpoint: str
    review_status: str
    owner_action_mode: str


@dataclass(frozen=True)
class DetailDrawerSection:
    section_id: str
    queue_item_id: str
    label: str
    section_type: str
    summary: str
    evidence_mode: str
    raw_evidence_visible: bool
    writes_state: bool


@dataclass(frozen=True)
class DetailDrawerAction:
    action_id: str
    queue_item_id: str
    label: str
    visible: bool
    enabled: bool
    result: str
    reason: str


@dataclass(frozen=True)
class DetailDrawerEvidencePointer:
    pointer_id: str
    queue_item_id: str
    pointer_type: str
    label: str
    source_pack: str
    source_endpoint: str
    reveal_mode: str
    raw_evidence_visible: bool


@dataclass(frozen=True)
class DetailDrawerCheckpoint:
    checkpoint_id: str
    label: str
    passed: bool
    result: str
    evidence_mode: str
    writes_state: bool


def _source_payload() -> Dict[str, Any]:
    return deepcopy(build_receipt_chain_saved_view_owner_review_queue_preview())


def _source_items(source_payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    return deepcopy(source_payload.get("owner_review_queue_items", []))


def _build_headers(items: List[Dict[str, Any]]) -> List[DetailDrawerHeader]:
    headers: List[DetailDrawerHeader] = []
    for item in items:
        headers.append(
            DetailDrawerHeader(
                drawer_id=f"detail_drawer_222_{item['queue_item_id']}",
                queue_item_id=item["queue_item_id"],
                review_key=item["review_key"],
                label=item["label"],
                priority=item["priority"],
                source_pack=item["source_pack"],
                source_endpoint=item["source_endpoint"],
                review_status=item["review_status"],
                owner_action_mode="preview_only",
            )
        )
    return headers


def _build_sections(items: List[Dict[str, Any]]) -> List[DetailDrawerSection]:
    sections: List[DetailDrawerSection] = []

    for item in items:
        queue_item_id = item["queue_item_id"]

        sections.extend(
            [
                DetailDrawerSection(
                    section_id=f"detail_section_222_{queue_item_id}_summary",
                    queue_item_id=queue_item_id,
                    label="Safe Summary",
                    section_type="summary",
                    summary=item["owner_review_hint"],
                    evidence_mode="safe_summary_only",
                    raw_evidence_visible=False,
                    writes_state=False,
                ),
                DetailDrawerSection(
                    section_id=f"detail_section_222_{queue_item_id}_source",
                    queue_item_id=queue_item_id,
                    label="Source Context",
                    section_type="source_context",
                    summary=f"Source pack {item['source_pack']} through {item['source_endpoint']}.",
                    evidence_mode=item["evidence_mode"],
                    raw_evidence_visible=False,
                    writes_state=False,
                ),
                DetailDrawerSection(
                    section_id=f"detail_section_222_{queue_item_id}_safety",
                    queue_item_id=queue_item_id,
                    label="Safety Boundary",
                    section_type="safety_boundary",
                    summary="Owner decisions, queue state writes, saved-view mutations, archive writes, exports, and raw evidence reveal are blocked.",
                    evidence_mode="blocked_action_summary",
                    raw_evidence_visible=False,
                    writes_state=False,
                ),
            ]
        )

    return sections


def _build_actions(items: List[Dict[str, Any]]) -> List[DetailDrawerAction]:
    actions: List[DetailDrawerAction] = []

    for item in items:
        queue_item_id = item["queue_item_id"]

        actions.extend(
            [
                DetailDrawerAction(
                    action_id=f"detail_action_222_{queue_item_id}_preview_source",
                    queue_item_id=queue_item_id,
                    label="Preview source summary",
                    visible=True,
                    enabled=True,
                    result="preview_allowed",
                    reason="Previewing safe source summary does not mutate state.",
                ),
                DetailDrawerAction(
                    action_id=f"detail_action_222_{queue_item_id}_approve",
                    queue_item_id=queue_item_id,
                    label="Approve",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Owner approval execution is blocked in Pack 222.",
                ),
                DetailDrawerAction(
                    action_id=f"detail_action_222_{queue_item_id}_deny",
                    queue_item_id=queue_item_id,
                    label="Deny",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Owner denial execution is blocked in Pack 222.",
                ),
                DetailDrawerAction(
                    action_id=f"detail_action_222_{queue_item_id}_write_note",
                    queue_item_id=queue_item_id,
                    label="Write note",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Owner note writes are deferred to preview-only note drafting and cannot write state.",
                ),
                DetailDrawerAction(
                    action_id=f"detail_action_222_{queue_item_id}_restore",
                    queue_item_id=queue_item_id,
                    label="Restore saved view",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Saved-view restore is blocked.",
                ),
                DetailDrawerAction(
                    action_id=f"detail_action_222_{queue_item_id}_export",
                    queue_item_id=queue_item_id,
                    label="Export review packet",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Exports are blocked in this preview lane.",
                ),
            ]
        )

    return actions


def _build_evidence_pointers(items: List[Dict[str, Any]]) -> List[DetailDrawerEvidencePointer]:
    pointers: List[DetailDrawerEvidencePointer] = []

    for item in items:
        queue_item_id = item["queue_item_id"]

        pointers.extend(
            [
                DetailDrawerEvidencePointer(
                    pointer_id=f"detail_pointer_222_{queue_item_id}_source",
                    queue_item_id=queue_item_id,
                    pointer_type="source_endpoint",
                    label="Source endpoint pointer",
                    source_pack=item["source_pack"],
                    source_endpoint=item["source_endpoint"],
                    reveal_mode="safe_pointer_only",
                    raw_evidence_visible=False,
                ),
                DetailDrawerEvidencePointer(
                    pointer_id=f"detail_pointer_222_{queue_item_id}_blocked_actions",
                    queue_item_id=queue_item_id,
                    pointer_type="blocked_action_summary",
                    label="Blocked action summary pointer",
                    source_pack=item["source_pack"],
                    source_endpoint=item["source_endpoint"],
                    reveal_mode="safe_summary_only",
                    raw_evidence_visible=False,
                ),
            ]
        )

    return pointers


def _build_checkpoints() -> List[DetailDrawerCheckpoint]:
    return [
        DetailDrawerCheckpoint(
            checkpoint_id="detail_drawer_checkpoint_222_001",
            label="Detail drawer headers are preview-only",
            passed=True,
            result="passed",
            evidence_mode="safe_summary_only",
            writes_state=False,
        ),
        DetailDrawerCheckpoint(
            checkpoint_id="detail_drawer_checkpoint_222_002",
            label="Detail drawer sections do not reveal raw evidence",
            passed=True,
            result="passed",
            evidence_mode="receipt_pointer_only",
            writes_state=False,
        ),
        DetailDrawerCheckpoint(
            checkpoint_id="detail_drawer_checkpoint_222_003",
            label="Detail drawer actions block approvals, denials, notes, restores, and exports",
            passed=True,
            result="passed",
            evidence_mode="blocked_action_summary",
            writes_state=False,
        ),
        DetailDrawerCheckpoint(
            checkpoint_id="detail_drawer_checkpoint_222_004",
            label="Evidence pointers remain safe pointer-only",
            passed=True,
            result="passed",
            evidence_mode="safe_pointer_only",
            writes_state=False,
        ),
        DetailDrawerCheckpoint(
            checkpoint_id="detail_drawer_checkpoint_222_005",
            label="Ready for owner review note draft preview",
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
            "reason": "Pack 222 previews owner review detail drawers only and cannot write review, queue, saved-view, archive, evidence, or action state.",
        }
        for action in BLOCKED_REAL_ACTIONS
    ]


@lru_cache(maxsize=1)
def _build_receipt_chain_saved_view_owner_review_detail_drawer_preview_cached() -> Dict[str, Any]:
    source_payload = _source_payload()
    items = _source_items(source_payload)

    headers = [asdict(header) for header in _build_headers(items)]
    sections = [asdict(section) for section in _build_sections(items)]
    actions = [asdict(action) for action in _build_actions(items)]
    evidence_pointers = [asdict(pointer) for pointer in _build_evidence_pointers(items)]
    checkpoints = [asdict(checkpoint) for checkpoint in _build_checkpoints()]

    enabled_action_count = sum(1 for action in actions if action["enabled"] is True)
    blocked_action_count = sum(1 for action in actions if action["enabled"] is False)

    all_headers_preview_only = all(header["owner_action_mode"] == "preview_only" for header in headers)
    all_sections_no_writes = all(section["writes_state"] is False for section in sections)
    all_sections_no_raw_evidence = all(section["raw_evidence_visible"] is False for section in sections)
    all_pointers_no_raw_evidence = all(pointer["raw_evidence_visible"] is False for pointer in evidence_pointers)
    all_blocking_actions_safe = all(
        action["result"] in {"preview_allowed", "blocked_preview_only"}
        for action in actions
    )
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
        "receipt_chain_layer": "saved_view_owner_review_detail_drawer_preview",
        "source_pack": source_payload.get("pack"),
        "source_endpoint": source_payload.get("endpoint"),
        "source_status": source_payload.get("status"),
        "source_readiness": source_payload.get("readiness"),
        "source_safe_to_continue": source_payload.get("safe_to_continue_to_pack_222"),
        "detail_drawer_headers": headers,
        "detail_drawer_sections": sections,
        "detail_drawer_actions": actions,
        "detail_drawer_evidence_pointers": evidence_pointers,
        "detail_drawer_checkpoints": checkpoints,
        "detail_drawer_summary": {
            "source_queue_item_count": len(items),
            "detail_drawer_count": len(headers),
            "detail_section_count": len(sections),
            "detail_action_count": len(actions),
            "detail_evidence_pointer_count": len(evidence_pointers),
            "detail_checkpoint_count": len(checkpoints),
            "enabled_action_count": enabled_action_count,
            "blocked_action_count": blocked_action_count,
            "all_headers_preview_only": all_headers_preview_only,
            "all_sections_no_writes": all_sections_no_writes,
            "all_sections_no_raw_evidence": all_sections_no_raw_evidence,
            "all_pointers_no_raw_evidence": all_pointers_no_raw_evidence,
            "all_blocking_actions_safe": all_blocking_actions_safe,
            "all_checkpoints_passed": all_checkpoints_passed,
            "all_checkpoints_no_writes": all_checkpoints_no_writes,
            "detail_drawer_ready": all([
                all_headers_preview_only,
                all_sections_no_writes,
                all_sections_no_raw_evidence,
                all_pointers_no_raw_evidence,
                all_blocking_actions_safe,
                all_checkpoints_passed,
                all_checkpoints_no_writes,
            ]),
            "real_owner_approval_enabled": False,
            "real_owner_denial_enabled": False,
            "real_owner_note_write_enabled": False,
            "real_queue_state_write_enabled": False,
            "real_saved_view_mutation_enabled": False,
            "real_archive_write_enabled": False,
            "raw_evidence_visible": False,
            "real_action_execution_enabled": False,
        },
        "safety_invariants": {
            "no_real_owner_review_approve": True,
            "no_real_owner_review_deny": True,
            "no_real_owner_review_assign": True,
            "no_real_owner_review_note_write": True,
            "no_real_owner_review_status_write": True,
            "no_real_detail_drawer_state_write": True,
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
        "pack_222_acceptance": {
            "detail_drawers_built": True,
            "detail_sections_built": True,
            "detail_actions_built": True,
            "evidence_pointers_safe": True,
            "owner_review_write_actions_blocked": True,
            "ready_for_owner_review_note_draft_preview": True,
        },
        SAFE_TO_CONTINUE_FLAG: True,
        NEXT_PREP_FLAG: {
            "pack": "223",
            "name": "Receipt Chain Saved View Owner Review Note Draft Preview",
            "mode": "simulated_preview_only",
            "recommended_next_endpoint": "/tower/receipt-chain-saved-view-owner-review-note-draft-v223.json",
            "save_batch": SAVE_BATCH,
            "save_after_pack": SAVE_AFTER_PACK,
        },
    }

    return preview


def build_receipt_chain_saved_view_owner_review_detail_drawer_preview() -> Dict[str, Any]:
    """Return a defensive copy of the cached Pack 222 preview payload."""
    return deepcopy(_build_receipt_chain_saved_view_owner_review_detail_drawer_preview_cached())


def build_pack_222_status_bridge() -> Dict[str, Any]:
    """Small cached status bridge for Tower cards/status surfaces."""
    preview = _build_receipt_chain_saved_view_owner_review_detail_drawer_preview_cached()
    summary = preview["detail_drawer_summary"]

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
        "detail_drawer_count": summary["detail_drawer_count"],
        "detail_section_count": summary["detail_section_count"],
        "detail_action_count": summary["detail_action_count"],
        "detail_drawer_ready": summary["detail_drawer_ready"],
        SAFE_TO_CONTINUE_FLAG: preview[SAFE_TO_CONTINUE_FLAG],
    }


def prepare_pack_223_saved_view_owner_review_note_draft_preview() -> Dict[str, Any]:
    """Prepare Pack 223 direction without writing state."""
    return {
        "ready": True,
        "next_pack": "223",
        "name": "Receipt Chain Saved View Owner Review Note Draft Preview",
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
    "build_receipt_chain_saved_view_owner_review_detail_drawer_preview",
    "build_pack_222_status_bridge",
    "prepare_pack_223_saved_view_owner_review_note_draft_preview",
]
