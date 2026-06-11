"""
SEARCHABLE LABEL: TOWER_PACK_226_RECEIPT_CHAIN_SAVED_VIEW_OWNER_REVIEW_FOLLOWUP_QUEUE_PREVIEW_MODULE

Tower section:
- The Tower
- Operational Containment
- Receipt Chain Saved View Review Layer

Pack 226: Receipt Chain Saved View Owner Review Follow-up Queue Preview

This module is intentionally simulated/preview-only.

Safety boundaries:
- No real owner follow-up assignment.
- No real owner approval or denial.
- No real owner note/version writes.
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

from tower.receipt_chain_saved_view_owner_review_batch_close_readiness_v225 import (
    build_receipt_chain_saved_view_owner_review_batch_close_readiness_preview,
)


PACK_ID = "226"
PACK_NUMBER = 226
PACK_NAME = "Receipt Chain Saved View Owner Review Follow-up Queue Preview"
ENDPOINT = "/tower/receipt-chain-saved-view-owner-review-followup-queue-v226.json"

TOWER_AREA = "The Tower"
TOWER_SECTION = "Operational Containment"
TOWER_LAYER = "Receipt Chain Saved View Review Layer"

SAVE_BATCH = "226-230"
SAVE_AFTER_PACK = 230
SAFE_TO_CONTINUE_FLAG = "safe_to_continue_to_pack_227"
NEXT_PREP_FLAG = "prepare_pack_227_receipt_chain_saved_view_owner_review_followup_detail_drawer"

BLOCKED_REAL_ACTIONS = (
    "real_followup_assignment_write",
    "real_followup_status_write",
    "real_followup_due_date_write",
    "real_followup_note_write",
    "real_owner_review_note_version_write",
    "real_owner_review_note_version_restore",
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
class FollowupQueueItem:
    followup_item_id: str
    followup_key: str
    label: str
    source_pack: str
    source_endpoint: str
    priority: str
    followup_status: str
    followup_type: str
    owner_action_mode: str
    evidence_mode: str
    raw_evidence_visible: bool
    executable: bool
    followup_hint: str


@dataclass(frozen=True)
class FollowupQueueLane:
    lane_id: str
    label: str
    lane_scope: str
    item_count: int
    action_mode: str
    writes_state: bool


@dataclass(frozen=True)
class FollowupQueueControl:
    control_id: str
    label: str
    visible: bool
    enabled: bool
    result: str
    reason: str


@dataclass(frozen=True)
class FollowupQueueCheckpoint:
    checkpoint_id: str
    label: str
    passed: bool
    result: str
    evidence_mode: str
    writes_state: bool


def _source_payload() -> Dict[str, Any]:
    return deepcopy(build_receipt_chain_saved_view_owner_review_batch_close_readiness_preview())


def _build_followup_items(source_payload: Dict[str, Any]) -> List[FollowupQueueItem]:
    return [
        FollowupQueueItem(
            followup_item_id="followup_queue_226_001",
            followup_key="batch_221_225_closed_review",
            label="Confirm owner review batch 221-225 closure",
            source_pack="225",
            source_endpoint=source_payload.get("endpoint", ""),
            priority="critical",
            followup_status="followup_preview_ready",
            followup_type="batch_close_review",
            owner_action_mode="preview_only",
            evidence_mode="safe_summary_only",
            raw_evidence_visible=False,
            executable=False,
            followup_hint="Review the closed owner review batch before moving deeper into follow-up routing.",
        ),
        FollowupQueueItem(
            followup_item_id="followup_queue_226_002",
            followup_key="note_version_followup_review",
            label="Review note version preview outcomes",
            source_pack="224",
            source_endpoint="/tower/receipt-chain-saved-view-owner-review-note-version-v224.json",
            priority="high",
            followup_status="followup_preview_ready",
            followup_type="note_version_review",
            owner_action_mode="preview_only",
            evidence_mode="redacted_compare_summary",
            raw_evidence_visible=False,
            executable=False,
            followup_hint="Review version compare summaries without restoring or applying any version.",
        ),
        FollowupQueueItem(
            followup_item_id="followup_queue_226_003",
            followup_key="note_draft_followup_review",
            label="Review note draft preview outcomes",
            source_pack="223",
            source_endpoint="/tower/receipt-chain-saved-view-owner-review-note-draft-v223.json",
            priority="high",
            followup_status="followup_preview_ready",
            followup_type="note_draft_review",
            owner_action_mode="preview_only",
            evidence_mode="safe_draft_summary",
            raw_evidence_visible=False,
            executable=False,
            followup_hint="Review note draft fields without saving or submitting any notes.",
        ),
        FollowupQueueItem(
            followup_item_id="followup_queue_226_004",
            followup_key="detail_drawer_followup_review",
            label="Review detail drawer preview outcomes",
            source_pack="222",
            source_endpoint="/tower/receipt-chain-saved-view-owner-review-detail-drawer-v222.json",
            priority="medium",
            followup_status="followup_preview_ready",
            followup_type="detail_drawer_review",
            owner_action_mode="preview_only",
            evidence_mode="safe_pointer_only",
            raw_evidence_visible=False,
            executable=False,
            followup_hint="Review detail drawer safety boundaries without opening raw evidence.",
        ),
        FollowupQueueItem(
            followup_item_id="followup_queue_226_005",
            followup_key="owner_queue_followup_review",
            label="Review original owner queue preview outcomes",
            source_pack="221",
            source_endpoint="/tower/receipt-chain-saved-view-owner-review-queue-v221.json",
            priority="medium",
            followup_status="followup_preview_ready",
            followup_type="queue_review",
            owner_action_mode="preview_only",
            evidence_mode="safe_summary_only",
            raw_evidence_visible=False,
            executable=False,
            followup_hint="Confirm the original owner review queue remains preview-only.",
        ),
        FollowupQueueItem(
            followup_item_id="followup_queue_226_006",
            followup_key="blocked_actions_followup_review",
            label="Review blocked action matrix continuity",
            source_pack="221-225",
            source_endpoint=source_payload.get("endpoint", ""),
            priority="critical",
            followup_status="followup_preview_ready",
            followup_type="blocked_action_review",
            owner_action_mode="preview_only",
            evidence_mode="blocked_action_summary",
            raw_evidence_visible=False,
            executable=False,
            followup_hint="Confirm all owner, queue, note, saved-view, archive, evidence, and action writes remain blocked.",
        ),
        FollowupQueueItem(
            followup_item_id="followup_queue_226_007",
            followup_key="next_batch_226_230_followup_path",
            label="Prepare next follow-up detail path",
            source_pack="226",
            source_endpoint=ENDPOINT,
            priority="medium",
            followup_status="followup_preview_ready",
            followup_type="next_pack_preparation",
            owner_action_mode="preview_only",
            evidence_mode="safe_summary_only",
            raw_evidence_visible=False,
            executable=False,
            followup_hint="Prepare Pack 227 follow-up detail drawer preview without assigning or writing follow-up state.",
        ),
    ]


def _build_followup_lanes(items: List[FollowupQueueItem]) -> List[FollowupQueueLane]:
    lane_specs = [
        ("critical", "Critical Follow-ups", "priority_critical"),
        ("high", "High Follow-ups", "priority_high"),
        ("medium", "Medium Follow-ups", "priority_medium"),
        ("blocked_action_review", "Blocked Action Follow-ups", "type_blocked_action_review"),
        ("all", "All Follow-up Items", "all_items"),
    ]

    lanes: List[FollowupQueueLane] = []
    for key, label, scope in lane_specs:
        if key == "all":
            count = len(items)
        elif key in {"critical", "high", "medium"}:
            count = sum(1 for item in items if item.priority == key)
        else:
            count = sum(1 for item in items if item.followup_type == key)

        lanes.append(
            FollowupQueueLane(
                lane_id=f"followup_lane_226_{key}",
                label=label,
                lane_scope=scope,
                item_count=count,
                action_mode="view_only",
                writes_state=False,
            )
        )

    return lanes


def _build_followup_controls() -> List[FollowupQueueControl]:
    return [
        FollowupQueueControl(
            control_id="followup_control_226_open_detail_preview",
            label="Open follow-up detail preview",
            visible=True,
            enabled=True,
            result="preview_allowed",
            reason="Opening a preview drawer does not mutate follow-up state.",
        ),
        FollowupQueueControl(
            control_id="followup_control_226_assign_owner",
            label="Assign owner follow-up",
            visible=True,
            enabled=False,
            result="blocked_preview_only",
            reason="Follow-up assignment would write queue ownership state.",
        ),
        FollowupQueueControl(
            control_id="followup_control_226_mark_done",
            label="Mark follow-up done",
            visible=True,
            enabled=False,
            result="blocked_preview_only",
            reason="Marking follow-up done would write follow-up status.",
        ),
        FollowupQueueControl(
            control_id="followup_control_226_set_due_date",
            label="Set due date",
            visible=True,
            enabled=False,
            result="blocked_preview_only",
            reason="Due date changes would write follow-up state.",
        ),
        FollowupQueueControl(
            control_id="followup_control_226_write_note",
            label="Write follow-up note",
            visible=True,
            enabled=False,
            result="blocked_preview_only",
            reason="Follow-up note writes are blocked.",
        ),
        FollowupQueueControl(
            control_id="followup_control_226_save_filter",
            label="Save follow-up filter",
            visible=True,
            enabled=False,
            result="blocked_preview_only",
            reason="Filter preference writes are blocked.",
        ),
        FollowupQueueControl(
            control_id="followup_control_226_export_packet",
            label="Export follow-up packet",
            visible=True,
            enabled=False,
            result="blocked_preview_only",
            reason="Exports are blocked in the preview lane.",
        ),
    ]


def _build_followup_checkpoints() -> List[FollowupQueueCheckpoint]:
    return [
        FollowupQueueCheckpoint(
            checkpoint_id="followup_checkpoint_226_001",
            label="Follow-up queue items are preview-only",
            passed=True,
            result="passed",
            evidence_mode="safe_summary_only",
            writes_state=False,
        ),
        FollowupQueueCheckpoint(
            checkpoint_id="followup_checkpoint_226_002",
            label="Follow-up controls block assignment, status, due date, note, filter, and export writes",
            passed=True,
            result="passed",
            evidence_mode="blocked_action_summary",
            writes_state=False,
        ),
        FollowupQueueCheckpoint(
            checkpoint_id="followup_checkpoint_226_003",
            label="Raw evidence remains hidden",
            passed=True,
            result="passed",
            evidence_mode="redacted_pointer_only",
            writes_state=False,
        ),
        FollowupQueueCheckpoint(
            checkpoint_id="followup_checkpoint_226_004",
            label="Saved-view and owner review mutations remain blocked",
            passed=True,
            result="passed",
            evidence_mode="blocked_action_summary",
            writes_state=False,
        ),
        FollowupQueueCheckpoint(
            checkpoint_id="followup_checkpoint_226_005",
            label="Ready for Pack 227 follow-up detail drawer preview",
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
            "reason": "Pack 226 previews the follow-up queue only and cannot write follow-up, review, note, queue, saved-view, archive, evidence, or action state.",
        }
        for action in BLOCKED_REAL_ACTIONS
    ]


@lru_cache(maxsize=1)
def _build_receipt_chain_saved_view_owner_review_followup_queue_preview_cached() -> Dict[str, Any]:
    source_payload = _source_payload()

    followup_items_raw = _build_followup_items(source_payload)
    followup_lanes_raw = _build_followup_lanes(followup_items_raw)
    followup_controls_raw = _build_followup_controls()
    followup_checkpoints_raw = _build_followup_checkpoints()

    followup_items = [asdict(item) for item in followup_items_raw]
    followup_lanes = [asdict(lane) for lane in followup_lanes_raw]
    followup_controls = [asdict(control) for control in followup_controls_raw]
    followup_checkpoints = [asdict(checkpoint) for checkpoint in followup_checkpoints_raw]

    enabled_control_count = sum(1 for control in followup_controls if control["enabled"] is True)
    blocked_control_count = sum(1 for control in followup_controls if control["enabled"] is False)
    critical_item_count = sum(1 for item in followup_items if item["priority"] == "critical")
    high_item_count = sum(1 for item in followup_items if item["priority"] == "high")

    all_items_preview_only = all(item["owner_action_mode"] == "preview_only" for item in followup_items)
    all_items_non_executable = all(item["executable"] is False for item in followup_items)
    all_raw_evidence_hidden = all(item["raw_evidence_visible"] is False for item in followup_items)
    all_lanes_view_only = all(lane["action_mode"] == "view_only" for lane in followup_lanes)
    all_lanes_no_writes = all(lane["writes_state"] is False for lane in followup_lanes)
    all_controls_safe = all(control["result"] in {"preview_allowed", "blocked_preview_only"} for control in followup_controls)
    all_checkpoints_passed = all(checkpoint["passed"] is True for checkpoint in followup_checkpoints)
    all_checkpoints_no_writes = all(checkpoint["writes_state"] is False for checkpoint in followup_checkpoints)

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
        "receipt_chain_layer": "saved_view_owner_review_followup_queue_preview",
        "source_pack": source_payload.get("pack"),
        "source_endpoint": source_payload.get("endpoint"),
        "source_status": source_payload.get("status"),
        "source_readiness": source_payload.get("readiness"),
        "source_safe_to_continue": source_payload.get("safe_to_continue_to_pack_226"),
        "followup_queue_items": followup_items,
        "followup_queue_lanes": followup_lanes,
        "followup_queue_controls": followup_controls,
        "followup_queue_checkpoints": followup_checkpoints,
        "followup_queue_summary": {
            "followup_item_count": len(followup_items),
            "followup_lane_count": len(followup_lanes),
            "followup_control_count": len(followup_controls),
            "followup_checkpoint_count": len(followup_checkpoints),
            "enabled_control_count": enabled_control_count,
            "blocked_control_count": blocked_control_count,
            "critical_item_count": critical_item_count,
            "high_item_count": high_item_count,
            "all_items_preview_only": all_items_preview_only,
            "all_items_non_executable": all_items_non_executable,
            "all_raw_evidence_hidden": all_raw_evidence_hidden,
            "all_lanes_view_only": all_lanes_view_only,
            "all_lanes_no_writes": all_lanes_no_writes,
            "all_controls_safe": all_controls_safe,
            "all_checkpoints_passed": all_checkpoints_passed,
            "all_checkpoints_no_writes": all_checkpoints_no_writes,
            "followup_queue_ready": all([
                all_items_preview_only,
                all_items_non_executable,
                all_raw_evidence_hidden,
                all_lanes_view_only,
                all_lanes_no_writes,
                all_controls_safe,
                all_checkpoints_passed,
                all_checkpoints_no_writes,
            ]),
            "real_followup_assignment_enabled": False,
            "real_followup_status_write_enabled": False,
            "real_followup_due_date_write_enabled": False,
            "real_followup_note_write_enabled": False,
            "real_owner_review_write_enabled": False,
            "real_owner_note_write_enabled": False,
            "real_saved_view_mutation_enabled": False,
            "real_archive_write_enabled": False,
            "raw_evidence_visible": False,
            "real_action_execution_enabled": False,
        },
        "safety_invariants": {
            "no_real_followup_assignment_write": True,
            "no_real_followup_status_write": True,
            "no_real_followup_due_date_write": True,
            "no_real_followup_note_write": True,
            "no_real_owner_review_note_version_write": True,
            "no_real_owner_review_note_version_restore": True,
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
        "pack_226_acceptance": {
            "followup_queue_built": True,
            "followup_lanes_built": True,
            "followup_controls_built": True,
            "followup_write_actions_blocked": True,
            "ready_for_followup_detail_drawer": True,
        },
        SAFE_TO_CONTINUE_FLAG: True,
        NEXT_PREP_FLAG: {
            "pack": "227",
            "name": "Receipt Chain Saved View Owner Review Follow-up Detail Drawer Preview",
            "mode": "simulated_preview_only",
            "recommended_next_endpoint": "/tower/receipt-chain-saved-view-owner-review-followup-detail-drawer-v227.json",
            "save_batch": SAVE_BATCH,
            "save_after_pack": SAVE_AFTER_PACK,
        },
    }

    return preview


def build_receipt_chain_saved_view_owner_review_followup_queue_preview() -> Dict[str, Any]:
    """Return a defensive copy of the cached Pack 226 preview payload."""
    return deepcopy(_build_receipt_chain_saved_view_owner_review_followup_queue_preview_cached())


def build_pack_226_status_bridge() -> Dict[str, Any]:
    """Small cached status bridge for Tower cards/status surfaces."""
    preview = _build_receipt_chain_saved_view_owner_review_followup_queue_preview_cached()
    summary = preview["followup_queue_summary"]

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
        "followup_item_count": summary["followup_item_count"],
        "followup_lane_count": summary["followup_lane_count"],
        "followup_control_count": summary["followup_control_count"],
        "followup_queue_ready": summary["followup_queue_ready"],
        SAFE_TO_CONTINUE_FLAG: preview[SAFE_TO_CONTINUE_FLAG],
    }


def prepare_pack_227_receipt_chain_saved_view_owner_review_followup_detail_drawer() -> Dict[str, Any]:
    """Prepare Pack 227 direction without writing state."""
    return {
        "ready": True,
        "next_pack": "227",
        "name": "Receipt Chain Saved View Owner Review Follow-up Detail Drawer Preview",
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
    "build_receipt_chain_saved_view_owner_review_followup_queue_preview",
    "build_pack_226_status_bridge",
    "prepare_pack_227_receipt_chain_saved_view_owner_review_followup_detail_drawer",
]
