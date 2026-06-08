"""
SEARCHABLE LABEL: TOWER_PACK_219C_RECEIPT_CHAIN_SAVED_VIEW_COMPARE_FILTER_NAVIGATION_PREVIEW_MODULE

Pack 219C: Receipt Chain Saved View Compare Filter Navigation Preview

This module is intentionally simulated/preview-only.

Safety boundaries:
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

from tower.receipt_chain_saved_view_version_compare_v219b import (
    build_receipt_chain_saved_view_version_compare_preview,
)


PACK_ID = "219C"
PACK_NAME = "Receipt Chain Saved View Compare Filter Navigation Preview"
ENDPOINT = "/tower/receipt-chain-saved-view-compare-filter-navigation-v219c.json"

SAFE_TO_CONTINUE_FLAG = "safe_to_continue_to_pack_220"
NEXT_PREP_FLAG = "prepare_pack_220_saved_view_batch_close_readiness"

BLOCKED_REAL_ACTIONS = (
    "real_compare_filter_save",
    "real_compare_filter_apply",
    "real_compare_filter_delete",
    "real_compare_navigation_preference_write",
    "real_saved_view_restore",
    "real_saved_view_revert",
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
class CompareFilterPreset:
    filter_id: str
    label: str
    purpose: str
    criteria: Dict[str, Any]
    matching_compare_row_count: int
    enabled: bool
    saved_to_preferences: bool
    executable: bool


@dataclass(frozen=True)
class CompareNavigationLane:
    lane_id: str
    label: str
    target_anchor: str
    row_scope: str
    compare_pair_scope: str
    enabled: bool
    action_mode: str
    writes_preferences: bool


@dataclass(frozen=True)
class CompareFilterResultPreview:
    result_id: str
    filter_id: str
    compare_pair_id: str
    row_id: str
    field_name: str
    severity: str
    redaction_state: str
    owner_review_hint: str
    raw_evidence_visible: bool
    executable: bool


def _safe_compare_payload() -> Dict[str, Any]:
    return deepcopy(build_receipt_chain_saved_view_version_compare_preview())


def _source_rows() -> List[Dict[str, Any]]:
    return _safe_compare_payload().get("compare_rows", [])


def _source_pairs() -> List[Dict[str, Any]]:
    return _safe_compare_payload().get("compare_pairs", [])


def _match_rows(rows: List[Dict[str, Any]], *, severity: str | None = None, redaction_states: set[str] | None = None, change_types: set[str] | None = None) -> List[Dict[str, Any]]:
    matched = []
    for row in rows:
        if severity is not None and row.get("severity") != severity:
            continue
        if redaction_states is not None and row.get("redaction_state") not in redaction_states:
            continue
        if change_types is not None and row.get("change_type") not in change_types:
            continue
        matched.append(row)
    return matched


def _build_filter_presets(rows: List[Dict[str, Any]]) -> List[CompareFilterPreset]:
    return [
        CompareFilterPreset(
            filter_id="cmp_filter_219c_high_severity",
            label="High Severity Changes",
            purpose="Focus owner review on safety-critical compare differences.",
            criteria={"severity": "high"},
            matching_compare_row_count=len(_match_rows(rows, severity="high")),
            enabled=True,
            saved_to_preferences=False,
            executable=False,
        ),
        CompareFilterPreset(
            filter_id="cmp_filter_219c_redacted_only",
            label="Redacted Boundaries",
            purpose="Show compare rows where raw content remains hidden or summarized.",
            criteria={"redaction_state_in": ["redacted_pointer_only", "redacted_summary_only"]},
            matching_compare_row_count=len(
                _match_rows(rows, redaction_states={"redacted_pointer_only", "redacted_summary_only"})
            ),
            enabled=True,
            saved_to_preferences=False,
            executable=False,
        ),
        CompareFilterPreset(
            filter_id="cmp_filter_219c_safety_controls",
            label="Safety Control Changes",
            purpose="Show restore, revert, export, evidence, and execution boundary rows.",
            criteria={"change_type_in": ["safety_control_change", "evidence_boundary_change", "unchanged_safety_boundary"]},
            matching_compare_row_count=len(
                _match_rows(
                    rows,
                    change_types={
                        "safety_control_change",
                        "evidence_boundary_change",
                        "unchanged_safety_boundary",
                    },
                )
            ),
            enabled=True,
            saved_to_preferences=False,
            executable=False,
        ),
        CompareFilterPreset(
            filter_id="cmp_filter_219c_navigation_changes",
            label="Navigation Changes",
            purpose="Show rows that prepare the next compare-navigation layer.",
            criteria={"change_type_in": ["navigation_change", "layout_change", "summary_change"]},
            matching_compare_row_count=len(
                _match_rows(rows, change_types={"navigation_change", "layout_change", "summary_change"})
            ),
            enabled=True,
            saved_to_preferences=False,
            executable=False,
        ),
        CompareFilterPreset(
            filter_id="cmp_filter_219c_owner_notes",
            label="Owner Note Changes",
            purpose="Show owner note count and visibility changes without raw note reveal.",
            criteria={"change_type_in": ["owner_note_change"]},
            matching_compare_row_count=len(_match_rows(rows, change_types={"owner_note_change"})),
            enabled=True,
            saved_to_preferences=False,
            executable=False,
        ),
        CompareFilterPreset(
            filter_id="cmp_filter_219c_all_compare_rows",
            label="All Compare Rows",
            purpose="Show all compare rows for read-only review.",
            criteria={"scope": "all"},
            matching_compare_row_count=len(rows),
            enabled=True,
            saved_to_preferences=False,
            executable=False,
        ),
    ]


def _build_navigation_lanes(pairs: List[Dict[str, Any]]) -> List[CompareNavigationLane]:
    return [
        CompareNavigationLane(
            lane_id="cmp_nav_219c_pair_index",
            label="Compare Pair Index",
            target_anchor="compare_pairs",
            row_scope="all_rows",
            compare_pair_scope="all_pairs",
            enabled=True,
            action_mode="view_only",
            writes_preferences=False,
        ),
        CompareNavigationLane(
            lane_id="cmp_nav_219c_high_severity",
            label="High Severity Lane",
            target_anchor="high_severity_rows",
            row_scope="severity_high",
            compare_pair_scope="pairs_with_high_severity_rows",
            enabled=True,
            action_mode="view_only",
            writes_preferences=False,
        ),
        CompareNavigationLane(
            lane_id="cmp_nav_219c_redaction",
            label="Redaction Boundary Lane",
            target_anchor="redacted_rows",
            row_scope="redacted_pointer_or_summary",
            compare_pair_scope="pairs_with_redacted_rows",
            enabled=True,
            action_mode="view_only",
            writes_preferences=False,
        ),
        CompareNavigationLane(
            lane_id="cmp_nav_219c_safety_controls",
            label="Safety Controls Lane",
            target_anchor="safety_control_rows",
            row_scope="restore_revert_export_execution_boundaries",
            compare_pair_scope="pairs_with_safety_control_rows",
            enabled=True,
            action_mode="view_only",
            writes_preferences=False,
        ),
        CompareNavigationLane(
            lane_id="cmp_nav_219c_owner_notes",
            label="Owner Note Lane",
            target_anchor="owner_note_rows",
            row_scope="owner_note_summary_rows",
            compare_pair_scope="pairs_with_owner_note_rows",
            enabled=True,
            action_mode="view_only",
            writes_preferences=False,
        ),
        CompareNavigationLane(
            lane_id="cmp_nav_219c_current_vs_baseline",
            label="Baseline to Current",
            target_anchor="vcmp_219b_006",
            row_scope="baseline_to_current_rows",
            compare_pair_scope="vcmp_219b_006",
            enabled=any(pair.get("compare_pair_id") == "vcmp_219b_006" for pair in pairs),
            action_mode="view_only",
            writes_preferences=False,
        ),
    ]


def _build_filter_result_previews(rows: List[Dict[str, Any]]) -> List[CompareFilterResultPreview]:
    result_rows: List[CompareFilterResultPreview] = []

    filter_specs = {
        "cmp_filter_219c_high_severity": _match_rows(rows, severity="high"),
        "cmp_filter_219c_redacted_only": _match_rows(
            rows,
            redaction_states={"redacted_pointer_only", "redacted_summary_only"},
        ),
        "cmp_filter_219c_safety_controls": _match_rows(
            rows,
            change_types={"safety_control_change", "evidence_boundary_change", "unchanged_safety_boundary"},
        ),
        "cmp_filter_219c_navigation_changes": _match_rows(
            rows,
            change_types={"navigation_change", "layout_change", "summary_change"},
        ),
        "cmp_filter_219c_owner_notes": _match_rows(rows, change_types={"owner_note_change"}),
    }

    counter = 1
    for filter_id, matched_rows in filter_specs.items():
        for row in matched_rows:
            result_rows.append(
                CompareFilterResultPreview(
                    result_id=f"cmp_filter_result_219c_{counter:03d}",
                    filter_id=filter_id,
                    compare_pair_id=row["compare_pair_id"],
                    row_id=row["row_id"],
                    field_name=row["field_name"],
                    severity=row["severity"],
                    redaction_state=row["redaction_state"],
                    owner_review_hint=row["owner_review_hint"],
                    raw_evidence_visible=False,
                    executable=False,
                )
            )
            counter += 1

    return result_rows


def _blocked_action_matrix() -> List[Dict[str, Any]]:
    return [
        {
            "action": action,
            "allowed": False,
            "result": "blocked_preview_only",
            "reason": "Pack 219C previews compare filter/navigation only and cannot mutate state.",
        }
        for action in BLOCKED_REAL_ACTIONS
    ]


@lru_cache(maxsize=1)
def _build_receipt_chain_saved_view_compare_filter_navigation_preview_cached() -> Dict[str, Any]:
    source_payload = _safe_compare_payload()
    rows = source_payload.get("compare_rows", [])
    pairs = source_payload.get("compare_pairs", [])

    filter_presets = [asdict(item) for item in _build_filter_presets(rows)]
    navigation_lanes = [asdict(item) for item in _build_navigation_lanes(pairs)]
    filter_results = [asdict(item) for item in _build_filter_result_previews(rows)]

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
        "receipt_chain_layer": "saved_view_compare_filter_navigation_preview",
        "source_pack": source_payload.get("pack"),
        "source_endpoint": source_payload.get("endpoint"),
        "source_status": source_payload.get("status"),
        "source_readiness": source_payload.get("readiness"),
        "source_safe_to_continue": source_payload.get("safe_to_continue_to_pack_219C"),
        "source_boundary": {
            "inherits_from_pack_219B": "saved_view_version_compare_preview",
            "writes_any_filter_preset": False,
            "applies_any_filter_preset": False,
            "deletes_any_filter_preset": False,
            "writes_any_navigation_preference": False,
            "writes_any_saved_view": False,
            "restores_any_saved_view": False,
            "reverts_any_saved_view": False,
            "writes_any_user_preference": False,
            "writes_any_archive": False,
            "reveals_raw_evidence": False,
            "executes_any_real_action": False,
        },
        "compare_filter_navigation_summary": {
            "filter_preset_count": len(filter_presets),
            "navigation_lane_count": len(navigation_lanes),
            "filter_result_preview_count": len(filter_results),
            "source_compare_pair_count": len(pairs),
            "source_compare_row_count": len(rows),
            "enabled_filter_count": sum(1 for item in filter_presets if item["enabled"] is True),
            "saved_filter_count": sum(1 for item in filter_presets if item["saved_to_preferences"] is True),
            "enabled_navigation_lane_count": sum(1 for item in navigation_lanes if item["enabled"] is True),
            "preference_write_enabled": False,
            "filter_apply_enabled": False,
            "filter_save_enabled": False,
            "filter_delete_enabled": False,
            "raw_evidence_visible": False,
            "real_action_execution_enabled": False,
        },
        "filter_presets": filter_presets,
        "navigation_lanes": navigation_lanes,
        "filter_result_previews": filter_results,
        "filter_controls": {
            "filter_selector_enabled": True,
            "filter_preview_button_enabled": True,
            "filter_apply_button_visible": True,
            "filter_apply_button_enabled": False,
            "save_filter_button_visible": True,
            "save_filter_button_enabled": False,
            "delete_filter_button_visible": True,
            "delete_filter_button_enabled": False,
            "remember_navigation_button_visible": True,
            "remember_navigation_button_enabled": False,
            "export_filtered_compare_button_visible": True,
            "export_filtered_compare_button_enabled": False,
            "control_mode": "preview_only",
        },
        "safety_invariants": {
            "no_real_compare_filter_save": True,
            "no_real_compare_filter_apply": True,
            "no_real_compare_filter_delete": True,
            "no_real_compare_navigation_preference_write": True,
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
            "all_filter_presets_non_executable": all(item["executable"] is False for item in filter_presets),
            "all_filter_results_non_executable": all(item["executable"] is False for item in filter_results),
            "all_navigation_lanes_view_only": all(item["action_mode"] == "view_only" for item in navigation_lanes),
            "cached_non_recursive_builder": True,
        },
        "blocked_action_matrix": _blocked_action_matrix(),
        "route_contract": {
            "method": "GET",
            "returns_json": True,
            "requires_tower_guard": True,
            "unguarded_high_risk_allowed": False,
        },
        "pack_219c_acceptance": {
            "filter_presets_built": True,
            "navigation_lanes_built": True,
            "filter_result_previews_built": True,
            "filter_save_apply_delete_blocked": True,
            "navigation_preference_write_blocked": True,
            "ready_for_batch_close_readiness": True,
        },
        NEXT_PREP_FLAG: {
            "pack": "220",
            "name": "Receipt Chain Saved View Batch Close Readiness Preview",
            "mode": "simulated_preview_only",
            "recommended_next_endpoint": "/tower/receipt-chain-saved-view-batch-close-readiness-v220.json",
            "save_batch": "216-220",
            "save_after_pack": 220,
        },
        SAFE_TO_CONTINUE_FLAG: True,
    }

    return preview


def build_receipt_chain_saved_view_compare_filter_navigation_preview() -> Dict[str, Any]:
    """Return a defensive copy of the cached Pack 219C preview payload."""
    return deepcopy(_build_receipt_chain_saved_view_compare_filter_navigation_preview_cached())


def build_pack_219c_status_bridge() -> Dict[str, Any]:
    """Small cached status bridge for Tower cards/status surfaces."""
    preview = _build_receipt_chain_saved_view_compare_filter_navigation_preview_cached()
    summary = preview["compare_filter_navigation_summary"]

    return {
        "pack": preview["pack"],
        "pack_name": preview["pack_name"],
        "status": preview["status"],
        "readiness": preview["readiness"],
        "endpoint": preview["endpoint"],
        "cached": preview["cached"],
        "non_recursive": preview["non_recursive"],
        "preview_only": preview["preview_only"],
        "source_pack": preview["source_pack"],
        "source_status": preview["source_status"],
        "filter_preset_count": summary["filter_preset_count"],
        "navigation_lane_count": summary["navigation_lane_count"],
        "filter_result_preview_count": summary["filter_result_preview_count"],
        SAFE_TO_CONTINUE_FLAG: preview[SAFE_TO_CONTINUE_FLAG],
    }


def prepare_pack_220_saved_view_batch_close_readiness() -> Dict[str, Any]:
    """Prepare Pack 220 batch-close readiness without writing state."""
    return {
        "ready": True,
        "next_pack": "220",
        "name": "Receipt Chain Saved View Batch Close Readiness Preview",
        "mode": "simulated_preview_only",
        "source_pack": PACK_ID,
        "source_endpoint": ENDPOINT,
        "save_batch": "216-220",
        "save_after_pack": 220,
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
    "build_receipt_chain_saved_view_compare_filter_navigation_preview",
    "build_pack_219c_status_bridge",
    "prepare_pack_220_saved_view_batch_close_readiness",
]
