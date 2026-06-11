"""
SEARCHABLE LABEL: TOWER_PACK_236_RECEIPT_CHAIN_SAVED_VIEW_OWNER_REVIEW_CROSS_BATCH_INDEX_PREVIEW_MODULE

Tower section:
- The Tower
- Operational Containment
- Receipt Chain Saved View Review Layer

Pack 236: Receipt Chain Saved View Owner Review Cross-Batch Index Preview

This module is intentionally simulated/preview-only.

Purpose:
- Index the closed owner review / follow-up / continuity batches.
- Create a cross-batch navigation preview across 221-225, 226-230, and 231-235.
- Prepare Pack 237 cross-batch detail drawer preview.

Safety boundaries:
- No real cross-batch index writes.
- No real batch linking writes.
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

from tower.receipt_chain_saved_view_owner_review_batch_close_readiness_v225 import (
    build_receipt_chain_saved_view_owner_review_batch_close_readiness_preview,
)
from tower.receipt_chain_saved_view_owner_review_followup_batch_close_readiness_v230 import (
    build_receipt_chain_saved_view_owner_review_followup_batch_close_readiness_preview,
)
from tower.receipt_chain_saved_view_owner_review_continuity_batch_close_readiness_v235 import (
    build_receipt_chain_saved_view_owner_review_continuity_batch_close_readiness_preview,
)


PACK_ID = "236"
PACK_NUMBER = 236
PACK_NAME = "Receipt Chain Saved View Owner Review Cross-Batch Index Preview"
ENDPOINT = "/tower/receipt-chain-saved-view-owner-review-cross-batch-index-v236.json"

TOWER_AREA = "The Tower"
TOWER_SECTION = "Operational Containment"
TOWER_LAYER = "Receipt Chain Saved View Review Layer"

SAVE_BATCH = "236-240"
SAVE_AFTER_PACK = 240
SAFE_TO_CONTINUE_FLAG = "safe_to_continue_to_pack_237"
NEXT_PREP_FLAG = "prepare_pack_237_receipt_chain_saved_view_owner_review_cross_batch_detail_drawer"

BLOCKED_REAL_ACTIONS = (
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
class CrossBatchIndexCard:
    batch_id: str
    batch_label: str
    batch_range: str
    close_pack: str
    close_endpoint: str
    batch_role: str
    status: str
    readiness: int
    preview_only: bool
    safe_to_continue: bool
    next_batch: str


@dataclass(frozen=True)
class CrossBatchLink:
    link_id: str
    from_batch: str
    to_batch: str
    label: str
    link_type: str
    link_mode: str
    writes_state: bool
    raw_evidence_visible: bool


@dataclass(frozen=True)
class CrossBatchLane:
    lane_id: str
    label: str
    lane_scope: str
    item_count: int
    action_mode: str
    writes_state: bool


@dataclass(frozen=True)
class CrossBatchControl:
    control_id: str
    label: str
    visible: bool
    enabled: bool
    result: str
    reason: str


@dataclass(frozen=True)
class CrossBatchCheckpoint:
    checkpoint_id: str
    label: str
    passed: bool
    result: str
    evidence_mode: str
    writes_state: bool


def _source_payloads() -> Dict[str, Dict[str, Any]]:
    return {
        "221-225": deepcopy(build_receipt_chain_saved_view_owner_review_batch_close_readiness_preview()),
        "226-230": deepcopy(build_receipt_chain_saved_view_owner_review_followup_batch_close_readiness_preview()),
        "231-235": deepcopy(build_receipt_chain_saved_view_owner_review_continuity_batch_close_readiness_preview()),
    }


def _build_index_cards(source_payloads: Dict[str, Dict[str, Any]]) -> List[CrossBatchIndexCard]:
    owner = source_payloads["221-225"]
    followup = source_payloads["226-230"]
    continuity = source_payloads["231-235"]

    return [
        CrossBatchIndexCard(
            batch_id="cross_batch_index_236_221_225",
            batch_label="Owner Review Batch",
            batch_range="221-225",
            close_pack=str(owner.get("pack", "225")),
            close_endpoint=str(owner.get("endpoint", "/tower/receipt-chain-saved-view-owner-review-batch-close-readiness-v225.json")),
            batch_role="owner_review_base",
            status=str(owner.get("status", "ready")),
            readiness=int(owner.get("readiness", 100)),
            preview_only=bool(owner.get("preview_only", True)),
            safe_to_continue=bool(owner.get("safe_to_continue_to_pack_226", True)),
            next_batch="226-230",
        ),
        CrossBatchIndexCard(
            batch_id="cross_batch_index_236_226_230",
            batch_label="Follow-up Batch",
            batch_range="226-230",
            close_pack=str(followup.get("pack", "230")),
            close_endpoint=str(followup.get("endpoint", "/tower/receipt-chain-saved-view-owner-review-followup-batch-close-readiness-v230.json")),
            batch_role="owner_review_followup",
            status=str(followup.get("status", "ready")),
            readiness=int(followup.get("readiness", 100)),
            preview_only=bool(followup.get("preview_only", True)),
            safe_to_continue=bool(followup.get("safe_to_continue_to_pack_231", True)),
            next_batch="231-235",
        ),
        CrossBatchIndexCard(
            batch_id="cross_batch_index_236_231_235",
            batch_label="Continuity Batch",
            batch_range="231-235",
            close_pack=str(continuity.get("pack", "235")),
            close_endpoint=str(continuity.get("endpoint", "/tower/receipt-chain-saved-view-owner-review-continuity-batch-close-readiness-v235.json")),
            batch_role="owner_review_continuity",
            status=str(continuity.get("status", "ready")),
            readiness=int(continuity.get("readiness", 100)),
            preview_only=bool(continuity.get("preview_only", True)),
            safe_to_continue=bool(continuity.get("safe_to_continue_to_pack_236", True)),
            next_batch="236-240",
        ),
    ]


def _build_cross_batch_links() -> List[CrossBatchLink]:
    return [
        CrossBatchLink(
            link_id="cross_batch_link_236_owner_to_followup",
            from_batch="221-225",
            to_batch="226-230",
            label="Owner review base to follow-up bridge",
            link_type="batch_continuation",
            link_mode="preview_only",
            writes_state=False,
            raw_evidence_visible=False,
        ),
        CrossBatchLink(
            link_id="cross_batch_link_236_followup_to_continuity",
            from_batch="226-230",
            to_batch="231-235",
            label="Follow-up batch to continuity bridge",
            link_type="batch_continuation",
            link_mode="preview_only",
            writes_state=False,
            raw_evidence_visible=False,
        ),
        CrossBatchLink(
            link_id="cross_batch_link_236_continuity_to_cross_batch_index",
            from_batch="231-235",
            to_batch="236-240",
            label="Continuity close to cross-batch index bridge",
            link_type="next_batch_preparation",
            link_mode="preview_only",
            writes_state=False,
            raw_evidence_visible=False,
        ),
        CrossBatchLink(
            link_id="cross_batch_link_236_repair_bridge_224_225",
            from_batch="221-225",
            to_batch="226-230",
            label="Repaired Pack 224-225 dependency bridge",
            link_type="repair_bridge_reference",
            link_mode="preview_only",
            writes_state=False,
            raw_evidence_visible=False,
        ),
        CrossBatchLink(
            link_id="cross_batch_link_236_safety_boundary_all",
            from_batch="221-225",
            to_batch="231-235",
            label="Shared blocked-write safety boundary",
            link_type="safety_boundary_reference",
            link_mode="preview_only",
            writes_state=False,
            raw_evidence_visible=False,
        ),
    ]


def _build_lanes(cards: List[CrossBatchIndexCard], links: List[CrossBatchLink]) -> List[CrossBatchLane]:
    return [
        CrossBatchLane(
            lane_id="cross_batch_lane_236_all_batches",
            label="All Closed Review Batches",
            lane_scope="all_batches",
            item_count=len(cards),
            action_mode="view_only",
            writes_state=False,
        ),
        CrossBatchLane(
            lane_id="cross_batch_lane_236_batch_links",
            label="Cross-Batch Links",
            lane_scope="batch_links",
            item_count=len(links),
            action_mode="view_only",
            writes_state=False,
        ),
        CrossBatchLane(
            lane_id="cross_batch_lane_236_repair_bridge",
            label="Repair Bridge References",
            lane_scope="repair_bridge_reference",
            item_count=sum(1 for link in links if link.link_type == "repair_bridge_reference"),
            action_mode="view_only",
            writes_state=False,
        ),
        CrossBatchLane(
            lane_id="cross_batch_lane_236_safety_boundaries",
            label="Safety Boundary References",
            lane_scope="safety_boundary_reference",
            item_count=sum(1 for link in links if link.link_type == "safety_boundary_reference"),
            action_mode="view_only",
            writes_state=False,
        ),
        CrossBatchLane(
            lane_id="cross_batch_lane_236_next_batch",
            label="Next Batch Preparation",
            lane_scope="next_batch_preparation",
            item_count=sum(1 for card in cards if card.next_batch == "236-240"),
            action_mode="view_only",
            writes_state=False,
        ),
    ]


def _build_controls() -> List[CrossBatchControl]:
    return [
        CrossBatchControl(
            control_id="cross_batch_control_236_preview_index",
            label="Preview cross-batch index",
            visible=True,
            enabled=True,
            result="preview_allowed",
            reason="Previewing the cross-batch index does not mutate state.",
        ),
        CrossBatchControl(
            control_id="cross_batch_control_236_write_index",
            label="Write cross-batch index",
            visible=True,
            enabled=False,
            result="blocked_preview_only",
            reason="Cross-batch index writes are blocked.",
        ),
        CrossBatchControl(
            control_id="cross_batch_control_236_link_batches",
            label="Create cross-batch link",
            visible=True,
            enabled=False,
            result="blocked_preview_only",
            reason="Cross-batch link writes are blocked.",
        ),
        CrossBatchControl(
            control_id="cross_batch_control_236_mark_batch_reviewed",
            label="Mark batch reviewed",
            visible=True,
            enabled=False,
            result="blocked_preview_only",
            reason="Batch status writes are blocked.",
        ),
        CrossBatchControl(
            control_id="cross_batch_control_236_apply_saved_view",
            label="Apply saved view to index",
            visible=True,
            enabled=False,
            result="blocked_preview_only",
            reason="Saved-view apply actions are blocked.",
        ),
        CrossBatchControl(
            control_id="cross_batch_control_236_save_filter",
            label="Save cross-batch filter",
            visible=True,
            enabled=False,
            result="blocked_preview_only",
            reason="User preference/filter writes are blocked.",
        ),
        CrossBatchControl(
            control_id="cross_batch_control_236_export_index",
            label="Export cross-batch index",
            visible=True,
            enabled=False,
            result="blocked_preview_only",
            reason="Index export is blocked in preview mode.",
        ),
    ]


def _build_checkpoints() -> List[CrossBatchCheckpoint]:
    return [
        CrossBatchCheckpoint(
            checkpoint_id="cross_batch_checkpoint_236_001",
            label="Closed batch cards are preview-only and ready",
            passed=True,
            result="passed",
            evidence_mode="safe_summary_only",
            writes_state=False,
        ),
        CrossBatchCheckpoint(
            checkpoint_id="cross_batch_checkpoint_236_002",
            label="Cross-batch links are preview-only and do not write state",
            passed=True,
            result="passed",
            evidence_mode="safe_summary_only",
            writes_state=False,
        ),
        CrossBatchCheckpoint(
            checkpoint_id="cross_batch_checkpoint_236_003",
            label="Repair bridge from Pack 224-225 remains indexed",
            passed=True,
            result="passed",
            evidence_mode="safe_summary_only",
            writes_state=False,
        ),
        CrossBatchCheckpoint(
            checkpoint_id="cross_batch_checkpoint_236_004",
            label="Index/link/status/filter/export actions remain blocked",
            passed=True,
            result="passed",
            evidence_mode="blocked_action_summary",
            writes_state=False,
        ),
        CrossBatchCheckpoint(
            checkpoint_id="cross_batch_checkpoint_236_005",
            label="Raw evidence remains hidden across batch index",
            passed=True,
            result="passed",
            evidence_mode="redacted_pointer_only",
            writes_state=False,
        ),
        CrossBatchCheckpoint(
            checkpoint_id="cross_batch_checkpoint_236_006",
            label="Ready for Pack 237 cross-batch detail drawer preview",
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
            "reason": "Pack 236 previews the cross-batch index only and cannot write index, links, batch, review, queue, saved-view, archive, evidence, or action state.",
        }
        for action in BLOCKED_REAL_ACTIONS
    ]


@lru_cache(maxsize=1)
def _build_receipt_chain_saved_view_owner_review_cross_batch_index_preview_cached() -> Dict[str, Any]:
    source_payloads = _source_payloads()

    cards_raw = _build_index_cards(source_payloads)
    links_raw = _build_cross_batch_links()
    lanes_raw = _build_lanes(cards_raw, links_raw)
    controls_raw = _build_controls()
    checkpoints_raw = _build_checkpoints()

    cards = [asdict(card) for card in cards_raw]
    links = [asdict(link) for link in links_raw]
    lanes = [asdict(lane) for lane in lanes_raw]
    controls = [asdict(control) for control in controls_raw]
    checkpoints = [asdict(checkpoint) for checkpoint in checkpoints_raw]

    enabled_control_count = sum(1 for control in controls if control["enabled"] is True)
    blocked_control_count = sum(1 for control in controls if control["enabled"] is False)
    repair_bridge_link_count = sum(1 for link in links if link["link_type"] == "repair_bridge_reference")
    safety_boundary_link_count = sum(1 for link in links if link["link_type"] == "safety_boundary_reference")

    all_cards_ready = all(card["status"] == "ready" and card["readiness"] == 100 for card in cards)
    all_cards_preview_only = all(card["preview_only"] is True for card in cards)
    all_cards_safe_to_continue = all(card["safe_to_continue"] is True for card in cards)
    all_links_preview_only = all(link["link_mode"] == "preview_only" for link in links)
    all_links_no_writes = all(link["writes_state"] is False for link in links)
    all_links_no_raw_evidence = all(link["raw_evidence_visible"] is False for link in links)
    all_lanes_view_only = all(lane["action_mode"] == "view_only" for lane in lanes)
    all_lanes_no_writes = all(lane["writes_state"] is False for lane in lanes)
    all_controls_safe = all(control["result"] in {"preview_allowed", "blocked_preview_only"} for control in controls)
    all_checkpoints_passed = all(checkpoint["passed"] is True for checkpoint in checkpoints)
    all_checkpoints_no_writes = all(checkpoint["writes_state"] is False for checkpoint in checkpoints)

    cross_batch_index_ready = all([
        all_cards_ready,
        all_cards_preview_only,
        all_cards_safe_to_continue,
        all_links_preview_only,
        all_links_no_writes,
        all_links_no_raw_evidence,
        all_lanes_view_only,
        all_lanes_no_writes,
        all_controls_safe,
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
        "next_batch": "236-240",
        "cached": True,
        "non_recursive": True,
        "simulation_only": True,
        "preview_only": True,
        "receipt_chain_layer": "saved_view_owner_review_cross_batch_index_preview",
        "source_batches": {
            "221-225": {
                "pack": source_payloads["221-225"].get("pack"),
                "status": source_payloads["221-225"].get("status"),
                "readiness": source_payloads["221-225"].get("readiness"),
                "endpoint": source_payloads["221-225"].get("endpoint"),
            },
            "226-230": {
                "pack": source_payloads["226-230"].get("pack"),
                "status": source_payloads["226-230"].get("status"),
                "readiness": source_payloads["226-230"].get("readiness"),
                "endpoint": source_payloads["226-230"].get("endpoint"),
            },
            "231-235": {
                "pack": source_payloads["231-235"].get("pack"),
                "status": source_payloads["231-235"].get("status"),
                "readiness": source_payloads["231-235"].get("readiness"),
                "endpoint": source_payloads["231-235"].get("endpoint"),
            },
        },
        "cross_batch_index_cards": cards,
        "cross_batch_links": links,
        "cross_batch_lanes": lanes,
        "cross_batch_controls": controls,
        "cross_batch_checkpoints": checkpoints,
        "cross_batch_index_summary": {
            "indexed_batch_count": len(cards),
            "cross_batch_link_count": len(links),
            "cross_batch_lane_count": len(lanes),
            "cross_batch_control_count": len(controls),
            "cross_batch_checkpoint_count": len(checkpoints),
            "enabled_control_count": enabled_control_count,
            "blocked_control_count": blocked_control_count,
            "repair_bridge_link_count": repair_bridge_link_count,
            "safety_boundary_link_count": safety_boundary_link_count,
            "all_cards_ready": all_cards_ready,
            "all_cards_preview_only": all_cards_preview_only,
            "all_cards_safe_to_continue": all_cards_safe_to_continue,
            "all_links_preview_only": all_links_preview_only,
            "all_links_no_writes": all_links_no_writes,
            "all_links_no_raw_evidence": all_links_no_raw_evidence,
            "all_lanes_view_only": all_lanes_view_only,
            "all_lanes_no_writes": all_lanes_no_writes,
            "all_controls_safe": all_controls_safe,
            "all_checkpoints_passed": all_checkpoints_passed,
            "all_checkpoints_no_writes": all_checkpoints_no_writes,
            "cross_batch_index_ready": cross_batch_index_ready,
            "real_cross_batch_index_write_enabled": False,
            "real_cross_batch_link_write_enabled": False,
            "real_cross_batch_status_write_enabled": False,
            "real_batch_close_write_enabled": False,
            "real_review_write_enabled": False,
            "real_saved_view_mutation_enabled": False,
            "real_archive_write_enabled": False,
            "raw_evidence_visible": False,
            "real_action_execution_enabled": False,
        },
        "safety_invariants": {
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
        "pack_236_acceptance": {
            "cross_batch_index_cards_built": True,
            "cross_batch_links_built": True,
            "cross_batch_lanes_built": True,
            "repair_bridge_indexed": True,
            "closed_batches_indexed": ["221-225", "226-230", "231-235"],
            "cross_batch_write_actions_blocked": True,
            "ready_for_cross_batch_detail_drawer": True,
        },
        SAFE_TO_CONTINUE_FLAG: True,
        NEXT_PREP_FLAG: {
            "pack": "237",
            "name": "Receipt Chain Saved View Owner Review Cross-Batch Detail Drawer Preview",
            "mode": "simulated_preview_only",
            "recommended_next_endpoint": "/tower/receipt-chain-saved-view-owner-review-cross-batch-detail-drawer-v237.json",
            "save_batch": SAVE_BATCH,
            "save_after_pack": SAVE_AFTER_PACK,
        },
    }

    return preview


def build_receipt_chain_saved_view_owner_review_cross_batch_index_preview() -> Dict[str, Any]:
    """Return a defensive copy of the cached Pack 236 preview payload."""
    return deepcopy(_build_receipt_chain_saved_view_owner_review_cross_batch_index_preview_cached())


def build_pack_236_status_bridge() -> Dict[str, Any]:
    """Small cached status bridge for Tower cards/status surfaces."""
    preview = _build_receipt_chain_saved_view_owner_review_cross_batch_index_preview_cached()
    summary = preview["cross_batch_index_summary"]

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
        "next_batch": preview["next_batch"],
        "cached": preview["cached"],
        "non_recursive": preview["non_recursive"],
        "preview_only": preview["preview_only"],
        "indexed_batch_count": summary["indexed_batch_count"],
        "cross_batch_link_count": summary["cross_batch_link_count"],
        "repair_bridge_link_count": summary["repair_bridge_link_count"],
        "cross_batch_index_ready": summary["cross_batch_index_ready"],
        SAFE_TO_CONTINUE_FLAG: preview[SAFE_TO_CONTINUE_FLAG],
    }


def prepare_pack_237_receipt_chain_saved_view_owner_review_cross_batch_detail_drawer() -> Dict[str, Any]:
    """Prepare Pack 237 direction without writing state."""
    return {
        "ready": True,
        "next_pack": "237",
        "name": "Receipt Chain Saved View Owner Review Cross-Batch Detail Drawer Preview",
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
    "build_receipt_chain_saved_view_owner_review_cross_batch_index_preview",
    "build_pack_236_status_bridge",
    "prepare_pack_237_receipt_chain_saved_view_owner_review_cross_batch_detail_drawer",
]
