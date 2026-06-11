"""
SEARCHABLE LABEL: TOWER_PACK_237_RECEIPT_CHAIN_SAVED_VIEW_OWNER_REVIEW_CROSS_BATCH_DETAIL_DRAWER_PREVIEW_MODULE

Tower section:
- The Tower
- Operational Containment
- Receipt Chain Saved View Review Layer

Pack 237: Receipt Chain Saved View Owner Review Cross-Batch Detail Drawer Preview

This module is intentionally simulated/preview-only.

Purpose:
- Expand Pack 236 cross-batch index cards into safe detail drawers.
- Preserve visibility across closed batches 221-225, 226-230, and 231-235.
- Prepare Pack 238 cross-batch note draft preview.

Safety boundaries:
- No real drawer state writes.
- No real cross-batch index or link writes.
- No real batch close writes.
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

from tower.receipt_chain_saved_view_owner_review_cross_batch_index_v236 import (
    build_receipt_chain_saved_view_owner_review_cross_batch_index_preview,
)


PACK_ID = "237"
PACK_NUMBER = 237
PACK_NAME = "Receipt Chain Saved View Owner Review Cross-Batch Detail Drawer Preview"
ENDPOINT = "/tower/receipt-chain-saved-view-owner-review-cross-batch-detail-drawer-v237.json"

TOWER_AREA = "The Tower"
TOWER_SECTION = "Operational Containment"
TOWER_LAYER = "Receipt Chain Saved View Review Layer"

SAVE_BATCH = "236-240"
SAVE_AFTER_PACK = 240
SAFE_TO_CONTINUE_FLAG = "safe_to_continue_to_pack_238"
NEXT_PREP_FLAG = "prepare_pack_238_receipt_chain_saved_view_owner_review_cross_batch_note_draft"

BLOCKED_REAL_ACTIONS = (
    "real_cross_batch_detail_state_write",
    "real_cross_batch_index_write",
    "real_cross_batch_link_write",
    "real_cross_batch_status_write",
    "real_cross_batch_checkpoint_write",
    "real_batch_close_write",
    "real_continuity_note_version_write",
    "real_continuity_note_version_restore",
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
class CrossBatchDetailHeader:
    drawer_id: str
    batch_id: str
    batch_range: str
    batch_label: str
    batch_role: str
    close_pack: str
    close_endpoint: str
    status: str
    readiness: int
    detail_mode: str
    raw_evidence_visible: bool


@dataclass(frozen=True)
class CrossBatchDetailSection:
    section_id: str
    drawer_id: str
    batch_range: str
    label: str
    section_type: str
    summary: str
    evidence_mode: str
    writes_state: bool
    raw_evidence_visible: bool


@dataclass(frozen=True)
class CrossBatchDetailLinkPointer:
    pointer_id: str
    drawer_id: str
    link_id: str
    from_batch: str
    to_batch: str
    label: str
    link_type: str
    reveal_mode: str
    writes_state: bool
    raw_evidence_visible: bool


@dataclass(frozen=True)
class CrossBatchDetailAction:
    action_id: str
    drawer_id: str
    label: str
    visible: bool
    enabled: bool
    result: str
    reason: str


@dataclass(frozen=True)
class CrossBatchDetailCheckpoint:
    checkpoint_id: str
    label: str
    passed: bool
    result: str
    evidence_mode: str
    writes_state: bool


def _source_payload() -> Dict[str, Any]:
    return deepcopy(build_receipt_chain_saved_view_owner_review_cross_batch_index_preview())


def _source_cards(source_payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    return deepcopy(source_payload.get("cross_batch_index_cards", []))


def _source_links(source_payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    return deepcopy(source_payload.get("cross_batch_links", []))


def _build_headers(cards: List[Dict[str, Any]]) -> List[CrossBatchDetailHeader]:
    headers: List[CrossBatchDetailHeader] = []

    for card in cards:
        headers.append(
            CrossBatchDetailHeader(
                drawer_id=f"cross_batch_detail_drawer_237_{card['batch_range'].replace('-', '_')}",
                batch_id=card["batch_id"],
                batch_range=card["batch_range"],
                batch_label=card["batch_label"],
                batch_role=card["batch_role"],
                close_pack=card["close_pack"],
                close_endpoint=card["close_endpoint"],
                status=card["status"],
                readiness=card["readiness"],
                detail_mode="preview_only",
                raw_evidence_visible=False,
            )
        )

    return headers


def _build_sections(headers: List[CrossBatchDetailHeader]) -> List[CrossBatchDetailSection]:
    sections: List[CrossBatchDetailSection] = []

    for header in headers:
        sections.extend(
            [
                CrossBatchDetailSection(
                    section_id=f"{header.drawer_id}_section_summary",
                    drawer_id=header.drawer_id,
                    batch_range=header.batch_range,
                    label="Batch Summary",
                    section_type="batch_summary",
                    summary=f"{header.batch_label} ({header.batch_range}) is indexed as {header.batch_role} with close pack {header.close_pack}.",
                    evidence_mode="safe_summary_only",
                    writes_state=False,
                    raw_evidence_visible=False,
                ),
                CrossBatchDetailSection(
                    section_id=f"{header.drawer_id}_section_close_readiness",
                    drawer_id=header.drawer_id,
                    batch_range=header.batch_range,
                    label="Close Readiness",
                    section_type="close_readiness",
                    summary=f"Close readiness is {header.status} at {header.readiness}. This is a safe preview only.",
                    evidence_mode="safe_summary_only",
                    writes_state=False,
                    raw_evidence_visible=False,
                ),
                CrossBatchDetailSection(
                    section_id=f"{header.drawer_id}_section_source_endpoint",
                    drawer_id=header.drawer_id,
                    batch_range=header.batch_range,
                    label="Source Endpoint",
                    section_type="source_endpoint_pointer",
                    summary=f"Source endpoint pointer: {header.close_endpoint}. No raw payload is revealed here.",
                    evidence_mode="safe_pointer_only",
                    writes_state=False,
                    raw_evidence_visible=False,
                ),
                CrossBatchDetailSection(
                    section_id=f"{header.drawer_id}_section_boundary",
                    drawer_id=header.drawer_id,
                    batch_range=header.batch_range,
                    label="Write Boundary",
                    section_type="blocked_action_boundary",
                    summary="Cross-batch index writes, link writes, status writes, batch writes, review writes, saved-view mutations, exports, and raw evidence reveal are blocked.",
                    evidence_mode="blocked_action_summary",
                    writes_state=False,
                    raw_evidence_visible=False,
                ),
                CrossBatchDetailSection(
                    section_id=f"{header.drawer_id}_section_next_step",
                    drawer_id=header.drawer_id,
                    batch_range=header.batch_range,
                    label="Next Step Preview",
                    section_type="next_step_preview",
                    summary="Detail drawer prepares a cross-batch note draft preview for Pack 238 without creating notes or writing state.",
                    evidence_mode="safe_summary_only",
                    writes_state=False,
                    raw_evidence_visible=False,
                ),
            ]
        )

    return sections


def _build_link_pointers(headers: List[CrossBatchDetailHeader], links: List[Dict[str, Any]]) -> List[CrossBatchDetailLinkPointer]:
    pointers: List[CrossBatchDetailLinkPointer] = []
    header_by_batch = {header.batch_range: header for header in headers}

    for link in links:
        linked_batches = {link["from_batch"], link["to_batch"]}
        for batch_range in linked_batches:
            header = header_by_batch.get(batch_range)
            if header is None:
                continue
            pointers.append(
                CrossBatchDetailLinkPointer(
                    pointer_id=f"{header.drawer_id}_pointer_{link['link_id']}",
                    drawer_id=header.drawer_id,
                    link_id=link["link_id"],
                    from_batch=link["from_batch"],
                    to_batch=link["to_batch"],
                    label=link["label"],
                    link_type=link["link_type"],
                    reveal_mode="safe_pointer_only",
                    writes_state=False,
                    raw_evidence_visible=False,
                )
            )

    return pointers


def _build_actions(headers: List[CrossBatchDetailHeader]) -> List[CrossBatchDetailAction]:
    actions: List[CrossBatchDetailAction] = []

    for header in headers:
        actions.extend(
            [
                CrossBatchDetailAction(
                    action_id=f"{header.drawer_id}_action_preview",
                    drawer_id=header.drawer_id,
                    label="Preview batch detail",
                    visible=True,
                    enabled=True,
                    result="preview_allowed",
                    reason="Previewing a cross-batch detail drawer does not write state.",
                ),
                CrossBatchDetailAction(
                    action_id=f"{header.drawer_id}_action_write_index_note",
                    drawer_id=header.drawer_id,
                    label="Write cross-batch note",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Cross-batch note writes are not enabled in Pack 237.",
                ),
                CrossBatchDetailAction(
                    action_id=f"{header.drawer_id}_action_link_batch",
                    drawer_id=header.drawer_id,
                    label="Create/edit batch link",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Cross-batch link writes are blocked.",
                ),
                CrossBatchDetailAction(
                    action_id=f"{header.drawer_id}_action_mark_reviewed",
                    drawer_id=header.drawer_id,
                    label="Mark batch reviewed",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Batch status writes are blocked.",
                ),
                CrossBatchDetailAction(
                    action_id=f"{header.drawer_id}_action_save_filter",
                    drawer_id=header.drawer_id,
                    label="Save drawer filter",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="User preference writes are blocked.",
                ),
                CrossBatchDetailAction(
                    action_id=f"{header.drawer_id}_action_apply_saved_view",
                    drawer_id=header.drawer_id,
                    label="Apply saved view",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Saved-view apply actions are blocked.",
                ),
                CrossBatchDetailAction(
                    action_id=f"{header.drawer_id}_action_export_detail",
                    drawer_id=header.drawer_id,
                    label="Export detail packet",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Exports are blocked in this preview lane.",
                ),
            ]
        )

    return actions


def _build_checkpoints() -> List[CrossBatchDetailCheckpoint]:
    return [
        CrossBatchDetailCheckpoint(
            checkpoint_id="cross_batch_detail_checkpoint_237_001",
            label="Cross-batch detail headers are preview-only",
            passed=True,
            result="passed",
            evidence_mode="safe_summary_only",
            writes_state=False,
        ),
        CrossBatchDetailCheckpoint(
            checkpoint_id="cross_batch_detail_checkpoint_237_002",
            label="Detail sections do not write state or reveal raw evidence",
            passed=True,
            result="passed",
            evidence_mode="redacted_pointer_only",
            writes_state=False,
        ),
        CrossBatchDetailCheckpoint(
            checkpoint_id="cross_batch_detail_checkpoint_237_003",
            label="Link pointers are safe pointer-only",
            passed=True,
            result="passed",
            evidence_mode="safe_pointer_only",
            writes_state=False,
        ),
        CrossBatchDetailCheckpoint(
            checkpoint_id="cross_batch_detail_checkpoint_237_004",
            label="Write, link, status, saved-view, filter, and export actions remain blocked",
            passed=True,
            result="passed",
            evidence_mode="blocked_action_summary",
            writes_state=False,
        ),
        CrossBatchDetailCheckpoint(
            checkpoint_id="cross_batch_detail_checkpoint_237_005",
            label="Ready for Pack 238 cross-batch note draft preview",
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
            "reason": "Pack 237 previews cross-batch detail drawers only and cannot write detail, index, links, review, queue, saved-view, archive, evidence, or action state.",
        }
        for action in BLOCKED_REAL_ACTIONS
    ]


@lru_cache(maxsize=1)
def _build_receipt_chain_saved_view_owner_review_cross_batch_detail_drawer_preview_cached() -> Dict[str, Any]:
    source_payload = _source_payload()
    cards = _source_cards(source_payload)
    links = _source_links(source_payload)

    headers_raw = _build_headers(cards)
    sections_raw = _build_sections(headers_raw)
    pointers_raw = _build_link_pointers(headers_raw, links)
    actions_raw = _build_actions(headers_raw)
    checkpoints_raw = _build_checkpoints()

    headers = [asdict(header) for header in headers_raw]
    sections = [asdict(section) for section in sections_raw]
    pointers = [asdict(pointer) for pointer in pointers_raw]
    actions = [asdict(action) for action in actions_raw]
    checkpoints = [asdict(checkpoint) for checkpoint in checkpoints_raw]

    enabled_action_count = sum(1 for action in actions if action["enabled"] is True)
    blocked_action_count = sum(1 for action in actions if action["enabled"] is False)
    repair_bridge_pointer_count = sum(1 for pointer in pointers if pointer["link_type"] == "repair_bridge_reference")
    safety_boundary_pointer_count = sum(1 for pointer in pointers if pointer["link_type"] == "safety_boundary_reference")

    all_headers_preview_only = all(header["detail_mode"] == "preview_only" for header in headers)
    all_headers_no_raw_evidence = all(header["raw_evidence_visible"] is False for header in headers)
    all_sections_no_writes = all(section["writes_state"] is False for section in sections)
    all_sections_no_raw_evidence = all(section["raw_evidence_visible"] is False for section in sections)
    all_pointers_no_writes = all(pointer["writes_state"] is False for pointer in pointers)
    all_pointers_no_raw_evidence = all(pointer["raw_evidence_visible"] is False for pointer in pointers)
    all_actions_safe = all(action["result"] in {"preview_allowed", "blocked_preview_only"} for action in actions)
    all_checkpoints_passed = all(checkpoint["passed"] is True for checkpoint in checkpoints)
    all_checkpoints_no_writes = all(checkpoint["writes_state"] is False for checkpoint in checkpoints)

    cross_batch_detail_ready = all([
        all_headers_preview_only,
        all_headers_no_raw_evidence,
        all_sections_no_writes,
        all_sections_no_raw_evidence,
        all_pointers_no_writes,
        all_pointers_no_raw_evidence,
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
        "receipt_chain_layer": "saved_view_owner_review_cross_batch_detail_drawer_preview",
        "source_pack": source_payload.get("pack"),
        "source_endpoint": source_payload.get("endpoint"),
        "source_status": source_payload.get("status"),
        "source_readiness": source_payload.get("readiness"),
        "source_safe_to_continue": source_payload.get("safe_to_continue_to_pack_237"),
        "cross_batch_detail_headers": headers,
        "cross_batch_detail_sections": sections,
        "cross_batch_detail_link_pointers": pointers,
        "cross_batch_detail_actions": actions,
        "cross_batch_detail_checkpoints": checkpoints,
        "cross_batch_detail_summary": {
            "source_indexed_batch_count": len(cards),
            "source_link_count": len(links),
            "detail_drawer_count": len(headers),
            "detail_section_count": len(sections),
            "detail_link_pointer_count": len(pointers),
            "detail_action_count": len(actions),
            "detail_checkpoint_count": len(checkpoints),
            "enabled_action_count": enabled_action_count,
            "blocked_action_count": blocked_action_count,
            "repair_bridge_pointer_count": repair_bridge_pointer_count,
            "safety_boundary_pointer_count": safety_boundary_pointer_count,
            "all_headers_preview_only": all_headers_preview_only,
            "all_headers_no_raw_evidence": all_headers_no_raw_evidence,
            "all_sections_no_writes": all_sections_no_writes,
            "all_sections_no_raw_evidence": all_sections_no_raw_evidence,
            "all_pointers_no_writes": all_pointers_no_writes,
            "all_pointers_no_raw_evidence": all_pointers_no_raw_evidence,
            "all_actions_safe": all_actions_safe,
            "all_checkpoints_passed": all_checkpoints_passed,
            "all_checkpoints_no_writes": all_checkpoints_no_writes,
            "cross_batch_detail_ready": cross_batch_detail_ready,
            "real_cross_batch_detail_state_write_enabled": False,
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
            "no_real_queue_reorder_write": True,
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
        "pack_237_acceptance": {
            "cross_batch_detail_headers_built": True,
            "cross_batch_detail_sections_built": True,
            "cross_batch_link_pointers_built": True,
            "repair_bridge_pointer_preserved": True,
            "cross_batch_detail_write_actions_blocked": True,
            "ready_for_cross_batch_note_draft": True,
        },
        SAFE_TO_CONTINUE_FLAG: True,
        NEXT_PREP_FLAG: {
            "pack": "238",
            "name": "Receipt Chain Saved View Owner Review Cross-Batch Note Draft Preview",
            "mode": "simulated_preview_only",
            "recommended_next_endpoint": "/tower/receipt-chain-saved-view-owner-review-cross-batch-note-draft-v238.json",
            "save_batch": SAVE_BATCH,
            "save_after_pack": SAVE_AFTER_PACK,
        },
    }

    return preview


def build_receipt_chain_saved_view_owner_review_cross_batch_detail_drawer_preview() -> Dict[str, Any]:
    """Return a defensive copy of the cached Pack 237 preview payload."""
    return deepcopy(_build_receipt_chain_saved_view_owner_review_cross_batch_detail_drawer_preview_cached())


def build_pack_237_status_bridge() -> Dict[str, Any]:
    """Small cached status bridge for Tower cards/status surfaces."""
    preview = _build_receipt_chain_saved_view_owner_review_cross_batch_detail_drawer_preview_cached()
    summary = preview["cross_batch_detail_summary"]

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
        "detail_link_pointer_count": summary["detail_link_pointer_count"],
        "repair_bridge_pointer_count": summary["repair_bridge_pointer_count"],
        "cross_batch_detail_ready": summary["cross_batch_detail_ready"],
        SAFE_TO_CONTINUE_FLAG: preview[SAFE_TO_CONTINUE_FLAG],
    }


def prepare_pack_238_receipt_chain_saved_view_owner_review_cross_batch_note_draft() -> Dict[str, Any]:
    """Prepare Pack 238 direction without writing state."""
    return {
        "ready": True,
        "next_pack": "238",
        "name": "Receipt Chain Saved View Owner Review Cross-Batch Note Draft Preview",
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
    "build_receipt_chain_saved_view_owner_review_cross_batch_detail_drawer_preview",
    "build_pack_237_status_bridge",
    "prepare_pack_238_receipt_chain_saved_view_owner_review_cross_batch_note_draft",
]
