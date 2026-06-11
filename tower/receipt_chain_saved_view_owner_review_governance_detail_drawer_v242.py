"""
SEARCHABLE LABEL: TOWER_PACK_242_RECEIPT_CHAIN_SAVED_VIEW_OWNER_REVIEW_GOVERNANCE_DETAIL_DRAWER_PREVIEW_MODULE

Tower section:
- The Tower
- Operational Containment
- Receipt Chain Saved View Review Layer
- Governance Index Preview layer

Pack 242: Receipt Chain Saved View Owner Review Governance Detail Drawer Preview

This module is intentionally simulated/preview-only.

Purpose:
- Expand Pack 241 governance index controls into safe detail drawers.
- Preserve governance boundaries above the saved-view owner review and cross-batch layers.
- Prepare Pack 243 governance note draft preview.

Safety boundaries:
- No real governance detail state writes.
- No real governance writes.
- No real policy changes.
- No real approval/denial execution.
- No real cross-batch index/link/status/checkpoint/note/version writes.
- No real continuity, follow-up, or owner review writes.
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

from tower.receipt_chain_saved_view_owner_review_governance_index_v241 import (
    build_receipt_chain_saved_view_owner_review_governance_index_preview,
)


PACK_ID = "242"
PACK_NUMBER = 242
PACK_NAME = "Receipt Chain Saved View Owner Review Governance Detail Drawer Preview"
ENDPOINT = "/tower/receipt-chain-saved-view-owner-review-governance-detail-drawer-v242.json"

TOWER_AREA = "The Tower"
TOWER_SECTION = "Operational Containment"
TOWER_LAYER = "Receipt Chain Saved View Review Layer"
TOWER_SUBLAYER = "Governance Index Preview layer"

SAVE_BATCH = "241-245"
SAVE_AFTER_PACK = 245
SAFE_TO_CONTINUE_FLAG = "safe_to_continue_to_pack_243"
NEXT_PREP_FLAG = "prepare_pack_243_receipt_chain_saved_view_owner_review_governance_note_draft"

BLOCKED_REAL_ACTIONS = (
    "real_governance_detail_state_write",
    "real_governance_index_write",
    "real_governance_control_write",
    "real_governance_status_write",
    "real_governance_checkpoint_write",
    "real_policy_change_write",
    "real_policy_enable",
    "real_policy_disable",
    "real_policy_override",
    "real_approval_execute",
    "real_denial_execute",
    "real_owner_review_execute",
    "real_batch_close_write",
    "real_cross_batch_note_version_write",
    "real_cross_batch_note_version_restore",
    "real_cross_batch_note_version_apply",
    "real_cross_batch_note_write",
    "real_cross_batch_index_write",
    "real_cross_batch_link_write",
    "real_cross_batch_status_write",
    "real_cross_batch_checkpoint_write",
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
class GovernanceDetailHeader:
    drawer_id: str
    governance_id: str
    governance_key: str
    label: str
    category: str
    control_scope: str
    source_layer: str
    status: str
    readiness: int
    detail_mode: str
    writes_state: bool
    raw_evidence_visible: bool


@dataclass(frozen=True)
class GovernanceDetailSection:
    section_id: str
    drawer_id: str
    governance_key: str
    label: str
    section_type: str
    summary: str
    evidence_mode: str
    writes_state: bool
    raw_evidence_visible: bool


@dataclass(frozen=True)
class GovernanceDetailPolicyPointer:
    pointer_id: str
    drawer_id: str
    governance_key: str
    policy_boundary: str
    label: str
    pointer_mode: str
    mutation_allowed: bool
    writes_state: bool
    raw_evidence_visible: bool


@dataclass(frozen=True)
class GovernanceDetailAction:
    action_id: str
    drawer_id: str
    label: str
    visible: bool
    enabled: bool
    result: str
    reason: str


@dataclass(frozen=True)
class GovernanceDetailCheckpoint:
    checkpoint_id: str
    label: str
    passed: bool
    result: str
    evidence_mode: str
    writes_state: bool


def _source_payload() -> Dict[str, Any]:
    return deepcopy(build_receipt_chain_saved_view_owner_review_governance_index_preview())


def _source_cards(source_payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    return deepcopy(source_payload.get("governance_index_cards", []))


def _build_headers(cards: List[Dict[str, Any]]) -> List[GovernanceDetailHeader]:
    headers: List[GovernanceDetailHeader] = []

    for card in cards:
        headers.append(
            GovernanceDetailHeader(
                drawer_id=f"governance_detail_drawer_242_{card['governance_key']}",
                governance_id=card["governance_id"],
                governance_key=card["governance_key"],
                label=f"Governance detail drawer for {card['label']}",
                category=card["category"],
                control_scope=card["control_scope"],
                source_layer=card["source_layer"],
                status=card["status"],
                readiness=card["readiness"],
                detail_mode="preview_only",
                writes_state=False,
                raw_evidence_visible=False,
            )
        )

    return headers


def _build_sections(headers: List[GovernanceDetailHeader]) -> List[GovernanceDetailSection]:
    sections: List[GovernanceDetailSection] = []

    for header in headers:
        sections.extend(
            [
                GovernanceDetailSection(
                    section_id=f"{header.drawer_id}_section_summary",
                    drawer_id=header.drawer_id,
                    governance_key=header.governance_key,
                    label="Governance Summary",
                    section_type="governance_summary",
                    summary=f"{header.label} is ready at {header.readiness} readiness in category {header.category}.",
                    evidence_mode="safe_summary_only",
                    writes_state=False,
                    raw_evidence_visible=False,
                ),
                GovernanceDetailSection(
                    section_id=f"{header.drawer_id}_section_scope",
                    drawer_id=header.drawer_id,
                    governance_key=header.governance_key,
                    label="Control Scope",
                    section_type="control_scope",
                    summary=f"Control scope preview: {header.control_scope}. No governance state is written.",
                    evidence_mode="safe_summary_only",
                    writes_state=False,
                    raw_evidence_visible=False,
                ),
                GovernanceDetailSection(
                    section_id=f"{header.drawer_id}_section_policy_boundary",
                    drawer_id=header.drawer_id,
                    governance_key=header.governance_key,
                    label="Policy Boundary",
                    section_type="policy_boundary",
                    summary="Policy enables, disables, overrides, and mutations are blocked in this preview layer.",
                    evidence_mode="blocked_action_summary",
                    writes_state=False,
                    raw_evidence_visible=False,
                ),
                GovernanceDetailSection(
                    section_id=f"{header.drawer_id}_section_action_boundary",
                    drawer_id=header.drawer_id,
                    governance_key=header.governance_key,
                    label="Action Boundary",
                    section_type="action_boundary",
                    summary="Approval execution, denial execution, owner review execution, saved-view actions, exports, and raw evidence reveal are blocked.",
                    evidence_mode="blocked_action_summary",
                    writes_state=False,
                    raw_evidence_visible=False,
                ),
                GovernanceDetailSection(
                    section_id=f"{header.drawer_id}_section_next_step",
                    drawer_id=header.drawer_id,
                    governance_key=header.governance_key,
                    label="Next Step Preview",
                    section_type="next_step_preview",
                    summary="Detail drawer prepares Pack 243 governance note draft preview without creating notes or writing state.",
                    evidence_mode="safe_summary_only",
                    writes_state=False,
                    raw_evidence_visible=False,
                ),
            ]
        )

    return sections


def _build_policy_pointers(headers: List[GovernanceDetailHeader]) -> List[GovernanceDetailPolicyPointer]:
    pointers: List[GovernanceDetailPolicyPointer] = []

    for header in headers:
        pointers.extend(
            [
                GovernanceDetailPolicyPointer(
                    pointer_id=f"{header.drawer_id}_pointer_policy_mutation",
                    drawer_id=header.drawer_id,
                    governance_key=header.governance_key,
                    policy_boundary="policy_mutation_block",
                    label="Policy mutation blocked",
                    pointer_mode="safe_pointer_only",
                    mutation_allowed=False,
                    writes_state=False,
                    raw_evidence_visible=False,
                ),
                GovernanceDetailPolicyPointer(
                    pointer_id=f"{header.drawer_id}_pointer_owner_execution",
                    drawer_id=header.drawer_id,
                    governance_key=header.governance_key,
                    policy_boundary="owner_execution_block",
                    label="Owner approval/denial execution blocked",
                    pointer_mode="safe_pointer_only",
                    mutation_allowed=False,
                    writes_state=False,
                    raw_evidence_visible=False,
                ),
                GovernanceDetailPolicyPointer(
                    pointer_id=f"{header.drawer_id}_pointer_raw_evidence",
                    drawer_id=header.drawer_id,
                    governance_key=header.governance_key,
                    policy_boundary="raw_evidence_redaction",
                    label="Raw evidence hidden",
                    pointer_mode="redacted_pointer_only",
                    mutation_allowed=False,
                    writes_state=False,
                    raw_evidence_visible=False,
                ),
            ]
        )

    return pointers


def _build_actions(headers: List[GovernanceDetailHeader]) -> List[GovernanceDetailAction]:
    actions: List[GovernanceDetailAction] = []

    for header in headers:
        actions.extend(
            [
                GovernanceDetailAction(
                    action_id=f"{header.drawer_id}_action_preview",
                    drawer_id=header.drawer_id,
                    label="Preview governance detail",
                    visible=True,
                    enabled=True,
                    result="preview_allowed",
                    reason="Previewing a governance detail drawer does not write state.",
                ),
                GovernanceDetailAction(
                    action_id=f"{header.drawer_id}_action_write_detail",
                    drawer_id=header.drawer_id,
                    label="Write governance detail",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Governance detail writes are blocked.",
                ),
                GovernanceDetailAction(
                    action_id=f"{header.drawer_id}_action_change_policy",
                    drawer_id=header.drawer_id,
                    label="Change policy",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Policy changes are blocked.",
                ),
                GovernanceDetailAction(
                    action_id=f"{header.drawer_id}_action_execute_approval",
                    drawer_id=header.drawer_id,
                    label="Execute approval/denial",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Approval and denial execution are blocked.",
                ),
                GovernanceDetailAction(
                    action_id=f"{header.drawer_id}_action_apply_saved_view",
                    drawer_id=header.drawer_id,
                    label="Apply saved view",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Saved-view apply actions are blocked.",
                ),
                GovernanceDetailAction(
                    action_id=f"{header.drawer_id}_action_export_detail",
                    drawer_id=header.drawer_id,
                    label="Export governance detail",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Governance detail exports are blocked in preview mode.",
                ),
            ]
        )

    return actions


def _build_checkpoints() -> List[GovernanceDetailCheckpoint]:
    return [
        GovernanceDetailCheckpoint(
            checkpoint_id="governance_detail_checkpoint_242_001",
            label="Governance detail headers are preview-only",
            passed=True,
            result="passed",
            evidence_mode="safe_summary_only",
            writes_state=False,
        ),
        GovernanceDetailCheckpoint(
            checkpoint_id="governance_detail_checkpoint_242_002",
            label="Governance detail sections do not write state or reveal raw evidence",
            passed=True,
            result="passed",
            evidence_mode="redacted_pointer_only",
            writes_state=False,
        ),
        GovernanceDetailCheckpoint(
            checkpoint_id="governance_detail_checkpoint_242_003",
            label="Policy pointers are safe pointer-only and non-mutating",
            passed=True,
            result="passed",
            evidence_mode="safe_pointer_only",
            writes_state=False,
        ),
        GovernanceDetailCheckpoint(
            checkpoint_id="governance_detail_checkpoint_242_004",
            label="Governance writes, policy changes, approvals, denials, saved-view actions, and exports remain blocked",
            passed=True,
            result="passed",
            evidence_mode="blocked_action_summary",
            writes_state=False,
        ),
        GovernanceDetailCheckpoint(
            checkpoint_id="governance_detail_checkpoint_242_005",
            label="Ready for Pack 243 governance note draft preview",
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
            "reason": "Pack 242 previews governance detail drawers only and cannot mutate governance, policy, approvals, review, cross-batch, saved-view, archive, evidence, or action state.",
        }
        for action in BLOCKED_REAL_ACTIONS
    ]


@lru_cache(maxsize=1)
def _build_receipt_chain_saved_view_owner_review_governance_detail_drawer_preview_cached() -> Dict[str, Any]:
    source_payload = _source_payload()
    cards = _source_cards(source_payload)

    headers_raw = _build_headers(cards)
    sections_raw = _build_sections(headers_raw)
    pointers_raw = _build_policy_pointers(headers_raw)
    actions_raw = _build_actions(headers_raw)
    checkpoints_raw = _build_checkpoints()

    headers = [asdict(header) for header in headers_raw]
    sections = [asdict(section) for section in sections_raw]
    pointers = [asdict(pointer) for pointer in pointers_raw]
    actions = [asdict(action) for action in actions_raw]
    checkpoints = [asdict(checkpoint) for checkpoint in checkpoints_raw]

    enabled_action_count = sum(1 for action in actions if action["enabled"] is True)
    blocked_action_count = sum(1 for action in actions if action["enabled"] is False)
    redacted_pointer_count = sum(1 for pointer in pointers if pointer["pointer_mode"] == "redacted_pointer_only")

    all_headers_preview_only = all(header["detail_mode"] == "preview_only" for header in headers)
    all_headers_no_writes = all(header["writes_state"] is False for header in headers)
    all_headers_no_raw_evidence = all(header["raw_evidence_visible"] is False for header in headers)
    all_sections_no_writes = all(section["writes_state"] is False for section in sections)
    all_sections_no_raw_evidence = all(section["raw_evidence_visible"] is False for section in sections)
    all_pointers_no_mutation = all(pointer["mutation_allowed"] is False for pointer in pointers)
    all_pointers_no_writes = all(pointer["writes_state"] is False for pointer in pointers)
    all_pointers_no_raw_evidence = all(pointer["raw_evidence_visible"] is False for pointer in pointers)
    all_actions_safe = all(action["result"] in {"preview_allowed", "blocked_preview_only"} for action in actions)
    all_checkpoints_passed = all(checkpoint["passed"] is True for checkpoint in checkpoints)
    all_checkpoints_no_writes = all(checkpoint["writes_state"] is False for checkpoint in checkpoints)

    governance_detail_ready = all([
        all_headers_preview_only,
        all_headers_no_writes,
        all_headers_no_raw_evidence,
        all_sections_no_writes,
        all_sections_no_raw_evidence,
        all_pointers_no_mutation,
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
        "tower_sublayer": TOWER_SUBLAYER,
        "save_batch": SAVE_BATCH,
        "save_after_pack": SAVE_AFTER_PACK,
        "cached": True,
        "non_recursive": True,
        "simulation_only": True,
        "preview_only": True,
        "receipt_chain_layer": "saved_view_owner_review_governance_detail_drawer_preview",
        "source_pack": source_payload.get("pack"),
        "source_endpoint": source_payload.get("endpoint"),
        "source_status": source_payload.get("status"),
        "source_readiness": source_payload.get("readiness"),
        "source_safe_to_continue": source_payload.get("safe_to_continue_to_pack_242"),
        "governance_detail_headers": headers,
        "governance_detail_sections": sections,
        "governance_detail_policy_pointers": pointers,
        "governance_detail_actions": actions,
        "governance_detail_checkpoints": checkpoints,
        "governance_detail_summary": {
            "source_governance_card_count": len(cards),
            "detail_drawer_count": len(headers),
            "detail_section_count": len(sections),
            "policy_pointer_count": len(pointers),
            "detail_action_count": len(actions),
            "detail_checkpoint_count": len(checkpoints),
            "enabled_action_count": enabled_action_count,
            "blocked_action_count": blocked_action_count,
            "redacted_pointer_count": redacted_pointer_count,
            "all_headers_preview_only": all_headers_preview_only,
            "all_headers_no_writes": all_headers_no_writes,
            "all_headers_no_raw_evidence": all_headers_no_raw_evidence,
            "all_sections_no_writes": all_sections_no_writes,
            "all_sections_no_raw_evidence": all_sections_no_raw_evidence,
            "all_pointers_no_mutation": all_pointers_no_mutation,
            "all_pointers_no_writes": all_pointers_no_writes,
            "all_pointers_no_raw_evidence": all_pointers_no_raw_evidence,
            "all_actions_safe": all_actions_safe,
            "all_checkpoints_passed": all_checkpoints_passed,
            "all_checkpoints_no_writes": all_checkpoints_no_writes,
            "governance_detail_ready": governance_detail_ready,
            "real_governance_detail_state_write_enabled": False,
            "real_governance_index_write_enabled": False,
            "real_governance_control_write_enabled": False,
            "real_policy_change_enabled": False,
            "real_approval_execution_enabled": False,
            "real_denial_execution_enabled": False,
            "real_review_write_enabled": False,
            "real_saved_view_mutation_enabled": False,
            "real_archive_write_enabled": False,
            "raw_evidence_visible": False,
            "real_action_execution_enabled": False,
        },
        "safety_invariants": {
            "no_real_governance_detail_state_write": True,
            "no_real_governance_index_write": True,
            "no_real_governance_control_write": True,
            "no_real_governance_status_write": True,
            "no_real_governance_checkpoint_write": True,
            "no_real_policy_change_write": True,
            "no_real_policy_enable": True,
            "no_real_policy_disable": True,
            "no_real_policy_override": True,
            "no_real_approval_execute": True,
            "no_real_denial_execute": True,
            "no_real_owner_review_execute": True,
            "no_real_cross_batch_write": True,
            "no_real_continuity_write": True,
            "no_real_followup_write": True,
            "no_real_owner_review_write": True,
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
        "pack_242_acceptance": {
            "governance_detail_headers_built": True,
            "governance_detail_sections_built": True,
            "governance_policy_pointers_built": True,
            "governance_policy_approval_execution_blocked": True,
            "ready_for_governance_note_draft": True,
        },
        SAFE_TO_CONTINUE_FLAG: True,
        NEXT_PREP_FLAG: {
            "pack": "243",
            "name": "Receipt Chain Saved View Owner Review Governance Note Draft Preview",
            "mode": "simulated_preview_only",
            "recommended_next_endpoint": "/tower/receipt-chain-saved-view-owner-review-governance-note-draft-v243.json",
            "save_batch": SAVE_BATCH,
            "save_after_pack": SAVE_AFTER_PACK,
        },
    }

    return preview


def build_receipt_chain_saved_view_owner_review_governance_detail_drawer_preview() -> Dict[str, Any]:
    """Return a defensive copy of the cached Pack 242 preview payload."""
    return deepcopy(_build_receipt_chain_saved_view_owner_review_governance_detail_drawer_preview_cached())


def build_pack_242_status_bridge() -> Dict[str, Any]:
    """Small cached status bridge for Tower cards/status surfaces."""
    preview = _build_receipt_chain_saved_view_owner_review_governance_detail_drawer_preview_cached()
    summary = preview["governance_detail_summary"]

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
        "detail_drawer_count": summary["detail_drawer_count"],
        "detail_section_count": summary["detail_section_count"],
        "policy_pointer_count": summary["policy_pointer_count"],
        "detail_action_count": summary["detail_action_count"],
        "governance_detail_ready": summary["governance_detail_ready"],
        SAFE_TO_CONTINUE_FLAG: preview[SAFE_TO_CONTINUE_FLAG],
    }


def prepare_pack_243_receipt_chain_saved_view_owner_review_governance_note_draft() -> Dict[str, Any]:
    """Prepare Pack 243 direction without writing state."""
    return {
        "ready": True,
        "next_pack": "243",
        "name": "Receipt Chain Saved View Owner Review Governance Note Draft Preview",
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
    "SAFE_TO_CONTINUE_FLAG",
    "NEXT_PREP_FLAG",
    "BLOCKED_REAL_ACTIONS",
    "build_receipt_chain_saved_view_owner_review_governance_detail_drawer_preview",
    "build_pack_242_status_bridge",
    "prepare_pack_243_receipt_chain_saved_view_owner_review_governance_note_draft",
]
