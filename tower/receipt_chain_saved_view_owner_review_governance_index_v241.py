"""
SEARCHABLE LABEL: TOWER_PACK_241_RECEIPT_CHAIN_SAVED_VIEW_OWNER_REVIEW_GOVERNANCE_INDEX_PREVIEW_MODULE

Tower section:
- The Tower
- Operational Containment
- Receipt Chain Saved View Review Layer
- Governance Index Preview layer

Pack 241: Receipt Chain Saved View Owner Review Governance Index Preview

This module is intentionally simulated/preview-only.

Purpose:
- Start the 241-245 governance preview batch.
- Index governance controls sitting above the saved-view owner review and cross-batch layers.
- Prepare Pack 242 governance detail drawer preview.

Safety boundaries:
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

from tower.receipt_chain_saved_view_owner_review_cross_batch_close_readiness_v240 import (
    build_receipt_chain_saved_view_owner_review_cross_batch_close_readiness_preview,
)


PACK_ID = "241"
PACK_NUMBER = 241
PACK_NAME = "Receipt Chain Saved View Owner Review Governance Index Preview"
ENDPOINT = "/tower/receipt-chain-saved-view-owner-review-governance-index-v241.json"

TOWER_AREA = "The Tower"
TOWER_SECTION = "Operational Containment"
TOWER_LAYER = "Receipt Chain Saved View Review Layer"
TOWER_SUBLAYER = "Governance Index Preview layer"

SAVE_BATCH = "241-245"
SAVE_AFTER_PACK = 245
NEXT_BATCH = "241-245"
SAFE_TO_CONTINUE_FLAG = "safe_to_continue_to_pack_242"
NEXT_PREP_FLAG = "prepare_pack_242_receipt_chain_saved_view_owner_review_governance_detail_drawer"

BLOCKED_REAL_ACTIONS = (
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
class GovernanceIndexCard:
    governance_id: str
    governance_key: str
    label: str
    category: str
    control_scope: str
    source_layer: str
    status: str
    readiness: int
    preview_only: bool
    writes_state: bool
    raw_evidence_visible: bool


@dataclass(frozen=True)
class GovernanceControlLane:
    lane_id: str
    label: str
    lane_scope: str
    control_count: int
    lane_mode: str
    writes_state: bool
    raw_evidence_visible: bool


@dataclass(frozen=True)
class GovernanceControlAction:
    action_id: str
    governance_id: str
    label: str
    visible: bool
    enabled: bool
    result: str
    reason: str


@dataclass(frozen=True)
class GovernanceCheckpoint:
    checkpoint_id: str
    label: str
    passed: bool
    result: str
    evidence_mode: str
    writes_state: bool


def _source_payload() -> Dict[str, Any]:
    return deepcopy(build_receipt_chain_saved_view_owner_review_cross_batch_close_readiness_preview())


def _build_governance_cards(source_payload: Dict[str, Any]) -> List[GovernanceIndexCard]:
    source_status = str(source_payload.get("status", "ready"))
    source_readiness = int(source_payload.get("readiness", 100))

    return [
        GovernanceIndexCard(
            governance_id="governance_index_241_preview_only_boundary",
            governance_key="preview_only_boundary",
            label="Preview-only governance boundary",
            category="safety_boundary",
            control_scope="all_owner_review_saved_view_layers",
            source_layer="cross_batch_close_readiness",
            status=source_status,
            readiness=source_readiness,
            preview_only=True,
            writes_state=False,
            raw_evidence_visible=False,
        ),
        GovernanceIndexCard(
            governance_id="governance_index_241_no_policy_mutation",
            governance_key="no_policy_mutation",
            label="No policy mutation governance",
            category="policy_guard",
            control_scope="policy_as_code_and_review_surfaces",
            source_layer="policy_boundary",
            status="ready",
            readiness=100,
            preview_only=True,
            writes_state=False,
            raw_evidence_visible=False,
        ),
        GovernanceIndexCard(
            governance_id="governance_index_241_owner_action_execution_block",
            governance_key="owner_action_execution_block",
            label="Owner action execution block",
            category="owner_action_guard",
            control_scope="approval_denial_assignment_status",
            source_layer="owner_review_controls",
            status="ready",
            readiness=100,
            preview_only=True,
            writes_state=False,
            raw_evidence_visible=False,
        ),
        GovernanceIndexCard(
            governance_id="governance_index_241_saved_view_mutation_block",
            governance_key="saved_view_mutation_block",
            label="Saved-view mutation block",
            category="saved_view_guard",
            control_scope="restore_revert_write_edit_delete_apply_export",
            source_layer="saved_view_controls",
            status="ready",
            readiness=100,
            preview_only=True,
            writes_state=False,
            raw_evidence_visible=False,
        ),
        GovernanceIndexCard(
            governance_id="governance_index_241_raw_evidence_redaction",
            governance_key="raw_evidence_redaction",
            label="Raw evidence redaction governance",
            category="evidence_guard",
            control_scope="raw_evidence_reveal_and_export",
            source_layer="evidence_boundary",
            status="ready",
            readiness=100,
            preview_only=True,
            writes_state=False,
            raw_evidence_visible=False,
        ),
        GovernanceIndexCard(
            governance_id="governance_index_241_archive_write_block",
            governance_key="archive_write_block",
            label="Archive write block",
            category="archive_guard",
            control_scope="receipt_chain_archive_and_packet_exports",
            source_layer="archive_boundary",
            status="ready",
            readiness=100,
            preview_only=True,
            writes_state=False,
            raw_evidence_visible=False,
        ),
        GovernanceIndexCard(
            governance_id="governance_index_241_cross_batch_continuity_guard",
            governance_key="cross_batch_continuity_guard",
            label="Cross-batch continuity governance",
            category="cross_batch_guard",
            control_scope="221_225_226_230_231_235_236_240",
            source_layer="cross_batch_index",
            status="ready",
            readiness=100,
            preview_only=True,
            writes_state=False,
            raw_evidence_visible=False,
        ),
        GovernanceIndexCard(
            governance_id="governance_index_241_cache_non_recursive_guard",
            governance_key="cache_non_recursive_guard",
            label="Cached non-recursive builder governance",
            category="performance_guard",
            control_scope="quick_actions_unified_status_previews",
            source_layer="builder_boundary",
            status="ready",
            readiness=100,
            preview_only=True,
            writes_state=False,
            raw_evidence_visible=False,
        ),
    ]


def _build_lanes(cards: List[GovernanceIndexCard]) -> List[GovernanceControlLane]:
    categories = sorted({card.category for card in cards})
    lanes = [
        GovernanceControlLane(
            lane_id="governance_lane_241_all_controls",
            label="All Governance Controls",
            lane_scope="all_governance_controls",
            control_count=len(cards),
            lane_mode="view_only",
            writes_state=False,
            raw_evidence_visible=False,
        )
    ]

    for category in categories:
        count = sum(1 for card in cards if card.category == category)
        lanes.append(
            GovernanceControlLane(
                lane_id=f"governance_lane_241_{category}",
                label=f"{category.replace('_', ' ').title()}",
                lane_scope=category,
                control_count=count,
                lane_mode="view_only",
                writes_state=False,
                raw_evidence_visible=False,
            )
        )

    lanes.append(
        GovernanceControlLane(
            lane_id="governance_lane_241_next_pack_preparation",
            label="Pack 242 Detail Drawer Preparation",
            lane_scope="next_pack_preparation",
            control_count=1,
            lane_mode="view_only",
            writes_state=False,
            raw_evidence_visible=False,
        )
    )

    return lanes


def _build_actions(cards: List[GovernanceIndexCard]) -> List[GovernanceControlAction]:
    actions: List[GovernanceControlAction] = []

    for card in cards:
        actions.extend(
            [
                GovernanceControlAction(
                    action_id=f"{card.governance_id}_action_preview",
                    governance_id=card.governance_id,
                    label="Preview governance control",
                    visible=True,
                    enabled=True,
                    result="preview_allowed",
                    reason="Previewing a governance index card does not write state.",
                ),
                GovernanceControlAction(
                    action_id=f"{card.governance_id}_action_write_control",
                    governance_id=card.governance_id,
                    label="Write governance control",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Governance control writes are blocked.",
                ),
                GovernanceControlAction(
                    action_id=f"{card.governance_id}_action_change_policy",
                    governance_id=card.governance_id,
                    label="Change policy",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Policy changes are blocked.",
                ),
                GovernanceControlAction(
                    action_id=f"{card.governance_id}_action_execute_approval",
                    governance_id=card.governance_id,
                    label="Execute approval/denial",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Approval and denial execution are blocked.",
                ),
                GovernanceControlAction(
                    action_id=f"{card.governance_id}_action_apply_saved_view",
                    governance_id=card.governance_id,
                    label="Apply saved view",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Saved-view apply actions are blocked.",
                ),
                GovernanceControlAction(
                    action_id=f"{card.governance_id}_action_export_governance",
                    governance_id=card.governance_id,
                    label="Export governance packet",
                    visible=True,
                    enabled=False,
                    result="blocked_preview_only",
                    reason="Governance exports are blocked in preview mode.",
                ),
            ]
        )

    return actions


def _build_checkpoints() -> List[GovernanceCheckpoint]:
    return [
        GovernanceCheckpoint(
            checkpoint_id="governance_index_checkpoint_241_001",
            label="Governance index cards are preview-only",
            passed=True,
            result="passed",
            evidence_mode="safe_summary_only",
            writes_state=False,
        ),
        GovernanceCheckpoint(
            checkpoint_id="governance_index_checkpoint_241_002",
            label="Governance lanes are view-only and non-mutating",
            passed=True,
            result="passed",
            evidence_mode="safe_summary_only",
            writes_state=False,
        ),
        GovernanceCheckpoint(
            checkpoint_id="governance_index_checkpoint_241_003",
            label="Governance writes and policy changes are blocked",
            passed=True,
            result="passed",
            evidence_mode="blocked_action_summary",
            writes_state=False,
        ),
        GovernanceCheckpoint(
            checkpoint_id="governance_index_checkpoint_241_004",
            label="Owner approval/denial execution remains blocked",
            passed=True,
            result="passed",
            evidence_mode="blocked_action_summary",
            writes_state=False,
        ),
        GovernanceCheckpoint(
            checkpoint_id="governance_index_checkpoint_241_005",
            label="Saved-view mutations, archive writes, exports, and raw evidence reveal remain blocked",
            passed=True,
            result="passed",
            evidence_mode="redacted_pointer_only",
            writes_state=False,
        ),
        GovernanceCheckpoint(
            checkpoint_id="governance_index_checkpoint_241_006",
            label="Ready for Pack 242 governance detail drawer preview",
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
            "reason": "Pack 241 previews the governance index only and cannot mutate governance, policy, approvals, review, cross-batch, saved-view, archive, evidence, or action state.",
        }
        for action in BLOCKED_REAL_ACTIONS
    ]


@lru_cache(maxsize=1)
def _build_receipt_chain_saved_view_owner_review_governance_index_preview_cached() -> Dict[str, Any]:
    source_payload = _source_payload()

    cards_raw = _build_governance_cards(source_payload)
    lanes_raw = _build_lanes(cards_raw)
    actions_raw = _build_actions(cards_raw)
    checkpoints_raw = _build_checkpoints()

    cards = [asdict(card) for card in cards_raw]
    lanes = [asdict(lane) for lane in lanes_raw]
    actions = [asdict(action) for action in actions_raw]
    checkpoints = [asdict(checkpoint) for checkpoint in checkpoints_raw]

    enabled_action_count = sum(1 for action in actions if action["enabled"] is True)
    blocked_action_count = sum(1 for action in actions if action["enabled"] is False)
    category_count = len({card["category"] for card in cards})

    all_cards_ready = all(card["status"] == "ready" and card["readiness"] == 100 for card in cards)
    all_cards_preview_only = all(card["preview_only"] is True for card in cards)
    all_cards_no_writes = all(card["writes_state"] is False for card in cards)
    all_cards_no_raw_evidence = all(card["raw_evidence_visible"] is False for card in cards)
    all_lanes_view_only = all(lane["lane_mode"] == "view_only" for lane in lanes)
    all_lanes_no_writes = all(lane["writes_state"] is False for lane in lanes)
    all_lanes_no_raw_evidence = all(lane["raw_evidence_visible"] is False for lane in lanes)
    all_actions_safe = all(action["result"] in {"preview_allowed", "blocked_preview_only"} for action in actions)
    all_checkpoints_passed = all(checkpoint["passed"] is True for checkpoint in checkpoints)
    all_checkpoints_no_writes = all(checkpoint["writes_state"] is False for checkpoint in checkpoints)

    governance_index_ready = all([
        all_cards_ready,
        all_cards_preview_only,
        all_cards_no_writes,
        all_cards_no_raw_evidence,
        all_lanes_view_only,
        all_lanes_no_writes,
        all_lanes_no_raw_evidence,
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
        "receipt_chain_layer": "saved_view_owner_review_governance_index_preview",
        "source_pack": source_payload.get("pack"),
        "source_endpoint": source_payload.get("endpoint"),
        "source_status": source_payload.get("status"),
        "source_readiness": source_payload.get("readiness"),
        "source_safe_to_continue": source_payload.get("safe_to_continue_to_pack_241"),
        "governance_index_cards": cards,
        "governance_control_lanes": lanes,
        "governance_control_actions": actions,
        "governance_checkpoints": checkpoints,
        "governance_index_summary": {
            "source_pack": source_payload.get("pack"),
            "governance_card_count": len(cards),
            "governance_lane_count": len(lanes),
            "governance_action_count": len(actions),
            "governance_checkpoint_count": len(checkpoints),
            "category_count": category_count,
            "enabled_action_count": enabled_action_count,
            "blocked_action_count": blocked_action_count,
            "all_cards_ready": all_cards_ready,
            "all_cards_preview_only": all_cards_preview_only,
            "all_cards_no_writes": all_cards_no_writes,
            "all_cards_no_raw_evidence": all_cards_no_raw_evidence,
            "all_lanes_view_only": all_lanes_view_only,
            "all_lanes_no_writes": all_lanes_no_writes,
            "all_lanes_no_raw_evidence": all_lanes_no_raw_evidence,
            "all_actions_safe": all_actions_safe,
            "all_checkpoints_passed": all_checkpoints_passed,
            "all_checkpoints_no_writes": all_checkpoints_no_writes,
            "governance_index_ready": governance_index_ready,
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
        "pack_241_acceptance": {
            "governance_index_cards_built": True,
            "governance_control_lanes_built": True,
            "governance_control_actions_built": True,
            "governance_policy_approval_execution_blocked": True,
            "ready_for_governance_detail_drawer": True,
        },
        SAFE_TO_CONTINUE_FLAG: True,
        NEXT_PREP_FLAG: {
            "pack": "242",
            "name": "Receipt Chain Saved View Owner Review Governance Detail Drawer Preview",
            "mode": "simulated_preview_only",
            "recommended_next_endpoint": "/tower/receipt-chain-saved-view-owner-review-governance-detail-drawer-v242.json",
            "save_batch": SAVE_BATCH,
            "save_after_pack": SAVE_AFTER_PACK,
        },
    }

    return preview


def build_receipt_chain_saved_view_owner_review_governance_index_preview() -> Dict[str, Any]:
    """Return a defensive copy of the cached Pack 241 preview payload."""
    return deepcopy(_build_receipt_chain_saved_view_owner_review_governance_index_preview_cached())


def build_pack_241_status_bridge() -> Dict[str, Any]:
    """Small cached status bridge for Tower cards/status surfaces."""
    preview = _build_receipt_chain_saved_view_owner_review_governance_index_preview_cached()
    summary = preview["governance_index_summary"]

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
        "governance_card_count": summary["governance_card_count"],
        "governance_lane_count": summary["governance_lane_count"],
        "governance_action_count": summary["governance_action_count"],
        "governance_index_ready": summary["governance_index_ready"],
        SAFE_TO_CONTINUE_FLAG: preview[SAFE_TO_CONTINUE_FLAG],
    }


def prepare_pack_242_receipt_chain_saved_view_owner_review_governance_detail_drawer() -> Dict[str, Any]:
    """Prepare Pack 242 direction without writing state."""
    return {
        "ready": True,
        "next_pack": "242",
        "name": "Receipt Chain Saved View Owner Review Governance Detail Drawer Preview",
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
    "build_receipt_chain_saved_view_owner_review_governance_index_preview",
    "build_pack_241_status_bridge",
    "prepare_pack_242_receipt_chain_saved_view_owner_review_governance_detail_drawer",
]
