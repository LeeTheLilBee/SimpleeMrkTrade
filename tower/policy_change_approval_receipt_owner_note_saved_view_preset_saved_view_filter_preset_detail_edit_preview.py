
"""
PACK 180 - Owner Note Saved View Preset Saved View / Filter Preset Detail Edit Preview.

This module sits on top of Pack 179.

Pack 179 creates preview-only saved view/filter presets for the saved-view-preset
version compare navigation layer.
Pack 180 creates preview-only detail/edit scaffolding for those saved view/filter presets:
- saved view preset detail edit drawers
- filter preset detail edit drawers
- editable field rows
- preview edit snapshots
- blocked save/persist/preference/navigation writes

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


PACK_ID = "PACK_180"
DETAIL_EDIT_ENDPOINT = "/tower/policy-change-approval-receipt-owner-note-saved-view-preset-saved-view-filter-preset-detail-edit-preview.json"
SOURCE_ENDPOINT = "/tower/policy-change-approval-receipt-owner-note-saved-view-preset-version-compare-navigation-saved-view-filter-preset.json"


SAVED_VIEW_EDIT_FIELDS = [
    {"field_id": "label", "field_label": "Saved View Label", "field_type": "text"},
    {"field_id": "description", "field_label": "Saved View Description", "field_type": "textarea"},
    {"field_id": "filter_lane_id", "field_label": "Filter Lane", "field_type": "select"},
    {"field_id": "view_priority", "field_label": "View Priority", "field_type": "select"},
    {"field_id": "is_default", "field_label": "Default View", "field_type": "boolean"},
]

FILTER_PRESET_EDIT_FIELDS = [
    {"field_id": "label", "field_label": "Filter Preset Label", "field_type": "text"},
    {"field_id": "description", "field_label": "Filter Preset Description", "field_type": "textarea"},
    {"field_id": "filter_type", "field_label": "Filter Type", "field_type": "select"},
    {"field_id": "matched_drawer_count", "field_label": "Matched Drawer Count", "field_type": "readonly_number"},
    {"field_id": "default_selected_saved_view_preset_id", "field_label": "Default Selected Preset", "field_type": "readonly_text"},
]


def _utc_now() -> str:
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def _stable_hash(value: Any, length: int = 18) -> str:
    raw = repr(value).encode("utf-8", errors="ignore")
    return hashlib.sha256(raw).hexdigest()[:length]


def _safe_text(value: Any) -> str:
    text = str(value or "")
    forbidden_fragments = [
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
    lowered = text.lower()
    for fragment in forbidden_fragments:
        if fragment in lowered:
            return "[REDACTED]"
    return text


def _base_flags() -> Dict[str, Any]:
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


def _load_pack_179_payload(force_refresh: bool = False) -> Dict[str, Any]:
    try:
        mod = importlib.import_module(
            "tower.policy_change_approval_receipt_owner_note_saved_view_preset_version_compare_navigation_saved_view_filter_preset"
        )
        fn = getattr(
            mod,
            "build_policy_change_approval_receipt_owner_note_saved_view_preset_version_compare_navigation_saved_view_filter_preset_payload",
            None,
        )
        if callable(fn):
            payload = fn(force_refresh=force_refresh)
            if isinstance(payload, dict):
                return payload
    except Exception as exc:
        return {
            "pack_id": "PACK_179",
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
        "pack_id": "PACK_179",
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


def _normalize_value(value: Any) -> Dict[str, Any]:
    if isinstance(value, bool):
        return {"kind": "boolean", "value": value, "display_value": "Yes" if value else "No", "safe_preview_only": True}

    if isinstance(value, int) or isinstance(value, float):
        return {"kind": "number", "value": value, "display_value": str(value), "safe_preview_only": True}

    if isinstance(value, list):
        return {
            "kind": "list",
            "value": [_safe_text(item) for item in value],
            "item_count": len(value),
            "safe_preview_only": True,
        }

    if isinstance(value, dict):
        return {
            "kind": "object",
            "value": {_safe_text(k): _safe_text(v) for k, v in value.items()},
            "item_count": len(value),
            "safe_preview_only": True,
        }

    text = _safe_text(value)
    return {"kind": "text", "value": text, "length": len(text), "safe_preview_only": True}


def _preview_edit_value(field_id: str, current_value: Any, field_type: str, sequence: int) -> Any:
    if field_type == "boolean":
        return bool(current_value)

    if field_type.startswith("readonly"):
        return current_value

    if field_id == "label":
        return f"{_safe_text(current_value)} · Preview"

    if field_id == "description":
        return f"{_safe_text(current_value)} Preview edit only; no persistence allowed."

    if field_id == "view_priority":
        current = _safe_text(current_value)
        if current == "critical":
            return "high"
        if current == "high":
            return "medium"
        if current == "medium":
            return "standard"
        return current or "standard"

    if field_id == "filter_lane_id":
        return _safe_text(current_value)

    return current_value


def _build_editable_row(source_kind: str, source_id: str, drawer_id: str, source: Dict[str, Any], field_def: Dict[str, Any], sequence: int) -> Dict[str, Any]:
    field_id = _safe_text(field_def.get("field_id"))
    field_type = _safe_text(field_def.get("field_type"))
    current_value = source.get(field_id)
    preview_value = _preview_edit_value(field_id, current_value, field_type, sequence)

    identity = {
        "pack": PACK_ID,
        "source_kind": source_kind,
        "source_id": source_id,
        "drawer_id": drawer_id,
        "field_id": field_id,
        "sequence": sequence,
    }

    row = {
        "editable_field_row_id": f"saved_view_filter_preset_editable_field_row_{_stable_hash(identity, 18)}",
        "source_kind": source_kind,
        "source_id": source_id,
        "drawer_id": drawer_id,
        "field_id": field_id,
        "field_label": _safe_text(field_def.get("field_label")),
        "field_type": field_type,
        "sequence": int(sequence),
        "current_value": _normalize_value(current_value),
        "preview_value": _normalize_value(preview_value),
        "changed": _normalize_value(current_value) != _normalize_value(preview_value),
        "editable_in_preview": field_type.startswith("readonly") is False,
        "row_status": "saved_view_filter_preset_editable_field_row_preview_ready",
        "row_result_type": "owner_note_saved_view_filter_preset_editable_field_row_preview",
        "safe_preview_only": True,
    }
    row.update(_base_flags())
    return row


def _build_saved_view_detail_edit_drawer(preset: Dict[str, Any], sequence: int) -> Dict[str, Any]:
    preset = dict(preset or {})
    source_id = _safe_text(preset.get("saved_view_preset_id"))
    drawer_id = f"saved_view_preset_detail_edit_drawer_{_stable_hash((PACK_ID, source_id, sequence), 18)}"

    rows = [
        _build_editable_row("saved_view_preset", source_id, drawer_id, preset, field_def, idx)
        for idx, field_def in enumerate(SAVED_VIEW_EDIT_FIELDS, start=1)
    ]

    original_snapshot = {
        "saved_view_preset_id": source_id,
        "label": preset.get("label"),
        "description": preset.get("description"),
        "filter_lane_id": preset.get("filter_lane_id"),
        "view_priority": preset.get("view_priority"),
        "is_default": preset.get("is_default"),
    }

    preview_edit_snapshot = {
        row["field_id"]: row["preview_value"].get("value")
        for row in rows
    }
    preview_edit_snapshot["saved_view_preset_id"] = source_id

    drawer = {
        "detail_edit_drawer_id": drawer_id,
        "source_kind": "saved_view_preset",
        "source_id": source_id,
        "saved_view_preset_id": source_id,
        "filter_lane_id": _safe_text(preset.get("filter_lane_id")),
        "linked_filter_preset_id": preset.get("linked_filter_preset_id"),
        "label": _safe_text(preset.get("label")),
        "view_priority": _safe_text(preset.get("view_priority")),
        "is_default": bool(preset.get("is_default", False)),
        "sequence": int(sequence),
        "drawer_status": "saved_view_preset_detail_edit_preview_ready",
        "drawer_result_type": "owner_note_saved_view_preset_detail_edit_drawer_preview",
        "editable_field_rows": rows,
        "editable_field_row_count": len(rows),
        "changed_field_count": len([row for row in rows if row.get("changed") is True]),
        "unchanged_field_count": len([row for row in rows if row.get("changed") is False]),
        "original_snapshot": original_snapshot,
        "preview_edit_snapshot": preview_edit_snapshot,
        "matched_navigation_item_count": int(preset.get("matched_navigation_item_count") or 0),
        "comparison_row_count": int(preset.get("comparison_row_count") or 0),
    }
    drawer.update(_base_flags())
    return drawer


def _build_filter_preset_detail_edit_drawer(preset: Dict[str, Any], sequence: int) -> Dict[str, Any]:
    preset = dict(preset or {})
    source_id = _safe_text(preset.get("filter_preset_id"))
    lane_id = _safe_text(preset.get("filter_lane_id"))
    drawer_id = f"filter_preset_detail_edit_drawer_{_stable_hash((PACK_ID, source_id, lane_id, sequence), 18)}"

    rows = [
        _build_editable_row("filter_preset", source_id, drawer_id, preset, field_def, idx)
        for idx, field_def in enumerate(FILTER_PRESET_EDIT_FIELDS, start=1)
    ]

    original_snapshot = {
        "filter_preset_id": source_id,
        "filter_lane_id": lane_id,
        "label": preset.get("label"),
        "description": preset.get("description"),
        "filter_type": preset.get("filter_type"),
        "matched_drawer_count": preset.get("matched_drawer_count"),
        "default_selected_saved_view_preset_id": preset.get("default_selected_saved_view_preset_id"),
    }

    preview_edit_snapshot = {
        row["field_id"]: row["preview_value"].get("value")
        for row in rows
    }
    preview_edit_snapshot["filter_preset_id"] = source_id
    preview_edit_snapshot["filter_lane_id"] = lane_id

    drawer = {
        "detail_edit_drawer_id": drawer_id,
        "source_kind": "filter_preset",
        "source_id": source_id,
        "filter_preset_id": source_id,
        "filter_lane_id": lane_id,
        "label": _safe_text(preset.get("label")),
        "filter_type": _safe_text(preset.get("filter_type")),
        "sequence": int(sequence),
        "drawer_status": "filter_preset_detail_edit_preview_ready",
        "drawer_result_type": "owner_note_filter_preset_detail_edit_drawer_preview",
        "editable_field_rows": rows,
        "editable_field_row_count": len(rows),
        "changed_field_count": len([row for row in rows if row.get("changed") is True]),
        "unchanged_field_count": len([row for row in rows if row.get("changed") is False]),
        "original_snapshot": original_snapshot,
        "preview_edit_snapshot": preview_edit_snapshot,
        "matched_drawer_count": int(preset.get("matched_drawer_count") or 0),
    }
    drawer.update(_base_flags())
    return drawer


def _build_indexes(saved_view_drawers: List[Dict[str, Any]], filter_preset_drawers: List[Dict[str, Any]]) -> Dict[str, Any]:
    indexes = {
        "saved_view_drawers_by_id": {},
        "saved_view_drawers_by_preset_id": {},
        "saved_view_drawers_by_filter_lane_id": {},
        "filter_preset_drawers_by_id": {},
        "filter_preset_drawers_by_preset_id": {},
        "filter_preset_drawers_by_filter_lane_id": {},
        "editable_rows_by_id": {},
        "editable_rows_by_source_kind": {},
    }

    for drawer in saved_view_drawers:
        drawer_id = _safe_text(drawer.get("detail_edit_drawer_id"))
        preset_id = _safe_text(drawer.get("saved_view_preset_id"))
        lane_id = _safe_text(drawer.get("filter_lane_id"))

        indexes["saved_view_drawers_by_id"][drawer_id] = drawer
        indexes["saved_view_drawers_by_preset_id"][preset_id] = drawer
        indexes["saved_view_drawers_by_filter_lane_id"].setdefault(lane_id, []).append(drawer)

        for row in drawer.get("editable_field_rows", []):
            row_id = _safe_text(row.get("editable_field_row_id"))
            indexes["editable_rows_by_id"][row_id] = row
            indexes["editable_rows_by_source_kind"].setdefault("saved_view_preset", []).append(row)

    for drawer in filter_preset_drawers:
        drawer_id = _safe_text(drawer.get("detail_edit_drawer_id"))
        preset_id = _safe_text(drawer.get("filter_preset_id"))
        lane_id = _safe_text(drawer.get("filter_lane_id"))

        indexes["filter_preset_drawers_by_id"][drawer_id] = drawer
        indexes["filter_preset_drawers_by_preset_id"][preset_id] = drawer
        indexes["filter_preset_drawers_by_filter_lane_id"][lane_id] = drawer

        for row in drawer.get("editable_field_rows", []):
            row_id = _safe_text(row.get("editable_field_row_id"))
            indexes["editable_rows_by_id"][row_id] = row
            indexes["editable_rows_by_source_kind"].setdefault("filter_preset", []).append(row)

    return indexes


@lru_cache(maxsize=1)
def build_policy_change_approval_receipt_owner_note_saved_view_preset_saved_view_filter_preset_detail_edit_preview_payload_cached() -> Dict[str, Any]:
    pack_179 = _load_pack_179_payload(force_refresh=False)

    saved_view_presets = pack_179.get("saved_view_presets", [])
    if not isinstance(saved_view_presets, list):
        saved_view_presets = []

    filter_presets = pack_179.get("filter_presets", [])
    if not isinstance(filter_presets, list):
        filter_presets = []

    saved_view_drawers = [
        _build_saved_view_detail_edit_drawer(preset, idx)
        for idx, preset in enumerate(saved_view_presets, start=1)
        if isinstance(preset, dict)
    ]

    filter_preset_drawers = [
        _build_filter_preset_detail_edit_drawer(preset, idx)
        for idx, preset in enumerate(filter_presets, start=1)
        if isinstance(preset, dict)
    ]

    all_drawers = saved_view_drawers + filter_preset_drawers
    all_rows = []
    for drawer in all_drawers:
        all_rows.extend(drawer.get("editable_field_rows", []))

    indexes = _build_indexes(saved_view_drawers, filter_preset_drawers)

    saved_view_changed = sum(int(drawer.get("changed_field_count") or 0) for drawer in saved_view_drawers)
    filter_changed = sum(int(drawer.get("changed_field_count") or 0) for drawer in filter_preset_drawers)
    total_changed = saved_view_changed + filter_changed
    total_rows = len(all_rows)
    total_unchanged = total_rows - total_changed

    readiness_checks = {
        "pack_179_ready": pack_179.get("status") == "ready",
        "has_saved_view_presets": len(saved_view_presets) >= 6,
        "has_filter_presets": len(filter_presets) >= 9,
        "saved_view_drawer_count_is_six": len(saved_view_drawers) == 6,
        "filter_preset_drawer_count_is_nine": len(filter_preset_drawers) >= 9,
        "all_saved_view_drawers_ready": all(drawer.get("drawer_status") == "saved_view_preset_detail_edit_preview_ready" for drawer in saved_view_drawers),
        "all_filter_preset_drawers_ready": all(drawer.get("drawer_status") == "filter_preset_detail_edit_preview_ready" for drawer in filter_preset_drawers),
        "all_saved_view_drawers_have_five_rows": all(int(drawer.get("editable_field_row_count") or 0) == 5 for drawer in saved_view_drawers),
        "all_filter_preset_drawers_have_five_rows": all(int(drawer.get("editable_field_row_count") or 0) == 5 for drawer in filter_preset_drawers),
        "has_editable_rows": total_rows >= 75,
        "has_changed_rows": total_changed >= 1,
        "saved_view_indexes_present": bool(indexes.get("saved_view_drawers_by_preset_id")),
        "filter_preset_indexes_present": bool(indexes.get("filter_preset_drawers_by_filter_lane_id")),
        "editable_row_indexes_present": bool(indexes.get("editable_rows_by_id")),
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
        "endpoint": DETAIL_EDIT_ENDPOINT,
        "cached_non_recursive": True,
    }

    bool_checks = [
        value for value in readiness_checks.values()
        if isinstance(value, bool)
    ]
    readiness_score = 100 if all(bool_checks) else 90

    return {
        "pack_id": PACK_ID,
        "pack_number": 180,
        "status": "ready" if readiness_score == 100 else "review",
        "title": "Owner Note Saved View Preset Saved View / Filter Preset Detail Edit Preview",
        "endpoint": DETAIL_EDIT_ENDPOINT,
        "source_endpoint": SOURCE_ENDPOINT,
        "generated_at": _utc_now(),
        **_base_flags(),
        "source_pack_179": {
            "status": pack_179.get("status"),
            "readiness_score": pack_179.get("summary", {}).get("readiness_score"),
            "saved_view_preset_count": pack_179.get("summary", {}).get("saved_view_preset_count"),
            "filter_preset_count": pack_179.get("summary", {}).get("filter_preset_count"),
            "comparison_row_count": pack_179.get("summary", {}).get("comparison_row_count"),
        },
        "summary": {
            "saved_view_detail_drawer_count": len(saved_view_drawers),
            "filter_preset_detail_drawer_count": len(filter_preset_drawers),
            "total_detail_drawer_count": len(all_drawers),
            "saved_view_editable_row_count": sum(len(drawer.get("editable_field_rows", [])) for drawer in saved_view_drawers),
            "filter_preset_editable_row_count": sum(len(drawer.get("editable_field_rows", [])) for drawer in filter_preset_drawers),
            "total_editable_row_count": total_rows,
            "changed_field_count": total_changed,
            "unchanged_field_count": total_unchanged,
            "saved_view_changed_field_count": saved_view_changed,
            "filter_preset_changed_field_count": filter_changed,
            "readiness_score": readiness_score,
            "readiness_label": "Owner note saved view/filter preset detail edit preview ready" if readiness_score == 100 else "Owner note saved view/filter preset detail edit preview needs review",
        },
        "readiness_checks": readiness_checks,
        "saved_view_edit_fields": SAVED_VIEW_EDIT_FIELDS,
        "filter_preset_edit_fields": FILTER_PRESET_EDIT_FIELDS,
        "saved_view_detail_edit_drawers": saved_view_drawers,
        "filter_preset_detail_edit_drawers": filter_preset_drawers,
        "detail_edit_indexes": indexes,
    }


def build_policy_change_approval_receipt_owner_note_saved_view_preset_saved_view_filter_preset_detail_edit_preview_payload(force_refresh: bool = False) -> Dict[str, Any]:
    if force_refresh:
        build_policy_change_approval_receipt_owner_note_saved_view_preset_saved_view_filter_preset_detail_edit_preview_payload_cached.cache_clear()
    return copy.deepcopy(build_policy_change_approval_receipt_owner_note_saved_view_preset_saved_view_filter_preset_detail_edit_preview_payload_cached())


def get_policy_change_approval_receipt_owner_note_saved_view_preset_saved_view_filter_preset_detail_edit_preview_payload(force_refresh: bool = False) -> Dict[str, Any]:
    return build_policy_change_approval_receipt_owner_note_saved_view_preset_saved_view_filter_preset_detail_edit_preview_payload(force_refresh=force_refresh)


def build_policy_change_approval_receipt_owner_note_saved_view_preset_saved_view_filter_preset_detail_edit_preview_status_bridge(force_refresh: bool = False) -> Dict[str, Any]:
    payload = build_policy_change_approval_receipt_owner_note_saved_view_preset_saved_view_filter_preset_detail_edit_preview_payload(force_refresh=force_refresh)
    summary = payload.get("summary", {})

    return {
        "pack_id": PACK_ID,
        "pack_number": 180,
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


def get_policy_change_approval_receipt_owner_note_saved_view_preset_saved_view_filter_preset_detail_edit_preview_status_bridge(force_refresh: bool = False) -> Dict[str, Any]:
    return build_policy_change_approval_receipt_owner_note_saved_view_preset_saved_view_filter_preset_detail_edit_preview_status_bridge(force_refresh=force_refresh)


def build_policy_change_approval_receipt_owner_note_saved_view_preset_saved_view_filter_preset_detail_edit_preview_quick_action() -> Dict[str, Any]:
    bridge = build_policy_change_approval_receipt_owner_note_saved_view_preset_saved_view_filter_preset_detail_edit_preview_status_bridge()

    action = {
        "id": "policy_change_approval_receipt_owner_note_saved_view_preset_saved_view_filter_preset_detail_edit_preview",
        "label": "Owner Note Saved View Detail Edit",
        "title": "Owner Note Saved View Preset Saved View / Filter Preset Detail Edit Preview",
        "href": DETAIL_EDIT_ENDPOINT,
        "endpoint": DETAIL_EDIT_ENDPOINT,
        "description": "Preview saved view/filter preset detail edit drawers and editable rows with all persistence blocked.",
        "status": bridge.get("status"),
        "pack": "Pack 180",
        "category": "policy",
    }
    action.update(_base_flags())
    return action


def build_policy_change_approval_receipt_owner_note_saved_view_preset_saved_view_filter_preset_detail_edit_preview_unified_owner_section() -> Dict[str, Any]:
    payload = build_policy_change_approval_receipt_owner_note_saved_view_preset_saved_view_filter_preset_detail_edit_preview_payload()
    summary = payload.get("summary", {})
    checks = payload.get("readiness_checks", {})

    section = {
        "section_id": "policy_change_approval_receipt_owner_note_saved_view_preset_saved_view_filter_preset_detail_edit_preview",
        "title": "Owner Note Saved View Detail Edit",
        "subtitle": "Preview saved view/filter preset detail edit drawers, editable rows, preview snapshots, and blocked persistence.",
        "status": payload.get("status"),
        "href": DETAIL_EDIT_ENDPOINT,
        "cards": [
            {
                "id": "detail_edit_readiness",
                "title": "Detail edit readiness",
                "value": summary.get("readiness_score"),
                "label": summary.get("readiness_label"),
            },
            {
                "id": "saved_view_drawers",
                "title": "Saved view drawers",
                "value": summary.get("saved_view_detail_drawer_count"),
                "label": "Saved view detail edit drawers",
            },
            {
                "id": "filter_preset_drawers",
                "title": "Filter preset drawers",
                "value": summary.get("filter_preset_detail_drawer_count"),
                "label": "Filter preset detail edit drawers",
            },
            {
                "id": "editable_rows",
                "title": "Editable rows",
                "value": summary.get("total_editable_row_count"),
                "label": "Preview editable fields",
            },
            {
                "id": "changed_fields",
                "title": "Changed fields",
                "value": summary.get("changed_field_count"),
                "label": "Preview changes only",
            },
            {
                "id": "persistence",
                "title": "Persistence",
                "value": "Blocked" if checks.get("all_saves_blocked") and checks.get("all_persists_blocked") else "Review",
                "label": "No real save/persist",
            },
        ],
    }
    section.update(_base_flags())
    return section


def build_policy_change_approval_receipt_owner_note_saved_view_preset_saved_view_filter_preset_detail_edit_preview_html_section() -> str:
    section = build_policy_change_approval_receipt_owner_note_saved_view_preset_saved_view_filter_preset_detail_edit_preview_unified_owner_section()
    cards = section.get("cards", [])

    card_html = []
    for card in cards:
        card_html.append(
            f"""
            <article class="tower-card policy-change-approval-receipt-owner-note-saved-view-detail-edit-card">
                <div class="tower-card-kicker">{card.get('title', '')}</div>
                <div class="tower-card-value">{card.get('value', '')}</div>
                <p>{card.get('label', '')}</p>
            </article>
            """
        )

    return f"""
    <section class="tower-section policy-change-approval-receipt-owner-note-saved-view-detail-edit-section" id="policy-change-approval-receipt-owner-note-saved-view-preset-saved-view-filter-preset-detail-edit-preview">
        <div class="tower-section-heading">
            <p class="tower-kicker">Pack 180</p>
            <h2>{section.get('title', 'Owner Note Saved View Detail Edit')}</h2>
            <p>{section.get('subtitle', '')}</p>
            <a class="tower-link-pill" href="{DETAIL_EDIT_ENDPOINT}">Open saved view/filter preset detail edit JSON</a>
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
    "SAVED_VIEW_EDIT_FIELDS",
    "FILTER_PRESET_EDIT_FIELDS",
    "build_policy_change_approval_receipt_owner_note_saved_view_preset_saved_view_filter_preset_detail_edit_preview_payload",
    "get_policy_change_approval_receipt_owner_note_saved_view_preset_saved_view_filter_preset_detail_edit_preview_payload",
    "build_policy_change_approval_receipt_owner_note_saved_view_preset_saved_view_filter_preset_detail_edit_preview_status_bridge",
    "get_policy_change_approval_receipt_owner_note_saved_view_preset_saved_view_filter_preset_detail_edit_preview_status_bridge",
    "build_policy_change_approval_receipt_owner_note_saved_view_preset_saved_view_filter_preset_detail_edit_preview_quick_action",
    "build_policy_change_approval_receipt_owner_note_saved_view_preset_saved_view_filter_preset_detail_edit_preview_unified_owner_section",
    "build_policy_change_approval_receipt_owner_note_saved_view_preset_saved_view_filter_preset_detail_edit_preview_html_section",
]
