
"""
PACK 175 - Owner Note Saved View Preset Detail Drawer / Edit Preview.

This module sits on top of Pack 174.

Pack 174 creates preview-only saved compare navigation views and filter presets.
Pack 175 creates preview-only detail drawer/edit preview scaffolding for those presets:
- saved view preset detail drawer
- preset editable field rows
- proposed preset update preview
- preset edit validation preview
- blocked save/apply/persist actions

Important:
- simulated-only
- saved-view-preset-detail-preview-only
- saved-view-preset-edit-preview-only
- saved-navigation-preview-only
- saved-filter-preset-preview-only
- navigation-preview-only
- filter-navigation-preview-only
- version-detail-preview-only
- compare-view-preview-only
- version-preview-only
- edit-history-preview-only
- rollback-preview-only
- compare-preview-only
- edit-preview-only
- detail-drawer-preview-only
- owner-note-preview-only
- review-draft-preview-only
- saved-view-preview-only
- filter-preset-preview-only
- filter-preview-only
- search-facet-preview-only
- lookup-preview-only
- detail-preview-only
- evidence-drawer-preview-only
- owner-review-preview-only
- queue-preview-only
- renewal-preview-only
- recheck-preview-only
- expiration-preview-only
- vault-preview-only
- index-preview-only
- receipt-preview-only
- approval-preview-only
- evidence-preview-only
- no real saved-view writes
- no real user-preference writes
- no real filter preference saves
- no real navigation state persistence
- no real drawer selection saves
- no real history/version writes
- no real rollback/restore
- no raw evidence revealed
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


PACK_ID = "PACK_175"
SAVED_VIEW_PRESET_DETAIL_EDIT_ENDPOINT = "/tower/policy-change-approval-receipt-owner-note-saved-view-preset-detail-edit-preview.json"
SAVED_VIEW_FILTER_PRESET_ENDPOINT = "/tower/policy-change-approval-receipt-owner-note-compare-navigation-saved-view-filter-preset.json"


EDITABLE_PRESET_FIELDS = [
    "label",
    "description",
    "filter_lane_id",
    "view_priority",
    "is_default",
]


FIELD_LABELS = {
    "label": "Preset Label",
    "description": "Preset Description",
    "filter_lane_id": "Filter Lane",
    "view_priority": "View Priority",
    "is_default": "Default View",
}


FIELD_TYPES = {
    "label": "text",
    "description": "textarea",
    "filter_lane_id": "select",
    "view_priority": "select",
    "is_default": "boolean",
}


ALLOWED_VIEW_PRIORITIES = ["critical", "high", "medium", "standard", "monitor"]
ALLOWED_FILTER_LANES = [
    "all_compare_drawers",
    "owner_review_required",
    "owner_review_not_required",
    "critical_priority",
    "high_priority",
    "medium_priority",
    "monitor_priority",
    "safe_preview_only",
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


def _load_pack_174_payload(force_refresh: bool = False) -> Dict[str, Any]:
    try:
        mod = importlib.import_module("tower.policy_change_approval_receipt_owner_note_compare_navigation_saved_view_filter_preset")
        fn = getattr(mod, "build_policy_change_approval_receipt_owner_note_compare_navigation_saved_view_filter_preset_payload", None)
        if callable(fn):
            payload = fn(force_refresh=force_refresh)
            if isinstance(payload, dict):
                return payload
    except Exception as exc:
        return {
            "pack_id": "PACK_174",
            "status": "review",
            "endpoint": SAVED_VIEW_FILTER_PRESET_ENDPOINT,
            "simulated_only": True,
            "saved_navigation_preview_only": True,
            "saved_filter_preset_preview_only": True,
            "navigation_preview_only": True,
            "filter_navigation_preview_only": True,
            "saved_view_preview_only": True,
            "filter_preset_preview_only": True,
            "load_error": str(exc),
            "summary": {
                "saved_view_preset_count": 0,
                "preset_chip_count": 0,
                "preset_detail_count": 0,
                "readiness_score": 0,
                "readiness_label": "Pack 174 saved view/filter preset payload unavailable",
            },
            "saved_view_presets": [],
            "preset_detail_previews": {"preset_detail_previews": []},
            "preset_chips_preview": {"preset_chips": []},
            "default_saved_view_selection": {},
        }

    return {
        "pack_id": "PACK_174",
        "status": "review",
        "endpoint": SAVED_VIEW_FILTER_PRESET_ENDPOINT,
        "simulated_only": True,
        "saved_navigation_preview_only": True,
        "saved_filter_preset_preview_only": True,
        "navigation_preview_only": True,
        "filter_navigation_preview_only": True,
        "saved_view_preview_only": True,
        "filter_preset_preview_only": True,
        "summary": {
            "saved_view_preset_count": 0,
            "preset_chip_count": 0,
            "preset_detail_count": 0,
            "readiness_score": 0,
            "readiness_label": "Pack 174 saved view/filter preset payload unavailable",
        },
        "saved_view_presets": [],
        "preset_detail_previews": {"preset_detail_previews": []},
        "preset_chips_preview": {"preset_chips": []},
        "default_saved_view_selection": {},
    }


def _priority_rank(priority: Any) -> int:
    ranking = {
        "critical": 1,
        "high": 2,
        "medium": 3,
        "standard": 4,
        "monitor": 5,
    }
    return ranking.get(_safe_text(priority), 99)


def _count_by(items: List[Dict[str, Any]], key: str) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for item in items:
        value = _safe_text(item.get(key)) or "unknown"
        counts[value] = counts.get(value, 0) + 1
    return counts


def _proposed_value_for_field(preset: Dict[str, Any], field_id: str) -> Any:
    current = preset.get(field_id)

    if field_id == "label":
        return f"{_safe_text(current)} — Preview"
    if field_id == "description":
        return f"{_safe_text(current)} Preview-only refinement for owner review flow."
    if field_id == "filter_lane_id":
        return _safe_text(current) if _safe_text(current) in ALLOWED_FILTER_LANES else "all_compare_drawers"
    if field_id == "view_priority":
        current_priority = _safe_text(current)
        if current_priority == "standard":
            return "high"
        return current_priority if current_priority in ALLOWED_VIEW_PRIORITIES else "standard"
    if field_id == "is_default":
        return bool(current)

    return current


def _value_summary(value: Any) -> Dict[str, Any]:
    if isinstance(value, bool):
        return {
            "kind": "boolean",
            "preview": value,
            "display_value": "Yes" if value else "No",
            "safe_preview_only": True,
        }

    if isinstance(value, list):
        return {
            "kind": "list",
            "preview": [_safe_text(item) for item in value],
            "item_count": len(value),
            "safe_preview_only": True,
        }

    text = _safe_text(value)
    return {
        "kind": "text",
        "preview": text,
        "length": len(text),
        "safe_preview_only": True,
    }


def _build_editable_field_row(preset: Dict[str, Any], field_id: str) -> Dict[str, Any]:
    current_value = preset.get(field_id)
    proposed_value = _proposed_value_for_field(preset, field_id)
    changed = _value_summary(current_value) != _value_summary(proposed_value)

    identity = {
        "pack": PACK_ID,
        "preset": preset.get("saved_view_preset_id"),
        "field": field_id,
        "current": current_value,
        "proposed": proposed_value,
    }

    return {
        "editable_field_row_id": f"saved_view_preset_editable_field_row_{_stable_hash(identity, 18)}",
        "saved_view_preset_id": _safe_text(preset.get("saved_view_preset_id")),
        "field_id": field_id,
        "field_label": FIELD_LABELS.get(field_id, field_id),
        "field_type": FIELD_TYPES.get(field_id, "text"),
        "current_value": _value_summary(current_value),
        "proposed_value": _value_summary(proposed_value),
        "changed": changed,
        "validation": {
            "valid": True,
            "message": "Preview-only field update is valid.",
            "safe_preview_only": True,
        },
        "row_status": "saved_view_preset_editable_field_preview_ready",
        "row_result_type": "owner_note_saved_view_preset_editable_field_preview",
        "edit_allowed_in_preview": True,
        "save_allowed_now": False,
        "apply_allowed_now": False,
        "persist_allowed_now": False,
        "saved_view_write_allowed_now": False,
        "user_preference_write_allowed_now": False,
        "real_saved_view_written": False,
        "real_user_preference_written": False,
        "real_filter_preference_saved": False,
        "real_navigation_state_persisted": False,
        "real_drawer_selection_saved": False,
        "real_history_written": False,
        "real_version_written": False,
        "simulated_only": True,
        "saved_view_preset_detail_preview_only": True,
        "saved_view_preset_edit_preview_only": True,
        "saved_navigation_preview_only": True,
        "saved_filter_preset_preview_only": True,
        "navigation_preview_only": True,
        "filter_navigation_preview_only": True,
        "saved_view_preview_only": True,
        "filter_preset_preview_only": True,
    }


def _build_proposed_preset_update_preview(preset: Dict[str, Any], editable_rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    proposed_fields = {
        row.get("field_id"): row.get("proposed_value", {}).get("preview")
        for row in editable_rows
        if row.get("field_id")
    }

    identity = {
        "pack": PACK_ID,
        "preset": preset.get("saved_view_preset_id"),
        "proposed": proposed_fields,
    }

    return {
        "proposed_update_preview_id": f"saved_view_preset_proposed_update_preview_{_stable_hash(identity, 18)}",
        "saved_view_preset_id": _safe_text(preset.get("saved_view_preset_id")),
        "current_snapshot": {
            "label": _safe_text(preset.get("label")),
            "description": _safe_text(preset.get("description")),
            "filter_lane_id": _safe_text(preset.get("filter_lane_id")),
            "view_priority": _safe_text(preset.get("view_priority")),
            "is_default": bool(preset.get("is_default", False)),
        },
        "proposed_snapshot": proposed_fields,
        "changed_field_count": len([row for row in editable_rows if row.get("changed") is True]),
        "unchanged_field_count": len([row for row in editable_rows if row.get("changed") is False]),
        "update_status": "saved_view_preset_proposed_update_preview_ready",
        "update_result_type": "owner_note_saved_view_preset_proposed_update_preview",
        "validation": {
            "valid": True,
            "message": "Preview update is valid but persistence is blocked.",
            "safe_preview_only": True,
        },
        "save_allowed_now": False,
        "apply_allowed_now": False,
        "persist_allowed_now": False,
        "saved_view_write_allowed_now": False,
        "user_preference_write_allowed_now": False,
        "filter_preference_save_allowed_now": False,
        "navigation_persistence_allowed_now": False,
        "drawer_selection_save_allowed_now": False,
        "real_saved_view_written": False,
        "real_user_preference_written": False,
        "real_filter_preference_saved": False,
        "real_navigation_state_persisted": False,
        "real_drawer_selection_saved": False,
        "real_history_written": False,
        "real_version_written": False,
        "simulated_only": True,
        "saved_view_preset_detail_preview_only": True,
        "saved_view_preset_edit_preview_only": True,
        "saved_navigation_preview_only": True,
        "saved_filter_preset_preview_only": True,
        "navigation_preview_only": True,
        "filter_navigation_preview_only": True,
        "saved_view_preview_only": True,
        "filter_preset_preview_only": True,
    }


def _build_preset_detail_edit_drawer(preset: Dict[str, Any], sequence: int) -> Dict[str, Any]:
    preset = dict(preset or {})
    editable_rows = [
        _build_editable_field_row(preset, field_id)
        for field_id in EDITABLE_PRESET_FIELDS
    ]

    proposed_update = _build_proposed_preset_update_preview(preset, editable_rows)

    identity = {
        "pack": PACK_ID,
        "preset": preset.get("saved_view_preset_id"),
        "sequence": sequence,
    }

    drawer_id = f"saved_view_preset_detail_edit_drawer_{_stable_hash(identity, 18)}"

    drawer_sections = [
        {
            "section_id": "preset_identity",
            "title": "Preset Identity",
            "safe_for_preview": True,
            "content": {
                "saved_view_preset_id": _safe_text(preset.get("saved_view_preset_id")),
                "label": _safe_text(preset.get("label")),
                "filter_lane_id": _safe_text(preset.get("filter_lane_id")),
            },
        },
        {
            "section_id": "matched_drawers",
            "title": "Matched Drawers",
            "safe_for_preview": True,
            "content": {
                "matched_drawer_count": int(preset.get("matched_drawer_count") or 0),
                "default_selected_version_detail_drawer_id": _safe_text(preset.get("default_selected_version_detail_drawer_id")),
            },
        },
        {
            "section_id": "editable_fields",
            "title": "Editable Fields",
            "safe_for_preview": True,
            "content": {
                "editable_field_count": len(editable_rows),
                "field_ids": EDITABLE_PRESET_FIELDS,
            },
        },
        {
            "section_id": "proposed_update",
            "title": "Proposed Update",
            "safe_for_preview": True,
            "content": {
                "changed_field_count": proposed_update.get("changed_field_count"),
                "validation": proposed_update.get("validation"),
            },
        },
        {
            "section_id": "blocked_persistence",
            "title": "Blocked Persistence",
            "safe_for_preview": True,
            "content": {
                "save_allowed_now": False,
                "apply_allowed_now": False,
                "persist_allowed_now": False,
                "real_saved_view_written": False,
                "real_user_preference_written": False,
            },
        },
        {
            "section_id": "safety_flags",
            "title": "Safety Flags",
            "safe_for_preview": True,
            "content": {
                "simulated_only": True,
                "saved_view_preset_detail_preview_only": True,
                "saved_view_preset_edit_preview_only": True,
                "raw_evidence_reveal_allowed": False,
            },
        },
    ]

    return {
        "saved_view_preset_detail_edit_drawer_id": drawer_id,
        "sequence": int(sequence),
        "saved_view_preset_id": _safe_text(preset.get("saved_view_preset_id")),
        "saved_view_preset_preview_id": _safe_text(preset.get("saved_view_preset_preview_id")),
        "label": _safe_text(preset.get("label")),
        "description": _safe_text(preset.get("description")),
        "filter_lane_id": _safe_text(preset.get("filter_lane_id")),
        "filter_lane_label": _safe_text(preset.get("filter_lane_label")),
        "view_priority": _safe_text(preset.get("view_priority")),
        "is_default": bool(preset.get("is_default", False)),
        "matched_drawer_count": int(preset.get("matched_drawer_count") or 0),
        "matched_version_detail_drawer_ids": preset.get("matched_version_detail_drawer_ids", []),
        "default_selected_version_detail_drawer_id": _safe_text(preset.get("default_selected_version_detail_drawer_id")),
        "default_selected_saved_view_id": _safe_text(preset.get("default_selected_saved_view_id")),
        "drawer_status": "saved_view_preset_detail_edit_preview_ready",
        "drawer_result_type": "owner_note_saved_view_preset_detail_edit_drawer_preview",
        "editable_field_rows": editable_rows,
        "editable_field_count": len(editable_rows),
        "proposed_update_preview": proposed_update,
        "drawer_sections": drawer_sections,
        "drawer_section_count": len(drawer_sections),
        "edit_allowed_in_preview": True,
        "preset_detail_allowed_in_preview": True,
        "save_allowed_now": False,
        "apply_allowed_now": False,
        "persist_allowed_now": False,
        "saved_view_write_allowed_now": False,
        "user_preference_write_allowed_now": False,
        "filter_preference_save_allowed_now": False,
        "navigation_persistence_allowed_now": False,
        "drawer_selection_save_allowed_now": False,
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
        "real_note_written": False,
        "real_draft_saved": False,
        "real_approval_executed": False,
        "real_policy_change_executed": False,
        "real_permission_change_executed": False,
        "real_access_granted": False,
        "real_enforcement_executed": False,
        "real_audit_written": False,
        "real_receipt_written": False,
        "real_archive_written": False,
        "real_vault_written": False,
        "real_expiration_enforced": False,
        "real_recheck_executed": False,
        "real_renewal_executed": False,
        "real_queue_action_executed": False,
        "real_owner_review_completed": False,
        "real_owner_approval_executed": False,
        "real_owner_rejection_executed": False,
        "real_owner_acknowledgement_executed": False,
        "real_evidence_revealed": False,
        "simulated_only": True,
        "saved_view_preset_detail_preview_only": True,
        "saved_view_preset_edit_preview_only": True,
        "saved_navigation_preview_only": True,
        "saved_filter_preset_preview_only": True,
        "navigation_preview_only": True,
        "filter_navigation_preview_only": True,
        "version_detail_preview_only": True,
        "compare_view_preview_only": True,
        "version_preview_only": True,
        "edit_history_preview_only": True,
        "rollback_preview_only": True,
        "compare_preview_only": True,
        "edit_preview_only": True,
        "detail_drawer_preview_only": True,
        "owner_note_preview_only": True,
        "review_draft_preview_only": True,
        "saved_view_preview_only": True,
        "filter_preset_preview_only": True,
        "filter_preview_only": True,
        "search_facet_preview_only": True,
        "lookup_preview_only": True,
        "detail_preview_only": True,
        "evidence_drawer_preview_only": True,
        "owner_review_preview_only": True,
        "queue_preview_only": True,
        "renewal_preview_only": True,
        "recheck_preview_only": True,
        "expiration_preview_only": True,
        "vault_preview_only": True,
        "index_preview_only": True,
        "receipt_preview_only": True,
        "approval_preview_only": True,
        "evidence_preview_only": True,
        "cached_non_recursive": True,
    }


def _build_detail_edit_indexes(drawers: List[Dict[str, Any]]) -> Dict[str, Any]:
    indexes = {
        "by_detail_edit_drawer_id": {},
        "by_saved_view_preset_id": {},
        "by_filter_lane_id": {},
        "by_view_priority": {},
        "by_default_state": {},
        "by_drawer_status": {},
    }

    for drawer in drawers:
        drawer_id = _safe_text(drawer.get("saved_view_preset_detail_edit_drawer_id"))
        if drawer_id:
            indexes["by_detail_edit_drawer_id"][drawer_id] = drawer

        preset_id = _safe_text(drawer.get("saved_view_preset_id"))
        if preset_id:
            indexes["by_saved_view_preset_id"][preset_id] = drawer

        lane_id = _safe_text(drawer.get("filter_lane_id")) or "unknown"
        indexes["by_filter_lane_id"].setdefault(lane_id, []).append(drawer)

        priority = _safe_text(drawer.get("view_priority")) or "unknown"
        indexes["by_view_priority"].setdefault(priority, []).append(drawer)

        default_key = "default" if drawer.get("is_default") else "not_default"
        indexes["by_default_state"].setdefault(default_key, []).append(drawer)

        status = _safe_text(drawer.get("drawer_status")) or "unknown"
        indexes["by_drawer_status"].setdefault(status, []).append(drawer)

    return indexes


@lru_cache(maxsize=1)
def build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_preview_payload_cached() -> Dict[str, Any]:
    pack_174_payload = _load_pack_174_payload(force_refresh=False)
    presets = pack_174_payload.get("saved_view_presets", [])

    if not isinstance(presets, list):
        presets = []

    sorted_presets = sorted(
        [preset for preset in presets if isinstance(preset, dict)],
        key=lambda item: (
            0 if item.get("is_default") else 1,
            _priority_rank(item.get("view_priority")),
            _safe_text(item.get("saved_view_preset_id")),
        ),
    )

    drawers = [
        _build_preset_detail_edit_drawer(preset, sequence=idx)
        for idx, preset in enumerate(sorted_presets, start=1)
    ]

    indexes = _build_detail_edit_indexes(drawers)

    drawer_status_counts = _count_by(drawers, "drawer_status")
    view_priority_counts = _count_by(drawers, "view_priority")
    filter_lane_counts = _count_by(drawers, "filter_lane_id")
    default_state_counts = {
        "default": len([drawer for drawer in drawers if drawer.get("is_default") is True]),
        "not_default": len([drawer for drawer in drawers if drawer.get("is_default") is False]),
    }

    total_editable_fields = sum(int(drawer.get("editable_field_count") or 0) for drawer in drawers)
    total_drawer_sections = sum(int(drawer.get("drawer_section_count") or 0) for drawer in drawers)
    total_changed_fields = sum(int(drawer.get("proposed_update_preview", {}).get("changed_field_count") or 0) for drawer in drawers)

    drawer_preview = {
        drawer.get("saved_view_preset_id"): drawer
        for drawer in drawers
        if drawer.get("saved_view_preset_id")
    }

    readiness_checks = {
        "pack_174_ready": pack_174_payload.get("status") == "ready",
        "has_detail_edit_drawers": len(drawers) >= 1,
        "drawer_count_matches_presets": len(drawers) == len(presets),
        "all_drawers_ready": all(drawer.get("drawer_status") == "saved_view_preset_detail_edit_preview_ready" for drawer in drawers),
        "all_have_five_editable_fields": all(int(drawer.get("editable_field_count") or 0) == 5 for drawer in drawers),
        "all_have_six_drawer_sections": all(int(drawer.get("drawer_section_count") or 0) >= 6 for drawer in drawers),
        "all_have_proposed_update_preview": all(drawer.get("proposed_update_preview", {}).get("update_status") == "saved_view_preset_proposed_update_preview_ready" for drawer in drawers),
        "all_expected_editable_fields_present": all(
            set(EDITABLE_PRESET_FIELDS).issubset({row.get("field_id") for row in drawer.get("editable_field_rows", [])})
            for drawer in drawers
        ),
        "all_simulated_only": all(drawer.get("simulated_only") is True for drawer in drawers),
        "all_saved_view_preset_detail_preview_only": all(drawer.get("saved_view_preset_detail_preview_only") is True for drawer in drawers),
        "all_saved_view_preset_edit_preview_only": all(drawer.get("saved_view_preset_edit_preview_only") is True for drawer in drawers),
        "all_saved_navigation_preview_only": all(drawer.get("saved_navigation_preview_only") is True for drawer in drawers),
        "all_saved_filter_preset_preview_only": all(drawer.get("saved_filter_preset_preview_only") is True for drawer in drawers),
        "all_navigation_preview_only": all(drawer.get("navigation_preview_only") is True for drawer in drawers),
        "all_filter_navigation_preview_only": all(drawer.get("filter_navigation_preview_only") is True for drawer in drawers),
        "all_version_detail_preview_only": all(drawer.get("version_detail_preview_only") is True for drawer in drawers),
        "all_compare_view_preview_only": all(drawer.get("compare_view_preview_only") is True for drawer in drawers),
        "all_version_preview_only": all(drawer.get("version_preview_only") is True for drawer in drawers),
        "all_edit_history_preview_only": all(drawer.get("edit_history_preview_only") is True for drawer in drawers),
        "all_rollback_preview_only": all(drawer.get("rollback_preview_only") is True for drawer in drawers),
        "all_compare_preview_only": all(drawer.get("compare_preview_only") is True for drawer in drawers),
        "all_edit_preview_only": all(drawer.get("edit_preview_only") is True for drawer in drawers),
        "all_detail_drawer_preview_only": all(drawer.get("detail_drawer_preview_only") is True for drawer in drawers),
        "all_owner_note_preview_only": all(drawer.get("owner_note_preview_only") is True for drawer in drawers),
        "all_review_draft_preview_only": all(drawer.get("review_draft_preview_only") is True for drawer in drawers),
        "all_saved_view_preview_only": all(drawer.get("saved_view_preview_only") is True for drawer in drawers),
        "all_filter_preset_preview_only": all(drawer.get("filter_preset_preview_only") is True for drawer in drawers),
        "all_filter_preview_only": all(drawer.get("filter_preview_only") is True for drawer in drawers),
        "all_search_facet_preview_only": all(drawer.get("search_facet_preview_only") is True for drawer in drawers),
        "all_lookup_preview_only": all(drawer.get("lookup_preview_only") is True for drawer in drawers),
        "all_detail_preview_only": all(drawer.get("detail_preview_only") is True for drawer in drawers),
        "all_evidence_drawer_preview_only": all(drawer.get("evidence_drawer_preview_only") is True for drawer in drawers),
        "all_owner_review_preview_only": all(drawer.get("owner_review_preview_only") is True for drawer in drawers),
        "all_queue_preview_only": all(drawer.get("queue_preview_only") is True for drawer in drawers),
        "all_renewal_preview_only": all(drawer.get("renewal_preview_only") is True for drawer in drawers),
        "all_recheck_preview_only": all(drawer.get("recheck_preview_only") is True for drawer in drawers),
        "all_expiration_preview_only": all(drawer.get("expiration_preview_only") is True for drawer in drawers),
        "all_vault_preview_only": all(drawer.get("vault_preview_only") is True for drawer in drawers),
        "all_index_preview_only": all(drawer.get("index_preview_only") is True for drawer in drawers),
        "all_receipt_preview_only": all(drawer.get("receipt_preview_only") is True for drawer in drawers),
        "all_approval_preview_only": all(drawer.get("approval_preview_only") is True for drawer in drawers),
        "all_evidence_preview_only": all(drawer.get("evidence_preview_only") is True for drawer in drawers),
        "no_real_saved_view_written": all(drawer.get("real_saved_view_written") is False for drawer in drawers),
        "no_real_user_preference_written": all(drawer.get("real_user_preference_written") is False for drawer in drawers),
        "no_real_filter_preference_saved": all(drawer.get("real_filter_preference_saved") is False for drawer in drawers),
        "no_real_navigation_state_persisted": all(drawer.get("real_navigation_state_persisted") is False for drawer in drawers),
        "no_real_drawer_selection_saved": all(drawer.get("real_drawer_selection_saved") is False for drawer in drawers),
        "no_real_history_written": all(drawer.get("real_history_written") is False for drawer in drawers),
        "no_real_version_written": all(drawer.get("real_version_written") is False for drawer in drawers),
        "no_real_version_saved": all(drawer.get("real_version_saved") is False for drawer in drawers),
        "no_real_rollback_executed": all(drawer.get("real_rollback_executed") is False for drawer in drawers),
        "no_real_restore_executed": all(drawer.get("real_restore_executed") is False for drawer in drawers),
        "no_real_edit_persisted": all(drawer.get("real_edit_persisted") is False for drawer in drawers),
        "no_real_note_written": all(drawer.get("real_note_written") is False for drawer in drawers),
        "no_real_draft_saved": all(drawer.get("real_draft_saved") is False for drawer in drawers),
        "no_real_approval_executed": all(drawer.get("real_approval_executed") is False for drawer in drawers),
        "no_real_policy_change": all(drawer.get("real_policy_change_executed") is False for drawer in drawers),
        "no_real_permission_change": all(drawer.get("real_permission_change_executed") is False for drawer in drawers),
        "no_real_access_granted": all(drawer.get("real_access_granted") is False for drawer in drawers),
        "no_real_enforcement": all(drawer.get("real_enforcement_executed") is False for drawer in drawers),
        "no_real_audit_written": all(drawer.get("real_audit_written") is False for drawer in drawers),
        "no_real_receipt_written": all(drawer.get("real_receipt_written") is False for drawer in drawers),
        "no_real_archive_written": all(drawer.get("real_archive_written") is False for drawer in drawers),
        "no_real_vault_written": all(drawer.get("real_vault_written") is False for drawer in drawers),
        "no_real_expiration_enforced": all(drawer.get("real_expiration_enforced") is False for drawer in drawers),
        "no_real_recheck_executed": all(drawer.get("real_recheck_executed") is False for drawer in drawers),
        "no_real_renewal_executed": all(drawer.get("real_renewal_executed") is False for drawer in drawers),
        "no_real_queue_action_executed": all(drawer.get("real_queue_action_executed") is False for drawer in drawers),
        "no_real_owner_review_completed": all(drawer.get("real_owner_review_completed") is False for drawer in drawers),
        "no_real_owner_approval_executed": all(drawer.get("real_owner_approval_executed") is False for drawer in drawers),
        "no_real_owner_rejection_executed": all(drawer.get("real_owner_rejection_executed") is False for drawer in drawers),
        "no_real_owner_acknowledgement_executed": all(drawer.get("real_owner_acknowledgement_executed") is False for drawer in drawers),
        "no_real_evidence_revealed": all(drawer.get("real_evidence_revealed") is False for drawer in drawers),
        "all_save_actions_blocked": all(drawer.get("save_allowed_now") is False for drawer in drawers),
        "all_apply_actions_blocked": all(drawer.get("apply_allowed_now") is False for drawer in drawers),
        "all_persist_actions_blocked": all(drawer.get("persist_allowed_now") is False for drawer in drawers),
        "all_saved_view_writes_blocked": all(drawer.get("saved_view_write_allowed_now") is False for drawer in drawers),
        "all_user_preference_writes_blocked": all(drawer.get("user_preference_write_allowed_now") is False for drawer in drawers),
        "all_filter_preference_saves_blocked": all(drawer.get("filter_preference_save_allowed_now") is False for drawer in drawers),
        "all_navigation_persistence_blocked": all(drawer.get("navigation_persistence_allowed_now") is False for drawer in drawers),
        "all_drawer_selection_saves_blocked": all(drawer.get("drawer_selection_save_allowed_now") is False for drawer in drawers),
        "all_raw_evidence_reveal_blocked": all(drawer.get("raw_evidence_reveal_allowed") is False for drawer in drawers),
        "all_raw_evidence_lookup_blocked": all(drawer.get("raw_evidence_lookup_allowed") is False for drawer in drawers),
        "default_all_compare_drawers_drawer_present": "default_all_compare_drawers" in drawer_preview,
        "owner_review_focus_drawer_present": "owner_review_focus" in drawer_preview,
        "critical_priority_focus_drawer_present": "critical_priority_focus" in drawer_preview,
        "high_priority_focus_drawer_present": "high_priority_focus" in drawer_preview,
        "monitor_only_focus_drawer_present": "monitor_only_focus" in drawer_preview,
        "safe_preview_focus_drawer_present": "safe_preview_focus" in drawer_preview,
        "endpoint": SAVED_VIEW_PRESET_DETAIL_EDIT_ENDPOINT,
        "cached_non_recursive": True,
    }

    bool_checks = [
        value
        for value in readiness_checks.values()
        if isinstance(value, bool)
    ]
    readiness_score = 100 if all(bool_checks) else 90

    return {
        "pack_id": PACK_ID,
        "pack_number": 175,
        "status": "ready" if readiness_score == 100 else "review",
        "title": "Owner Note Saved View Preset Detail Drawer / Edit Preview",
        "endpoint": SAVED_VIEW_PRESET_DETAIL_EDIT_ENDPOINT,
        "source_endpoint": SAVED_VIEW_FILTER_PRESET_ENDPOINT,
        "generated_at": _utc_now(),
        "simulated_only": True,
        "saved_view_preset_detail_preview_only": True,
        "saved_view_preset_edit_preview_only": True,
        "saved_navigation_preview_only": True,
        "saved_filter_preset_preview_only": True,
        "navigation_preview_only": True,
        "filter_navigation_preview_only": True,
        "version_detail_preview_only": True,
        "compare_view_preview_only": True,
        "version_preview_only": True,
        "edit_history_preview_only": True,
        "rollback_preview_only": True,
        "compare_preview_only": True,
        "edit_preview_only": True,
        "detail_drawer_preview_only": True,
        "owner_note_preview_only": True,
        "review_draft_preview_only": True,
        "saved_view_preview_only": True,
        "filter_preset_preview_only": True,
        "filter_preview_only": True,
        "search_facet_preview_only": True,
        "lookup_preview_only": True,
        "detail_preview_only": True,
        "evidence_drawer_preview_only": True,
        "owner_review_preview_only": True,
        "queue_preview_only": True,
        "renewal_preview_only": True,
        "recheck_preview_only": True,
        "expiration_preview_only": True,
        "vault_preview_only": True,
        "index_preview_only": True,
        "receipt_preview_only": True,
        "approval_preview_only": True,
        "evidence_preview_only": True,
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
        "real_note_written": False,
        "real_draft_saved": False,
        "real_approval_executed": False,
        "real_policy_change_executed": False,
        "real_permission_change_executed": False,
        "real_access_granted": False,
        "real_enforcement_executed": False,
        "real_audit_written": False,
        "real_receipt_written": False,
        "real_archive_written": False,
        "real_vault_written": False,
        "real_expiration_enforced": False,
        "real_recheck_executed": False,
        "real_renewal_executed": False,
        "real_queue_action_executed": False,
        "real_owner_review_completed": False,
        "real_owner_approval_executed": False,
        "real_owner_rejection_executed": False,
        "real_owner_acknowledgement_executed": False,
        "real_evidence_revealed": False,
        "cached_non_recursive": True,
        "source_pack_174": {
            "status": pack_174_payload.get("status"),
            "readiness_score": pack_174_payload.get("summary", {}).get("readiness_score"),
            "saved_view_preset_count": pack_174_payload.get("summary", {}).get("saved_view_preset_count"),
            "preset_chip_count": pack_174_payload.get("summary", {}).get("preset_chip_count"),
            "preset_detail_count": pack_174_payload.get("summary", {}).get("preset_detail_count"),
        },
        "summary": {
            "detail_edit_drawer_count": len(drawers),
            "source_saved_view_preset_count": len(presets),
            "editable_field_row_count": total_editable_fields,
            "drawer_section_count": total_drawer_sections,
            "changed_field_count": total_changed_fields,
            "editable_field_count": len(EDITABLE_PRESET_FIELDS),
            "drawer_status_counts": drawer_status_counts,
            "view_priority_counts": view_priority_counts,
            "filter_lane_counts": filter_lane_counts,
            "default_state_counts": default_state_counts,
            "readiness_score": readiness_score,
            "readiness_label": "Owner note saved view preset detail/edit preview ready" if readiness_score == 100 else "Owner note saved view preset detail/edit preview needs review",
        },
        "readiness_checks": readiness_checks,
        "editable_preset_fields": EDITABLE_PRESET_FIELDS,
        "field_labels": FIELD_LABELS,
        "field_types": FIELD_TYPES,
        "allowed_view_priorities": ALLOWED_VIEW_PRIORITIES,
        "allowed_filter_lanes": ALLOWED_FILTER_LANES,
        "detail_edit_drawers": drawers,
        "drawer_preview": drawer_preview,
        "detail_edit_indexes": indexes,
    }


def build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_preview_payload(force_refresh: bool = False) -> Dict[str, Any]:
    if force_refresh:
        build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_preview_payload_cached.cache_clear()
    return copy.deepcopy(build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_preview_payload_cached())


def get_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_preview_payload(force_refresh: bool = False) -> Dict[str, Any]:
    return build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_preview_payload(force_refresh=force_refresh)


def build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_preview_status_bridge(force_refresh: bool = False) -> Dict[str, Any]:
    payload = build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_preview_payload(force_refresh=force_refresh)
    summary = payload.get("summary", {})

    return {
        "pack_id": PACK_ID,
        "pack_number": 175,
        "status": payload.get("status", "ready"),
        "endpoint": payload.get("endpoint", SAVED_VIEW_PRESET_DETAIL_EDIT_ENDPOINT),
        "source_endpoint": payload.get("source_endpoint", SAVED_VIEW_FILTER_PRESET_ENDPOINT),
        "readiness_score": summary.get("readiness_score", 100),
        "readiness_label": summary.get("readiness_label", "Owner note saved view preset detail/edit preview ready"),
        "detail_edit_drawer_count": summary.get("detail_edit_drawer_count", 0),
        "source_saved_view_preset_count": summary.get("source_saved_view_preset_count", 0),
        "editable_field_row_count": summary.get("editable_field_row_count", 0),
        "drawer_section_count": summary.get("drawer_section_count", 0),
        "changed_field_count": summary.get("changed_field_count", 0),
        "editable_field_count": summary.get("editable_field_count", 0),
        "drawer_status_counts": summary.get("drawer_status_counts", {}),
        "view_priority_counts": summary.get("view_priority_counts", {}),
        "filter_lane_counts": summary.get("filter_lane_counts", {}),
        "default_state_counts": summary.get("default_state_counts", {}),
        "simulated_only": True,
        "saved_view_preset_detail_preview_only": True,
        "saved_view_preset_edit_preview_only": True,
        "saved_navigation_preview_only": True,
        "saved_filter_preset_preview_only": True,
        "navigation_preview_only": True,
        "filter_navigation_preview_only": True,
        "saved_view_preview_only": True,
        "filter_preset_preview_only": True,
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
        "cached_non_recursive": True,
    }


def get_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_preview_status_bridge(force_refresh: bool = False) -> Dict[str, Any]:
    return build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_preview_status_bridge(force_refresh=force_refresh)


def build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_preview_quick_action() -> Dict[str, Any]:
    bridge = build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_preview_status_bridge()
    return {
        "id": "policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_preview",
        "label": "Owner Note Preset Edit Preview",
        "title": "Owner Note Saved View Preset Detail Drawer / Edit Preview",
        "href": SAVED_VIEW_PRESET_DETAIL_EDIT_ENDPOINT,
        "endpoint": SAVED_VIEW_PRESET_DETAIL_EDIT_ENDPOINT,
        "description": "Preview saved view preset detail drawers, editable field rows, proposed update previews, and blocked persistence.",
        "status": bridge.get("status", "ready"),
        "pack": "Pack 175",
        "category": "policy",
        "simulated_only": True,
        "saved_view_preset_detail_preview_only": True,
        "saved_view_preset_edit_preview_only": True,
        "saved_navigation_preview_only": True,
        "saved_filter_preset_preview_only": True,
        "navigation_preview_only": True,
        "filter_navigation_preview_only": True,
        "saved_view_preview_only": True,
        "filter_preset_preview_only": True,
    }


def build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_preview_unified_owner_section() -> Dict[str, Any]:
    payload = build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_preview_payload()
    summary = payload.get("summary", {})
    checks = payload.get("readiness_checks", {})

    cards = [
        {
            "id": "detail_edit_readiness",
            "title": "Detail/edit readiness",
            "value": summary.get("readiness_score", 100),
            "label": summary.get("readiness_label", "Owner note saved view preset detail/edit preview ready"),
        },
        {
            "id": "detail_edit_drawers",
            "title": "Detail edit drawers",
            "value": summary.get("detail_edit_drawer_count", 0),
            "label": "Preset edit drawers",
        },
        {
            "id": "editable_fields",
            "title": "Editable fields",
            "value": summary.get("editable_field_row_count", 0),
            "label": "Preview field rows",
        },
        {
            "id": "changed_fields",
            "title": "Changed fields",
            "value": summary.get("changed_field_count", 0),
            "label": "Proposed preview updates",
        },
        {
            "id": "save_blocked",
            "title": "Save/apply",
            "value": "Blocked" if checks.get("all_save_actions_blocked") and checks.get("all_apply_actions_blocked") else "Review",
            "label": "No real persistence",
        },
        {
            "id": "preference_write",
            "title": "Preference write",
            "value": "Blocked" if checks.get("all_user_preference_writes_blocked") else "Review",
            "label": "No real preference write",
        },
    ]

    return {
        "section_id": "policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_preview",
        "title": "Owner Note Preset Edit Preview",
        "subtitle": "Preview saved view preset detail drawers, editable field rows, proposed update previews, and blocked persistence.",
        "status": payload.get("status", "ready"),
        "href": SAVED_VIEW_PRESET_DETAIL_EDIT_ENDPOINT,
        "cards": cards,
        "simulated_only": True,
        "saved_view_preset_detail_preview_only": True,
        "saved_view_preset_edit_preview_only": True,
        "saved_navigation_preview_only": True,
        "saved_filter_preset_preview_only": True,
        "navigation_preview_only": True,
        "filter_navigation_preview_only": True,
        "saved_view_preview_only": True,
        "filter_preset_preview_only": True,
        "cached_non_recursive": True,
    }


def build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_preview_html_section() -> str:
    section = build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_preview_unified_owner_section()
    cards = section.get("cards", [])

    card_html = []
    for card in cards:
        card_html.append(
            f"""
            <article class="tower-card policy-change-approval-receipt-owner-note-preset-edit-card">
                <div class="tower-card-kicker">{card.get('title', '')}</div>
                <div class="tower-card-value">{card.get('value', '')}</div>
                <p>{card.get('label', '')}</p>
            </article>
            """
        )

    return f"""
    <section class="tower-section policy-change-approval-receipt-owner-note-preset-edit-section" id="policy-change-approval-receipt-owner-note-saved-view-preset-detail-edit-preview">
        <div class="tower-section-heading">
            <p class="tower-kicker">Pack 175</p>
            <h2>{section.get('title', 'Owner Note Preset Edit Preview')}</h2>
            <p>{section.get('subtitle', '')}</p>
            <a class="tower-link-pill" href="{SAVED_VIEW_PRESET_DETAIL_EDIT_ENDPOINT}">Open owner note preset edit preview JSON</a>
        </div>
        <div class="tower-card-grid">
            {''.join(card_html)}
        </div>
    </section>
    """


__all__ = [
    "PACK_ID",
    "SAVED_VIEW_PRESET_DETAIL_EDIT_ENDPOINT",
    "SAVED_VIEW_FILTER_PRESET_ENDPOINT",
    "EDITABLE_PRESET_FIELDS",
    "FIELD_LABELS",
    "FIELD_TYPES",
    "ALLOWED_VIEW_PRIORITIES",
    "ALLOWED_FILTER_LANES",
    "build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_preview_payload",
    "get_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_preview_payload",
    "build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_preview_status_bridge",
    "get_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_preview_status_bridge",
    "build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_preview_quick_action",
    "build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_preview_unified_owner_section",
    "build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_preview_html_section",
]
