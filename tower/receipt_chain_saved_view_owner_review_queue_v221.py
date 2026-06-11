"""
SEARCHABLE LABEL: TOWER_PACK_221_RECEIPT_CHAIN_SAVED_VIEW_OWNER_REVIEW_QUEUE_PREVIEW_MODULE

Tower section:
- The Tower
- Operational Containment
- Receipt Chain Saved View Review Layer

Pack 221: Receipt Chain Saved View Owner Review Queue Preview

This module is intentionally simulated/preview-only.

Safety boundaries:
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

from tower.receipt_chain_saved_view_batch_close_readiness_v220 import (
    build_receipt_chain_saved_view_batch_close_readiness_preview,
)


PACK_ID = "221"
PACK_NUMBER = 221
PACK_NAME = "Receipt Chain Saved View Owner Review Queue Preview"
ENDPOINT = "/tower/receipt-chain-saved-view-owner-review-queue-v221.json"

TOWER_AREA = "The Tower"
TOWER_SECTION = "Operational Containment"
TOWER_LAYER = "Receipt Chain Saved View Review Layer"

SAVE_BATCH = "221-225"
SAVE_AFTER_PACK = 225
SAFE_TO_CONTINUE_FLAG = "safe_to_continue_to_pack_222"
NEXT_PREP_FLAG = "prepare_pack_222_saved_view_owner_review_detail_drawer"

BLOCKED_REAL_ACTIONS = (
    "real_owner_review_approve",
    "real_owner_review_deny",
    "real_owner_review_assign",
    "real_owner_review_note_write",
    "real_queue_reorder_write",
    "real_queue_filter_save",
    "real_batch_close_write",
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
class OwnerReviewQueueItem:
    queue_item_id: str
    review_key: str
    label: str
    source_pack: str
    source_endpoint: str
    priority: str
    review_status: str
    owner_action_mode: str
    evidence_mode: str
    raw_evidence_visible: bool
    executable: bool
    owner_review_hint: str


@dataclass(frozen=True)
class OwnerReviewQueueLane:
    lane_id: str
    label: str
    priority_scope: str
    item_count: int
    action_mode: str
    writes_state: bool


@dataclass(frozen=True)
class OwnerReviewQueueControl:
    control_id: str
    label: str
    visible: bool
    enabled: bool
    result: str
    reason: str


@dataclass(frozen=True)
class OwnerReviewQueueCheckpoint:
    checkpoint_id: str
    label: str
    passed: bool
    result: str
    evidence_mode: str
    writes_state: bool


def _source_payload() -> Dict[str, Any]:
    return deepcopy(build_receipt_chain_saved_view_batch_close_readiness_preview())


def _build_queue_items(source_payload: Dict[str, Any]) -> List[OwnerReviewQueueItem]:
    return [
        OwnerReviewQueueItem(
            queue_item_id="owner_review_queue_221_001",
            review_key="batch_216_220_close_readiness",
            label="Batch 216-220 close readiness review",
            source_pack="220",
            source_endpoint=source_payload.get("endpoint", ""),
            priority="critical",
            review_status="ready_for_owner_preview",
            owner_action_mode="preview_only",
            evidence_mode="safe_summary_only",
            raw_evidence_visible=False,
            executable=False,
            owner_review_hint="Confirm batch close readiness before continuing deeper saved-view review lanes.",
        ),
        OwnerReviewQueueItem(
            queue_item_id="owner_review_queue_221_002",
            review_key="saved_view_history_review",
            label="Saved-view history timeline review",
            source_pack="219A",
            source_endpoint="/tower/receipt-chain-saved-view-history-v219a.json",
            priority="high",
            review_status="ready_for_owner_preview",
            owner_action_mode="preview_only",
            evidence_mode="receipt_pointer_only",
            raw_evidence_visible=False,
            executable=False,
            owner_review_hint="Review version history summaries without restore/revert actions.",
        ),
        OwnerReviewQueueItem(
            queue_item_id="owner_review_queue_221_003",
            review_key="saved_view_version_compare_review",
            label="Saved-view version compare review",
            source_pack="219B",
            source_endpoint="/tower/receipt-chain-saved-view-version-compare-v219b.json",
            priority="high",
            review_status="ready_for_owner_preview",
            owner_action_mode="preview_only",
            evidence_mode="redacted_compare_summary",
            raw_evidence_visible=False,
            executable=False,
            owner_review_hint="Review compare rows, redactions, and safety-control changes without export or restore.",
        ),
        OwnerReviewQueueItem(
            queue_item_id="owner_review_queue_221_004",
            review_key="compare_filter_navigation_review",
            label="Compare filter navigation review",
            source_pack="219C",
            source_endpoint="/tower/receipt-chain-saved-view-compare-filter-navigation-v219c.json",
            priority="medium",
            review_status="ready_for_owner_preview",
            owner_action_mode="preview_only",
            evidence_mode="safe_filter_summary",
            raw_evidence_visible=False,
            executable=False,
            owner_review_hint="Review filter/navigation lanes without saving preferences or applying filters.",
        ),
        OwnerReviewQueueItem(
            queue_item_id="owner_review_queue_221_005",
            review_key="blocked_mutation_actions_review",
            label="Blocked saved-view mutation actions review",
            source_pack="216-220",
            source_endpoint=source_payload.get("endpoint", ""),
            priority="critical",
            review_status="ready_for_owner_preview",
            owner_action_mode="preview_only",
            evidence_mode="blocked_action_summary",
            raw_evidence_visible=False,
            executable=False,
            owner_review_hint="Confirm all write/apply/export/archive/action paths remain blocked.",
        ),
        OwnerReviewQueueItem(
            queue_item_id="owner_review_queue_221_006",
            review_key="next_batch_221_225_review_path",
            label="Next batch 221-225 review path",
            source_pack="221",
            source_endpoint=ENDPOINT,
            priority="medium",
            review_status="ready_for_owner_preview",
            owner_action_mode="preview_only",
            evidence_mode="safe_summary_only",
            raw_evidence_visible=False,
            executable=False,
            owner_review_hint="Confirm the next review detail drawer should be prepared in Pack 222.",
        ),
    ]


def _build_queue_lanes(items: List[OwnerReviewQueueItem]) -> List[OwnerReviewQueueLane]:
    priorities = ["critical", "high", "medium"]
    lanes: List[OwnerReviewQueueLane] = []

    for priority in priorities:
        count = sum(1 for item in items if item.priority == priority)
        lanes.append(
            OwnerReviewQueueLane(
                lane_id=f"owner_review_lane_221_{priority}",
                label=f"{priority.title()} Priority",
                priority_scope=priority,
                item_count=count,
                action_mode="view_only",
                writes_state=False,
            )
        )

    lanes.append(
        OwnerReviewQueueLane(
            lane_id="owner_review_lane_221_all_items",
            label="All Owner Review Items",
            priority_scope="all",
            item_count=len(items),
            action_mode="view_only",
            writes_state=False,
        )
    )

    return lanes


def _build_queue_controls() -> List[OwnerReviewQueueControl]:
    return [
        OwnerReviewQueueControl(
            control_id="owner_review_control_221_open_detail",
            label="Open detail preview",
            visible=True,
            enabled=True,
            result="preview_allowed",
            reason="Opening a preview drawer does not mutate state.",
        ),
        OwnerReviewQueueControl(
            control_id="owner_review_control_221_mark_reviewed",
            label="Mark reviewed",
            visible=True,
            enabled=False,
            result="blocked_preview_only",
            reason="Marking reviewed would write owner review state.",
        ),
        OwnerReviewQueueControl(
            control_id="owner_review_control_221_approve",
            label="Approve",
            visible=True,
            enabled=False,
            result="blocked_preview_only",
            reason="Owner approval execution is not allowed in this preview lane.",
        ),
        OwnerReviewQueueControl(
            control_id="owner_review_control_221_deny",
            label="Deny",
            visible=True,
            enabled=False,
            result="blocked_preview_only",
            reason="Owner denial execution is not allowed in this preview lane.",
        ),
        OwnerReviewQueueControl(
            control_id="owner_review_control_221_assign",
            label="Assign review",
            visible=True,
            enabled=False,
            result="blocked_preview_only",
            reason="Assignment would write queue ownership state.",
        ),
        OwnerReviewQueueControl(
            control_id="owner_review_control_221_write_note",
            label="Write owner note",
            visible=True,
            enabled=False,
            result="blocked_preview_only",
            reason="Owner note writes are blocked in Pack 221.",
        ),
        OwnerReviewQueueControl(
            control_id="owner_review_control_221_save_filter",
            label="Save queue filter",
            visible=True,
            enabled=False,
            result="blocked_preview_only",
            reason="Queue filter preference writes are blocked.",
        ),
    ]


def _build_queue_checkpoints() -> List[OwnerReviewQueueCheckpoint]:
    return [
        OwnerReviewQueueCheckpoint(
            checkpoint_id="owner_review_checkpoint_221_001",
            label="Queue items are preview-only",
            passed=True,
            result="passed",
            evidence_mode="safe_summary_only",
            writes_state=False,
        ),
        OwnerReviewQueueCheckpoint(
            checkpoint_id="owner_review_checkpoint_221_002",
            label="Queue controls block write actions",
            passed=True,
            result="passed",
            evidence_mode="blocked_action_summary",
            writes_state=False,
        ),
        OwnerReviewQueueCheckpoint(
            checkpoint_id="owner_review_checkpoint_221_003",
            label="Raw evidence remains hidden",
            passed=True,
            result="passed",
            evidence_mode="receipt_pointer_only",
            writes_state=False,
        ),
        OwnerReviewQueueCheckpoint(
            checkpoint_id="owner_review_checkpoint_221_004",
            label="Archive writes remain blocked",
            passed=True,
            result="passed",
            evidence_mode="safe_summary_only",
            writes_state=False,
        ),
        OwnerReviewQueueCheckpoint(
            checkpoint_id="owner_review_checkpoint_221_005",
            label="Real owner action execution remains blocked",
            passed=True,
            result="passed",
            evidence_mode="safe_summary_only",
            writes_state=False,
        ),
        OwnerReviewQueueCheckpoint(
            checkpoint_id="owner_review_checkpoint_221_006",
            label="Ready for Pack 222 detail drawer preview",
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
            "reason": "Pack 221 previews the owner review queue only and cannot write review, saved-view, archive, evidence, or action state.",
        }
        for action in BLOCKED_REAL_ACTIONS
    ]


@lru_cache(maxsize=1)
def _build_receipt_chain_saved_view_owner_review_queue_preview_cached() -> Dict[str, Any]:
    source_payload = _source_payload()

    queue_items_raw = _build_queue_items(source_payload)
    queue_lanes_raw = _build_queue_lanes(queue_items_raw)
    queue_controls_raw = _build_queue_controls()
    queue_checkpoints_raw = _build_queue_checkpoints()

    queue_items = [asdict(item) for item in queue_items_raw]
    queue_lanes = [asdict(lane) for lane in queue_lanes_raw]
    queue_controls = [asdict(control) for control in queue_controls_raw]
    queue_checkpoints = [asdict(checkpoint) for checkpoint in queue_checkpoints_raw]

    enabled_control_count = sum(1 for control in queue_controls if control["enabled"] is True)
    blocked_control_count = sum(1 for control in queue_controls if control["enabled"] is False)
    critical_item_count = sum(1 for item in queue_items if item["priority"] == "critical")
    high_item_count = sum(1 for item in queue_items if item["priority"] == "high")

    all_items_preview_only = all(item["owner_action_mode"] == "preview_only" for item in queue_items)
    all_items_non_executable = all(item["executable"] is False for item in queue_items)
    all_raw_evidence_hidden = all(item["raw_evidence_visible"] is False for item in queue_items)
    all_lanes_view_only = all(lane["action_mode"] == "view_only" for lane in queue_lanes)
    all_lanes_no_writes = all(lane["writes_state"] is False for lane in queue_lanes)
    all_checkpoints_passed = all(checkpoint["passed"] is True for checkpoint in queue_checkpoints)
    all_checkpoints_no_writes = all(checkpoint["writes_state"] is False for checkpoint in queue_checkpoints)

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
        "receipt_chain_layer": "saved_view_owner_review_queue_preview",
        "source_pack": source_payload.get("pack"),
        "source_endpoint": source_payload.get("endpoint"),
        "source_status": source_payload.get("status"),
        "source_readiness": source_payload.get("readiness"),
        "source_safe_to_continue": source_payload.get("safe_to_continue_to_pack_221"),
        "owner_review_queue_items": queue_items,
        "owner_review_queue_lanes": queue_lanes,
        "owner_review_queue_controls": queue_controls,
        "owner_review_queue_checkpoints": queue_checkpoints,
        "owner_review_queue_summary": {
            "queue_item_count": len(queue_items),
            "queue_lane_count": len(queue_lanes),
            "queue_control_count": len(queue_controls),
            "queue_checkpoint_count": len(queue_checkpoints),
            "enabled_control_count": enabled_control_count,
            "blocked_control_count": blocked_control_count,
            "critical_item_count": critical_item_count,
            "high_item_count": high_item_count,
            "all_items_preview_only": all_items_preview_only,
            "all_items_non_executable": all_items_non_executable,
            "all_raw_evidence_hidden": all_raw_evidence_hidden,
            "all_lanes_view_only": all_lanes_view_only,
            "all_lanes_no_writes": all_lanes_no_writes,
            "all_checkpoints_passed": all_checkpoints_passed,
            "all_checkpoints_no_writes": all_checkpoints_no_writes,
            "owner_review_queue_ready": all([
                all_items_preview_only,
                all_items_non_executable,
                all_raw_evidence_hidden,
                all_lanes_view_only,
                all_lanes_no_writes,
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
            "no_real_queue_reorder_write": True,
            "no_real_queue_filter_save": True,
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
        "pack_221_acceptance": {
            "owner_review_queue_built": True,
            "owner_review_lanes_built": True,
            "owner_review_controls_built": True,
            "owner_review_write_actions_blocked": True,
            "ready_for_owner_review_detail_drawer": True,
        },
        SAFE_TO_CONTINUE_FLAG: True,
        NEXT_PREP_FLAG: {
            "pack": "222",
            "name": "Receipt Chain Saved View Owner Review Detail Drawer Preview",
            "mode": "simulated_preview_only",
            "recommended_next_endpoint": "/tower/receipt-chain-saved-view-owner-review-detail-drawer-v222.json",
            "save_batch": SAVE_BATCH,
            "save_after_pack": SAVE_AFTER_PACK,
        },
    }

    return preview


def build_receipt_chain_saved_view_owner_review_queue_preview() -> Dict[str, Any]:
    """Return a defensive copy of the cached Pack 221 preview payload."""
    return deepcopy(_build_receipt_chain_saved_view_owner_review_queue_preview_cached())


def build_pack_221_status_bridge() -> Dict[str, Any]:
    """Small cached status bridge for Tower cards/status surfaces."""
    preview = _build_receipt_chain_saved_view_owner_review_queue_preview_cached()
    summary = preview["owner_review_queue_summary"]

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
        "queue_item_count": summary["queue_item_count"],
        "queue_lane_count": summary["queue_lane_count"],
        "queue_control_count": summary["queue_control_count"],
        "owner_review_queue_ready": summary["owner_review_queue_ready"],
        SAFE_TO_CONTINUE_FLAG: preview[SAFE_TO_CONTINUE_FLAG],
    }


def prepare_pack_222_saved_view_owner_review_detail_drawer() -> Dict[str, Any]:
    """Prepare Pack 222 next-batch direction without writing state."""
    return {
        "ready": True,
        "next_pack": "222",
        "name": "Receipt Chain Saved View Owner Review Detail Drawer Preview",
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
    "build_receipt_chain_saved_view_owner_review_queue_preview",
    "build_pack_221_status_bridge",
    "prepare_pack_222_saved_view_owner_review_detail_drawer",
]
