
"""
PACK 190 - Owner Note Saved View Preset Detail Edit History Version Compare
Saved View / Filter Preset Detail Edit History Version Compare Navigation
Saved View / Filter Preset Detail Edit Preview.

This module sits on top of Pack 189.

Pack 189 creates preview-only saved view/filter presets for version compare navigation.
Pack 190 creates preview-only detail edit drawers for those saved view/filter presets:
- saved view preset detail edit drawers
- filter preset detail edit drawers
- editable field preview rows
- original vs preview snapshots
- indexes
- blocked saved view/user preference/filter/navigation/drawer/edit persistence

Important:
- simulated-only
- detail-edit-preview-only
- saved-view-preview-only
- filter-preset-preview-only
- navigation-preview-only
- filter-navigation-preview-only
- no real saved view written
- no real user preference written
- no real filter preference saved
- no real navigation state persisted
- no real drawer selection saved
- no real edit persisted
- cached
- non-recursive
"""

from __future__ import annotations

import copy
import datetime
import hashlib
import importlib
from functools import lru_cache
from typing import Any, Dict, List


PACK_ID = "PACK_190"
DETAIL_EDIT_ENDPOINT = "/tower/policy-change-approval-receipt-owner-note-saved-view-preset-detail-edit-history-version-compare-saved-view-filter-preset-detail-edit-history-version-compare-navigation-saved-view-filter-preset-detail-edit-preview.json"
SOURCE_ENDPOINT = "/tower/policy-change-approval-receipt-owner-note-saved-view-preset-detail-edit-history-version-compare-saved-view-filter-preset-detail-edit-history-version-compare-navigation-saved-view-filter-preset.json"


SAVED_VIEW_FIELDS = [
    {"field_id": "label", "field_label": "Label", "field_type": "text"},
    {"field_id": "description", "field_label": "Description", "field_type": "textarea"},
    {"field_id": "filter_lane_id", "field_label": "Filter Lane", "field_type": "select"},
    {"field_id": "view_priority", "field_label": "View Priority", "field_type": "select"},
    {"field_id": "is_default", "field_label": "Default View", "field_type": "boolean"},
]

FILTER_PRESET_FIELDS = [
    {"field_id": "label", "field_label": "Label", "field_type": "text"},
    {"field_id": "filter_lane_id", "field_label": "Filter Lane", "field_type": "readonly_text"},
    {"field_id": "filter_type", "field_label": "Filter Type", "field_type": "readonly_text"},
    {"field_id": "matched_navigation_item_count", "field_label": "Matched Items", "field_type": "readonly_number"},
    {"field_id": "default_selected_version_detail_drawer_id", "field_label": "Default Drawer", "field_type": "readonly_text"},
]


def _utc_now() -> str:
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def _stable_hash(value: Any, length: int = 18) -> str:
    raw = repr(value).encode("utf-8", errors="ignore")
    return hashlib.sha256(raw).hexdigest()[:length]


def _safe_text(value: Any) -> str:
    text = str(value or "")
    lowered = text.lower()
    forbidden = [
        "sk_live_",
        "sk_test_",
        "github_pat_",
        "ghp_",
        "xoxb-",
        "aws_secret_access_key",
        "private_key-----",
        "broker_token_value",
        "api_secret_value",
    ]
    return "[REDACTED]" if any(fragment in lowered for fragment in forbidden) else text


def _base_flags() -> Dict[str, object]:
    return {
        "simulated_only": True,
        "detail_edit_preview_only": True,
        "saved_view_preview_only": True,
        "filter_preset_preview_only": True,
        "navigation_preview_only": True,
        "filter_navigation_preview_only": True,
        "version_detail_preview_only": True,
        "compare_view_preview_only": True,
        "edit_history_preview_only": True,
        "version_preview_only": True,
        "rollback_preview_only": True,
        "restore_preview_only": True,
        "compare_preview_only": True,
        "saved_view_preset_detail_preview_only": True,
        "saved_view_preset_edit_preview_only": True,
        "saved_navigation_preview_only": True,
        "saved_filter_preset_preview_only": True,
        "navigation_persistence_allowed_now": False,
        "filter_preference_save_allowed_now": False,
        "drawer_selection_save_allowed_now": False,
        "saved_view_write_allowed_now": False,
        "user_preference_write_allowed_now": False,
        "restore_allowed_now": False,
        "rollback_allowed_now": False,
        "save_allowed_now": False,
        "persist_allowed_now": False,
        "history_write_allowed_now": False,
        "version_write_allowed_now": False,
        "version_save_allowed_now": False,
        "raw_evidence_reveal_allowed": False,
        "raw_evidence_lookup_allowed": False,
        "real_saved_view_written": False,
        "real_user_preference_written": False,
        "real_filter_preference_saved": False,
        "real_navigation_state_persisted": False,
        "real_drawer_selection_saved": False,
        "real_history_written": False,
        "real_version_written": False,
        "real_version_saved": False,
        "real_rollback_executed": False,
        "real_restore_executed": False,
        "real_edit_persisted": False,
        "cached_non_recursive": True,
    }


def _load_pack_189_payload(force_refresh: bool = False) -> Dict[str, object]:
    try:
        mod = importlib.import_module(
            "tower.policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset"
        )
        fn = getattr(
            mod,
            "build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_payload",
            None,
        )
        if callable(fn):
            payload = fn(force_refresh=force_refresh)
            if isinstance(payload, dict):
                return payload
    except Exception as exc:
        return {
            "pack_id": "PACK_189",
            "status": "review",
            "endpoint": SOURCE_ENDPOINT,
            "summary": {
                "saved_view_preset_count": 0,
                "filter_preset_count": 0,
                "readiness_score": 0,
            },
            "saved_view_presets": [],
            "filter_presets": [],
            "load_error": str(exc),
            **_base_flags(),
        }

    return {
        "pack_id": "PACK_189",
        "status": "review",
        "endpoint": SOURCE_ENDPOINT,
        "summary": {
            "saved_view_preset_count": 0,
            "filter_preset_count": 0,
            "readiness_score": 0,
        },
        "saved_view_presets": [],
        "filter_presets": [],
        **_base_flags(),
    }


def _display_value(value: Any) -> str:
    if isinstance(value, bool):
        return "Yes" if value else "No"
    if value is None:
        return ""
    if isinstance(value, list):
        return f"{len(value)} items"
    if isinstance(value, dict):
        return f"{len(value)} keys"
    return _safe_text(value)


def _preview_value_for_saved_view(preset: Dict[str, object], field_id: str) -> Any:
    current = preset.get(field_id)

    if field_id == "label":
        return f"{_safe_text(current)} · Preview"
    if field_id == "description":
        return f"{_safe_text(current)} Preview-only detail edit draft."
    if field_id == "filter_lane_id":
        return current
    if field_id == "view_priority":
        priority = _safe_text(current)
        return "high" if priority in {"medium", "monitor"} else priority
    if field_id == "is_default":
        return bool(current)

    return current


def _preview_value_for_filter_preset(preset: Dict[str, object], field_id: str) -> Any:
    current = preset.get(field_id)

    if field_id == "label":
        return f"{_safe_text(current)} · Preview"
    return current


def _build_editable_row(
    source_kind: str,
    source_id: str,
    drawer_id: str,
    field_def: Dict[str, object],
    current_value: Any,
    preview_value: Any,
    sequence: int,
) -> Dict[str, object]:
    field_id = field_def["field_id"]
    changed = current_value != preview_value

    row = {
        "editable_field_row_id": f"version_compare_navigation_saved_view_filter_detail_edit_row_{_stable_hash((source_kind, source_id, drawer_id, field_id, sequence), 18)}",
        "source_kind": source_kind,
        "source_id": source_id,
        "drawer_id": drawer_id,
        "field_id": field_id,
        "field_label": field_def["field_label"],
        "field_type": field_def["field_type"],
        "sequence": int(sequence),
        "current_value": {
            "value": current_value,
            "display_value": _display_value(current_value),
        },
        "preview_value": {
            "value": preview_value,
            "display_value": _display_value(preview_value),
        },
        "changed": bool(changed),
        "row_status": "version_compare_navigation_saved_view_filter_detail_edit_row_preview_ready",
        "row_result_type": "owner_note_version_compare_navigation_saved_view_filter_detail_edit_row_preview",
        "safe_preview_only": True,
    }
    row.update(_base_flags())
    return row


def _snapshot_from_rows(rows: List[Dict[str, object]], side: str) -> Dict[str, object]:
    snapshot = {}
    value_key = "current_value" if side == "current" else "preview_value"
    for row in rows:
        if isinstance(row, dict):
            value_payload = row.get(value_key, {})
            snapshot[row.get("field_id")] = value_payload.get("value") if isinstance(value_payload, dict) else value_payload
    return snapshot


def _build_saved_view_detail_drawer(preset: Dict[str, object], sequence: int) -> Dict[str, object]:
    source_id = _safe_text(preset.get("saved_view_preset_id"))
    drawer_id = f"version_compare_navigation_saved_view_preset_detail_edit_drawer_{_stable_hash((PACK_ID, source_id, sequence), 18)}"

    rows = []
    for idx, field_def in enumerate(SAVED_VIEW_FIELDS, start=1):
        field_id = field_def["field_id"]
        current = preset.get(field_id)
        preview = _preview_value_for_saved_view(preset, field_id)
        rows.append(
            _build_editable_row(
                source_kind="saved_view_preset",
                source_id=source_id,
                drawer_id=drawer_id,
                field_def=field_def,
                current_value=current,
                preview_value=preview,
                sequence=idx,
            )
        )

    changed_rows = [row for row in rows if row.get("changed") is True]
    unchanged_rows = [row for row in rows if row.get("changed") is False]

    drawer = {
        "detail_edit_drawer_id": drawer_id,
        "source_kind": "saved_view_preset",
        "source_id": source_id,
        "saved_view_preset_id": source_id,
        "saved_view_preset_preview_id": preset.get("saved_view_preset_preview_id"),
        "filter_lane_id": preset.get("filter_lane_id"),
        "linked_filter_preset_id": preset.get("linked_filter_preset_id"),
        "label": preset.get("label"),
        "view_priority": preset.get("view_priority"),
        "is_default": preset.get("is_default"),
        "sequence": int(sequence),
        "editable_field_rows": rows,
        "editable_field_row_count": len(rows),
        "changed_field_count": len(changed_rows),
        "unchanged_field_count": len(unchanged_rows),
        "original_snapshot": _snapshot_from_rows(rows, "current"),
        "preview_edit_snapshot": _snapshot_from_rows(rows, "preview"),
        "drawer_status": "version_compare_navigation_saved_view_preset_detail_edit_drawer_preview_ready",
        "drawer_result_type": "owner_note_version_compare_navigation_saved_view_preset_detail_edit_drawer_preview",
        "safe_preview_only": True,
    }
    drawer.update(_base_flags())
    return drawer


def _build_filter_preset_detail_drawer(preset: Dict[str, object], sequence: int) -> Dict[str, object]:
    source_id = _safe_text(preset.get("filter_preset_id"))
    drawer_id = f"version_compare_navigation_filter_preset_detail_edit_drawer_{_stable_hash((PACK_ID, source_id, sequence), 18)}"

    rows = []
    for idx, field_def in enumerate(FILTER_PRESET_FIELDS, start=1):
        field_id = field_def["field_id"]
        current = preset.get(field_id)
        preview = _preview_value_for_filter_preset(preset, field_id)
        rows.append(
            _build_editable_row(
                source_kind="filter_preset",
                source_id=source_id,
                drawer_id=drawer_id,
                field_def=field_def,
                current_value=current,
                preview_value=preview,
                sequence=idx,
            )
        )

    changed_rows = [row for row in rows if row.get("changed") is True]
    unchanged_rows = [row for row in rows if row.get("changed") is False]

    drawer = {
        "detail_edit_drawer_id": drawer_id,
        "source_kind": "filter_preset",
        "source_id": source_id,
        "filter_preset_id": source_id,
        "filter_lane_id": preset.get("filter_lane_id"),
        "label": preset.get("label"),
        "filter_type": preset.get("filter_type"),
        "sequence": int(sequence),
        "editable_field_rows": rows,
        "editable_field_row_count": len(rows),
        "changed_field_count": len(changed_rows),
        "unchanged_field_count": len(unchanged_rows),
        "original_snapshot": _snapshot_from_rows(rows, "current"),
        "preview_edit_snapshot": _snapshot_from_rows(rows, "preview"),
        "drawer_status": "version_compare_navigation_filter_preset_detail_edit_drawer_preview_ready",
        "drawer_result_type": "owner_note_version_compare_navigation_filter_preset_detail_edit_drawer_preview",
        "safe_preview_only": True,
    }
    drawer.update(_base_flags())
    return drawer


def _build_indexes(saved_view_drawers: List[Dict[str, object]], filter_preset_drawers: List[Dict[str, object]]) -> Dict[str, object]:
    all_drawers = saved_view_drawers + filter_preset_drawers
    indexes = {
        "drawers_by_id": {},
        "drawers_by_source_kind": {},
        "drawers_by_source_id": {},
        "saved_view_drawers_by_preset_id": {},
        "saved_view_drawers_by_filter_lane_id": {},
        "saved_view_drawers_by_priority": {},
        "filter_preset_drawers_by_preset_id": {},
        "filter_preset_drawers_by_filter_lane_id": {},
        "editable_rows_by_id": {},
        "editable_rows_by_drawer_id": {},
        "editable_rows_by_source_kind": {},
        "editable_rows_by_field_id": {},
        "changed_rows_by_drawer_id": {},
    }

    for drawer in all_drawers:
        drawer_id = drawer.get("detail_edit_drawer_id")
        source_kind = drawer.get("source_kind")
        source_id = drawer.get("source_id")

        indexes["drawers_by_id"][drawer_id] = drawer
        indexes["drawers_by_source_kind"].setdefault(source_kind, []).append(drawer)
        indexes["drawers_by_source_id"][source_id] = drawer

        if source_kind == "saved_view_preset":
            indexes["saved_view_drawers_by_preset_id"][drawer.get("saved_view_preset_id")] = drawer
            indexes["saved_view_drawers_by_filter_lane_id"].setdefault(drawer.get("filter_lane_id"), []).append(drawer)
            indexes["saved_view_drawers_by_priority"].setdefault(drawer.get("view_priority"), []).append(drawer)
        elif source_kind == "filter_preset":
            indexes["filter_preset_drawers_by_preset_id"][drawer.get("filter_preset_id")] = drawer
            indexes["filter_preset_drawers_by_filter_lane_id"].setdefault(drawer.get("filter_lane_id"), []).append(drawer)

        for row in drawer.get("editable_field_rows", []):
            if not isinstance(row, dict):
                continue
            row_id = row.get("editable_field_row_id")
            indexes["editable_rows_by_id"][row_id] = row
            indexes["editable_rows_by_drawer_id"].setdefault(drawer_id, []).append(row)
            indexes["editable_rows_by_source_kind"].setdefault(source_kind, []).append(row)
            indexes["editable_rows_by_field_id"].setdefault(row.get("field_id"), []).append(row)
            if row.get("changed") is True:
                indexes["changed_rows_by_drawer_id"].setdefault(drawer_id, []).append(row)

    return indexes


@lru_cache(maxsize=1)
def build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_detail_edit_preview_payload_cached() -> Dict[str, object]:
    pack_189 = _load_pack_189_payload(force_refresh=False)

    saved_view_presets = pack_189.get("saved_view_presets", [])
    if not isinstance(saved_view_presets, list):
        saved_view_presets = []

    filter_presets = pack_189.get("filter_presets", [])
    if not isinstance(filter_presets, list):
        filter_presets = []

    saved_view_drawers = [
        _build_saved_view_detail_drawer(preset, idx)
        for idx, preset in enumerate(saved_view_presets, start=1)
        if isinstance(preset, dict)
    ]

    filter_preset_drawers = [
        _build_filter_preset_detail_drawer(preset, idx)
        for idx, preset in enumerate(filter_presets, start=1)
        if isinstance(preset, dict)
    ]

    all_drawers = saved_view_drawers + filter_preset_drawers
    all_rows = []
    for drawer in all_drawers:
        all_rows.extend(drawer.get("editable_field_rows", []))

    changed_rows = [row for row in all_rows if isinstance(row, dict) and row.get("changed") is True]
    unchanged_rows = [row for row in all_rows if isinstance(row, dict) and row.get("changed") is False]

    saved_view_changed = [
        row for row in changed_rows
        if row.get("source_kind") == "saved_view_preset"
    ]
    filter_preset_changed = [
        row for row in changed_rows
        if row.get("source_kind") == "filter_preset"
    ]

    indexes = _build_indexes(saved_view_drawers, filter_preset_drawers)

    readiness_checks = {
        "pack_189_ready": pack_189.get("status") == "ready",
        "has_saved_view_presets": len(saved_view_presets) == 6,
        "has_filter_presets": len(filter_presets) >= 9,
        "saved_view_drawer_count_is_six": len(saved_view_drawers) == 6,
        "filter_preset_drawer_count_is_nine": len(filter_preset_drawers) >= 9,
        "has_detail_edit_drawers": len(all_drawers) >= 15,
        "all_saved_view_drawers_ready": all(drawer.get("drawer_status") == "version_compare_navigation_saved_view_preset_detail_edit_drawer_preview_ready" for drawer in saved_view_drawers),
        "all_filter_preset_drawers_ready": all(drawer.get("drawer_status") == "version_compare_navigation_filter_preset_detail_edit_drawer_preview_ready" for drawer in filter_preset_drawers),
        "all_saved_view_drawers_have_five_rows": all(int(drawer.get("editable_field_row_count") or 0) == 5 for drawer in saved_view_drawers),
        "all_filter_preset_drawers_have_five_rows": all(int(drawer.get("editable_field_row_count") or 0) == 5 for drawer in filter_preset_drawers),
        "has_editable_rows": len(all_rows) >= 75,
        "has_changed_rows": len(changed_rows) >= 1,
        "has_unchanged_rows": len(unchanged_rows) >= 1,
        "saved_view_indexes_present": bool(indexes.get("saved_view_drawers_by_preset_id")),
        "filter_preset_indexes_present": bool(indexes.get("filter_preset_drawers_by_preset_id")),
        "editable_row_indexes_present": bool(indexes.get("editable_rows_by_id")),
        "changed_row_indexes_present": bool(indexes.get("changed_rows_by_drawer_id")),
        "all_simulated_only": all(item.get("simulated_only") is True for item in all_drawers + all_rows),
        "all_detail_edit_preview_only": all(item.get("detail_edit_preview_only") is True for item in all_drawers + all_rows),
        "all_saved_view_preview_only": all(item.get("saved_view_preview_only") is True for item in all_drawers + all_rows),
        "all_filter_preset_preview_only": all(item.get("filter_preset_preview_only") is True for item in all_drawers + all_rows),
        "all_navigation_preview_only": all(item.get("navigation_preview_only") is True for item in all_drawers + all_rows),
        "all_filter_navigation_preview_only": all(item.get("filter_navigation_preview_only") is True for item in all_drawers + all_rows),
        "no_real_saved_view_written": all(item.get("real_saved_view_written") is False for item in all_drawers + all_rows),
        "no_real_user_preference_written": all(item.get("real_user_preference_written") is False for item in all_drawers + all_rows),
        "no_real_filter_preference_saved": all(item.get("real_filter_preference_saved") is False for item in all_drawers + all_rows),
        "no_real_navigation_state_persisted": all(item.get("real_navigation_state_persisted") is False for item in all_drawers + all_rows),
        "no_real_drawer_selection_saved": all(item.get("real_drawer_selection_saved") is False for item in all_drawers + all_rows),
        "no_real_edit_persisted": all(item.get("real_edit_persisted") is False for item in all_drawers + all_rows),
        "all_saved_view_writes_blocked": all(item.get("saved_view_write_allowed_now") is False for item in all_drawers + all_rows),
        "all_user_preference_writes_blocked": all(item.get("user_preference_write_allowed_now") is False for item in all_drawers + all_rows),
        "all_filter_preference_saves_blocked": all(item.get("filter_preference_save_allowed_now") is False for item in all_drawers + all_rows),
        "all_navigation_persistence_blocked": all(item.get("navigation_persistence_allowed_now") is False for item in all_drawers + all_rows),
        "all_drawer_selection_saves_blocked": all(item.get("drawer_selection_save_allowed_now") is False for item in all_drawers + all_rows),
        "all_saves_blocked": all(item.get("save_allowed_now") is False for item in all_drawers + all_rows),
        "all_persists_blocked": all(item.get("persist_allowed_now") is False for item in all_drawers + all_rows),
        "all_raw_evidence_reveal_blocked": all(item.get("raw_evidence_reveal_allowed") is False for item in all_drawers + all_rows),
        "all_raw_evidence_lookup_blocked": all(item.get("raw_evidence_lookup_allowed") is False for item in all_drawers + all_rows),
        "cached_non_recursive": True,
    }

    readiness_score = 100 if all(v for v in readiness_checks.values() if isinstance(v, bool)) else 90

    return {
        "pack_id": PACK_ID,
        "pack_number": 190,
        "status": "ready" if readiness_score == 100 else "review",
        "title": "Owner Note Saved View Preset Detail Edit History Version Compare Navigation Saved View / Filter Preset Detail Edit Preview",
        "endpoint": DETAIL_EDIT_ENDPOINT,
        "source_endpoint": SOURCE_ENDPOINT,
        "generated_at": _utc_now(),
        **_base_flags(),
        "source_pack_189": {
            "status": pack_189.get("status"),
            "readiness_score": pack_189.get("summary", {}).get("readiness_score"),
            "saved_view_preset_count": pack_189.get("summary", {}).get("saved_view_preset_count"),
            "filter_preset_count": pack_189.get("summary", {}).get("filter_preset_count"),
            "source_navigation_item_count": pack_189.get("summary", {}).get("source_navigation_item_count"),
            "source_filter_lane_count": pack_189.get("summary", {}).get("source_filter_lane_count"),
        },
        "summary": {
            "saved_view_detail_drawer_count": len(saved_view_drawers),
            "filter_preset_detail_drawer_count": len(filter_preset_drawers),
            "total_detail_drawer_count": len(all_drawers),
            "saved_view_editable_row_count": sum(int(drawer.get("editable_field_row_count") or 0) for drawer in saved_view_drawers),
            "filter_preset_editable_row_count": sum(int(drawer.get("editable_field_row_count") or 0) for drawer in filter_preset_drawers),
            "total_editable_row_count": len(all_rows),
            "changed_field_count": len(changed_rows),
            "unchanged_field_count": len(unchanged_rows),
            "saved_view_changed_field_count": len(saved_view_changed),
            "filter_preset_changed_field_count": len(filter_preset_changed),
            "readiness_score": readiness_score,
            "readiness_label": "Owner note version compare navigation saved view/filter preset detail edit preview ready" if readiness_score == 100 else "Owner note version compare navigation saved view/filter preset detail edit preview needs review",
        },
        "readiness_checks": readiness_checks,
        "saved_view_detail_edit_drawers": saved_view_drawers,
        "filter_preset_detail_edit_drawers": filter_preset_drawers,
        "detail_edit_indexes": indexes,
    }


def build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_detail_edit_preview_payload(force_refresh: bool = False) -> Dict[str, object]:
    if force_refresh:
        build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_detail_edit_preview_payload_cached.cache_clear()
    return copy.deepcopy(build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_detail_edit_preview_payload_cached())


def get_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_detail_edit_preview_payload(force_refresh: bool = False) -> Dict[str, object]:
    return build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_detail_edit_preview_payload(force_refresh=force_refresh)


def build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_detail_edit_preview_status_bridge(force_refresh: bool = False) -> Dict[str, object]:
    payload = build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_detail_edit_preview_payload(force_refresh=force_refresh)
    summary = payload.get("summary", {})

    return {
        "pack_id": PACK_ID,
        "pack_number": 190,
        "status": payload.get("status"),
        "endpoint": payload.get("endpoint"),
        "source_endpoint": payload.get("source_endpoint"),
        "readiness_score": summary.get("readiness_score"),
        "readiness_label": summary.get("readiness_label"),
        "saved_view_detail_drawer_count": summary.get("saved_view_detail_drawer_count"),
        "filter_preset_detail_drawer_count": summary.get("filter_preset_detail_drawer_count"),
        "total_detail_drawer_count": summary.get("total_detail_drawer_count"),
        "saved_view_editable_row_count": summary.get("saved_view_editable_row_count"),
        "filter_preset_editable_row_count": summary.get("filter_preset_editable_row_count"),
        "total_editable_row_count": summary.get("total_editable_row_count"),
        "changed_field_count": summary.get("changed_field_count"),
        "unchanged_field_count": summary.get("unchanged_field_count"),
        "saved_view_changed_field_count": summary.get("saved_view_changed_field_count"),
        "filter_preset_changed_field_count": summary.get("filter_preset_changed_field_count"),
        **_base_flags(),
    }


def get_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_detail_edit_preview_status_bridge(force_refresh: bool = False) -> Dict[str, object]:
    return build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_detail_edit_preview_status_bridge(force_refresh=force_refresh)


def build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_detail_edit_preview_quick_action() -> Dict[str, object]:
    bridge = build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_detail_edit_preview_status_bridge()

    action = {
        "id": "policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_detail_edit_preview",
        "label": "Owner Note Version Compare Saved View Detail Edit",
        "title": "Owner Note Saved View Preset Detail Edit History Version Compare Navigation Saved View / Filter Preset Detail Edit Preview",
        "href": DETAIL_EDIT_ENDPOINT,
        "endpoint": DETAIL_EDIT_ENDPOINT,
        "description": "Preview editable saved view/filter preset detail drawers for version compare navigation with all persistence blocked.",
        "status": bridge.get("status"),
        "pack": "Pack 190",
        "category": "policy",
    }
    action.update(_base_flags())
    return action


def build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_detail_edit_preview_unified_owner_section() -> Dict[str, object]:
    payload = build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_detail_edit_preview_payload()
    summary = payload.get("summary", {})
    checks = payload.get("readiness_checks", {})

    section = {
        "section_id": "policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_detail_edit_preview",
        "title": "Owner Note Version Compare Saved View Detail Edit",
        "subtitle": "Preview detail edit drawers and editable rows for version compare navigation saved view/filter presets.",
        "status": payload.get("status"),
        "href": DETAIL_EDIT_ENDPOINT,
        "cards": [
            {"id": "readiness", "title": "Detail edit readiness", "value": summary.get("readiness_score"), "label": summary.get("readiness_label")},
            {"id": "saved_view_drawers", "title": "Saved view drawers", "value": summary.get("saved_view_detail_drawer_count"), "label": "Saved view detail edit drawers"},
            {"id": "filter_preset_drawers", "title": "Filter preset drawers", "value": summary.get("filter_preset_detail_drawer_count"), "label": "Filter preset detail edit drawers"},
            {"id": "editable_rows", "title": "Editable rows", "value": summary.get("total_editable_row_count"), "label": "Preview editable rows"},
            {"id": "changed_fields", "title": "Changed fields", "value": summary.get("changed_field_count"), "label": "Preview field changes"},
            {"id": "persistence", "title": "Persistence", "value": "Blocked" if checks.get("all_saved_view_writes_blocked") and checks.get("all_user_preference_writes_blocked") else "Review", "label": "No real saved view/preference write"},
        ],
    }
    section.update(_base_flags())
    return section


def build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_detail_edit_preview_html_section() -> str:
    section = build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_detail_edit_preview_unified_owner_section()
    cards = section.get("cards", [])

    card_html = []
    for card in cards:
        card_html.append(
            f"""
            <article class="tower-card policy-change-approval-receipt-owner-note-version-compare-saved-view-detail-edit-card">
                <div class="tower-card-kicker">{card.get('title', '')}</div>
                <div class="tower-card-value">{card.get('value', '')}</div>
                <p>{card.get('label', '')}</p>
            </article>
            """
        )

    return f"""
    <section class="tower-section policy-change-approval-receipt-owner-note-version-compare-saved-view-detail-edit-section" id="policy-change-approval-receipt-owner-note-saved-view-preset-detail-edit-history-version-compare-navigation-saved-view-filter-preset-detail-edit-preview">
        <div class="tower-section-heading">
            <p class="tower-kicker">Pack 190</p>
            <h2>{section.get('title', 'Owner Note Version Compare Saved View Detail Edit')}</h2>
            <p>{section.get('subtitle', '')}</p>
            <a class="tower-link-pill" href="{DETAIL_EDIT_ENDPOINT}">Open version compare saved view/filter preset detail edit JSON</a>
        </div>
        <div class="tower-card-grid">
            {''.join(card_html)}
        </div>
    </section>
    """


__all__ = [
    "PACK_ID",
    "DETAIL_EDIT_ENDPOINT",
    "SOURCE_ENDPOINT",
    "SAVED_VIEW_FIELDS",
    "FILTER_PRESET_FIELDS",
    "build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_detail_edit_preview_payload",
    "get_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_detail_edit_preview_payload",
    "build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_detail_edit_preview_status_bridge",
    "get_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_detail_edit_preview_status_bridge",
    "build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_detail_edit_preview_quick_action",
    "build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_detail_edit_preview_unified_owner_section",
    "build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_detail_edit_preview_html_section",
]
