"""
SEARCHABLE LABEL: TOWER_PACK_219A_RECEIPT_CHAIN_SAVED_VIEW_HISTORY_PREVIEW_MODULE

Pack 219A: Receipt Chain Saved View History Preview

This module is intentionally simulated/preview-only.

Safety boundaries:
- No real saved-view write/edit/delete/apply/export.
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


PACK_ID = "219A"
PACK_NAME = "Receipt Chain Saved View History Preview"
ENDPOINT = "/tower/receipt-chain-saved-view-history-v219a.json"

SAFE_TO_CONTINUE_FLAG = "safe_to_continue_to_pack_219B"
NEXT_PREP_FLAG = "prepare_pack_219B_saved_view_version_compare"

BLOCKED_REAL_ACTIONS = (
    "real_saved_view_write",
    "real_saved_view_edit",
    "real_saved_view_delete",
    "real_saved_view_apply",
    "real_saved_view_export",
    "real_user_preference_write",
    "real_archive_write",
    "raw_evidence_reveal",
    "real_action_execution",
    "live_policy_mutation",
    "receipt_chain_mutation",
)


@dataclass(frozen=True)
class SavedViewHistoryEvent:
    event_id: str
    version_id: str
    event_type: str
    actor_scope: str
    simulated_at: str
    summary: str
    safety_result: str
    evidence_mode: str


@dataclass(frozen=True)
class SavedViewVersionCard:
    version_id: str
    label: str
    status: str
    simulated_timestamp: str
    changed_field_count: int
    receipt_pointer_count: int
    owner_note_count: int
    restore_mode: str
    raw_evidence_visible: bool


@dataclass(frozen=True)
class FieldChangePreview:
    row_id: str
    version_id: str
    field_name: str
    previous_preview: str
    current_preview: str
    change_type: str
    redaction_state: str
    executable: bool


def _history_events() -> List[SavedViewHistoryEvent]:
    return [
        SavedViewHistoryEvent(
            event_id="svh_219a_001",
            version_id="sv_v218_001",
            event_type="created_preview",
            actor_scope="tower.system.preview",
            simulated_at="2026-06-08T00:00:00Z",
            summary="Initial saved-view edit preview baseline was prepared from Pack 218 output.",
            safety_result="preview_only",
            evidence_mode="receipt_pointer_only",
        ),
        SavedViewHistoryEvent(
            event_id="svh_219a_002",
            version_id="sv_v218_002",
            event_type="filter_adjusted_preview",
            actor_scope="owner.review.preview",
            simulated_at="2026-06-08T00:03:00Z",
            summary="Containment severity filter preview changed from all severities to high and critical.",
            safety_result="preview_only",
            evidence_mode="receipt_pointer_only",
        ),
        SavedViewHistoryEvent(
            event_id="svh_219a_003",
            version_id="sv_v218_003",
            event_type="sort_adjusted_preview",
            actor_scope="owner.review.preview",
            simulated_at="2026-06-08T00:06:00Z",
            summary="Sort preview changed to newest receipt-chain event first.",
            safety_result="preview_only",
            evidence_mode="receipt_pointer_only",
        ),
        SavedViewHistoryEvent(
            event_id="svh_219a_004",
            version_id="sv_v218_004",
            event_type="drawer_layout_preview",
            actor_scope="owner.review.preview",
            simulated_at="2026-06-08T00:09:00Z",
            summary="Drawer layout preview emphasized containment status, owner notes, and receipt pointers.",
            safety_result="preview_only",
            evidence_mode="receipt_pointer_only",
        ),
        SavedViewHistoryEvent(
            event_id="svh_219a_005",
            version_id="sv_v218_005",
            event_type="owner_note_preview",
            actor_scope="owner.review.preview",
            simulated_at="2026-06-08T00:12:00Z",
            summary="Owner note draft preview was linked to saved-view version metadata without writing notes.",
            safety_result="preview_only",
            evidence_mode="receipt_pointer_only",
        ),
        SavedViewHistoryEvent(
            event_id="svh_219a_006",
            version_id="sv_v218_006",
            event_type="history_checkpoint_preview",
            actor_scope="tower.system.preview",
            simulated_at="2026-06-08T00:15:00Z",
            summary="History checkpoint preview confirms version navigation can proceed without mutation.",
            safety_result="preview_only",
            evidence_mode="receipt_pointer_only",
        ),
    ]


def _version_cards() -> List[SavedViewVersionCard]:
    return [
        SavedViewVersionCard(
            version_id="sv_v218_001",
            label="Baseline edit preview",
            status="available_preview",
            simulated_timestamp="2026-06-08T00:00:00Z",
            changed_field_count=0,
            receipt_pointer_count=8,
            owner_note_count=0,
            restore_mode="disabled_preview_only",
            raw_evidence_visible=False,
        ),
        SavedViewVersionCard(
            version_id="sv_v218_002",
            label="Severity filter preview",
            status="available_preview",
            simulated_timestamp="2026-06-08T00:03:00Z",
            changed_field_count=3,
            receipt_pointer_count=9,
            owner_note_count=0,
            restore_mode="disabled_preview_only",
            raw_evidence_visible=False,
        ),
        SavedViewVersionCard(
            version_id="sv_v218_003",
            label="Newest-first sort preview",
            status="available_preview",
            simulated_timestamp="2026-06-08T00:06:00Z",
            changed_field_count=2,
            receipt_pointer_count=9,
            owner_note_count=0,
            restore_mode="disabled_preview_only",
            raw_evidence_visible=False,
        ),
        SavedViewVersionCard(
            version_id="sv_v218_004",
            label="Drawer layout preview",
            status="available_preview",
            simulated_timestamp="2026-06-08T00:09:00Z",
            changed_field_count=5,
            receipt_pointer_count=10,
            owner_note_count=0,
            restore_mode="disabled_preview_only",
            raw_evidence_visible=False,
        ),
        SavedViewVersionCard(
            version_id="sv_v218_005",
            label="Owner note link preview",
            status="available_preview",
            simulated_timestamp="2026-06-08T00:12:00Z",
            changed_field_count=4,
            receipt_pointer_count=10,
            owner_note_count=2,
            restore_mode="disabled_preview_only",
            raw_evidence_visible=False,
        ),
        SavedViewVersionCard(
            version_id="sv_v218_006",
            label="History checkpoint preview",
            status="current_preview",
            simulated_timestamp="2026-06-08T00:15:00Z",
            changed_field_count=6,
            receipt_pointer_count=12,
            owner_note_count=2,
            restore_mode="disabled_preview_only",
            raw_evidence_visible=False,
        ),
    ]


def _field_change_rows() -> List[FieldChangePreview]:
    return [
        FieldChangePreview(
            row_id="fcp_219a_001",
            version_id="sv_v218_002",
            field_name="severity_filter",
            previous_preview="all",
            current_preview="high, critical",
            change_type="filter_preview",
            redaction_state="safe_preview",
            executable=False,
        ),
        FieldChangePreview(
            row_id="fcp_219a_002",
            version_id="sv_v218_002",
            field_name="containment_state_filter",
            previous_preview="all",
            current_preview="quarantine, fail_closed, step_up_required",
            change_type="filter_preview",
            redaction_state="safe_preview",
            executable=False,
        ),
        FieldChangePreview(
            row_id="fcp_219a_003",
            version_id="sv_v218_003",
            field_name="sort_order",
            previous_preview="oldest_first",
            current_preview="newest_first",
            change_type="sort_preview",
            redaction_state="safe_preview",
            executable=False,
        ),
        FieldChangePreview(
            row_id="fcp_219a_004",
            version_id="sv_v218_004",
            field_name="drawer_primary_section",
            previous_preview="receipt summary",
            current_preview="containment status",
            change_type="layout_preview",
            redaction_state="safe_preview",
            executable=False,
        ),
        FieldChangePreview(
            row_id="fcp_219a_005",
            version_id="sv_v218_004",
            field_name="drawer_secondary_section",
            previous_preview="policy decision trace",
            current_preview="owner notes and receipt pointers",
            change_type="layout_preview",
            redaction_state="safe_preview",
            executable=False,
        ),
        FieldChangePreview(
            row_id="fcp_219a_006",
            version_id="sv_v218_005",
            field_name="owner_note_visibility",
            previous_preview="hidden",
            current_preview="preview summary only",
            change_type="owner_note_preview",
            redaction_state="redacted_summary_only",
            executable=False,
        ),
        FieldChangePreview(
            row_id="fcp_219a_007",
            version_id="sv_v218_006",
            field_name="history_navigation",
            previous_preview="single edit card",
            current_preview="version timeline plus compare-ready rows",
            change_type="navigation_preview",
            redaction_state="safe_preview",
            executable=False,
        ),
    ]


def _blocked_action_matrix() -> List[Dict[str, Any]]:
    return [
        {
            "action": action,
            "allowed": False,
            "result": "blocked_preview_only",
            "reason": "Pack 219A is a simulated saved-view history preview and cannot mutate state.",
        }
        for action in BLOCKED_REAL_ACTIONS
    ]


def _owner_review_lanes() -> List[Dict[str, Any]]:
    return [
        {
            "lane_id": "owner_review_lane_219a_history",
            "label": "History timeline",
            "purpose": "Show saved-view version events without applying or restoring them.",
            "action_mode": "view_only",
            "cached": True,
        },
        {
            "lane_id": "owner_review_lane_219a_field_changes",
            "label": "Field change preview",
            "purpose": "Show redacted changed-field rows for later compare previews.",
            "action_mode": "view_only",
            "cached": True,
        },
        {
            "lane_id": "owner_review_lane_219a_safety",
            "label": "Safety lock preview",
            "purpose": "Confirm restore, revert, export, archive write, and preference write are disabled.",
            "action_mode": "view_only",
            "cached": True,
        },
    ]


def _navigation_cards() -> List[Dict[str, Any]]:
    return [
        {
            "nav_id": "nav_219a_saved_view_history",
            "label": "Saved View History",
            "target_endpoint": ENDPOINT,
            "enabled": True,
            "mode": "preview_only",
        },
        {
            "nav_id": "nav_219a_version_cards",
            "label": "Version Cards",
            "target_endpoint": ENDPOINT,
            "enabled": True,
            "mode": "preview_only",
        },
        {
            "nav_id": "nav_219a_compare_ready",
            "label": "Compare Ready Rows",
            "target_endpoint": ENDPOINT,
            "enabled": True,
            "mode": "preview_only",
        },
        {
            "nav_id": "nav_219a_restore_disabled",
            "label": "Restore Disabled",
            "target_endpoint": ENDPOINT,
            "enabled": False,
            "mode": "blocked_preview_only",
        },
    ]


@lru_cache(maxsize=1)
def _build_receipt_chain_saved_view_history_preview_cached() -> Dict[str, Any]:
    history_events = [asdict(event) for event in _history_events()]
    version_cards = [asdict(card) for card in _version_cards()]
    field_change_rows = [asdict(row) for row in _field_change_rows()]

    preview = {
        "pack": PACK_ID,
        "pack_name": PACK_NAME,
        "status": "ready",
        "readiness": 100,
        "endpoint": ENDPOINT,
        "cached": True,
        "non_recursive": True,
        "simulation_only": True,
        "preview_only": True,
        "receipt_chain_layer": "saved_view_history_preview",
        "source_boundary": {
            "inherits_from_pack_216": "saved_view_presets_preview",
            "inherits_from_pack_217": "saved_view_detail_preview",
            "inherits_from_pack_218": "saved_view_edit_preview",
            "writes_any_saved_view": False,
            "writes_any_user_preference": False,
            "writes_any_archive": False,
            "reveals_raw_evidence": False,
            "executes_any_real_action": False,
        },
        "saved_view_history_summary": {
            "history_event_count": len(history_events),
            "version_card_count": len(version_cards),
            "field_change_preview_count": len(field_change_rows),
            "current_preview_version_id": "sv_v218_006",
            "restore_enabled": False,
            "revert_enabled": False,
            "export_enabled": False,
            "apply_enabled": False,
            "delete_enabled": False,
        },
        "history_events": history_events,
        "version_cards": version_cards,
        "field_change_preview_rows": field_change_rows,
        "owner_review_lanes": _owner_review_lanes(),
        "navigation_cards": _navigation_cards(),
        "restore_revert_simulation": {
            "restore_button_visible": True,
            "restore_button_enabled": False,
            "restore_result": "blocked_preview_only",
            "revert_button_visible": True,
            "revert_button_enabled": False,
            "revert_result": "blocked_preview_only",
            "reason": "Pack 219A may preview version history but cannot restore or mutate saved views.",
        },
        "safety_invariants": {
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
        "pack_219a_acceptance": {
            "history_preview_built": True,
            "version_preview_built": True,
            "field_change_preview_built": True,
            "blocked_mutation_actions_verified": True,
            "ready_for_version_compare_preview": True,
        },
        NEXT_PREP_FLAG: {
            "pack": "219B",
            "name": "Receipt Chain Saved View Version Compare Preview",
            "mode": "simulated_preview_only",
            "recommended_next_endpoint": "/tower/receipt-chain-saved-view-version-compare-v219b.json",
        },
        SAFE_TO_CONTINUE_FLAG: True,
    }

    return preview


def build_receipt_chain_saved_view_history_preview() -> Dict[str, Any]:
    """Return a defensive copy of the cached Pack 219A preview payload."""
    return deepcopy(_build_receipt_chain_saved_view_history_preview_cached())


def build_pack_219a_status_bridge() -> Dict[str, Any]:
    """Small cached status bridge for Tower cards/status surfaces."""
    preview = _build_receipt_chain_saved_view_history_preview_cached()
    return {
        "pack": preview["pack"],
        "pack_name": preview["pack_name"],
        "status": preview["status"],
        "readiness": preview["readiness"],
        "endpoint": preview["endpoint"],
        "cached": preview["cached"],
        "non_recursive": preview["non_recursive"],
        "preview_only": preview["preview_only"],
        "history_event_count": preview["saved_view_history_summary"]["history_event_count"],
        "version_card_count": preview["saved_view_history_summary"]["version_card_count"],
        "field_change_preview_count": preview["saved_view_history_summary"]["field_change_preview_count"],
        SAFE_TO_CONTINUE_FLAG: preview[SAFE_TO_CONTINUE_FLAG],
    }


def prepare_pack_219B_saved_view_version_compare() -> Dict[str, Any]:
    """Prepare the next preview-only pack direction without writing state."""
    return {
        "ready": True,
        "next_pack": "219B",
        "name": "Receipt Chain Saved View Version Compare Preview",
        "mode": "simulated_preview_only",
        "source_pack": PACK_ID,
        "source_endpoint": ENDPOINT,
        "blocked_real_actions": list(BLOCKED_REAL_ACTIONS),
        "safe_to_continue": True,
    }


__all__ = [
    "PACK_ID",
    "PACK_NAME",
    "ENDPOINT",
    "SAFE_TO_CONTINUE_FLAG",
    "NEXT_PREP_FLAG",
    "BLOCKED_REAL_ACTIONS",
    "build_receipt_chain_saved_view_history_preview",
    "build_pack_219a_status_bridge",
    "prepare_pack_219B_saved_view_version_compare",
]
