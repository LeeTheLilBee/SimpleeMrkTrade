
"""
PACK 192 - Owner Note Version Compare Navigation Saved View / Filter Preset
Detail Edit History Version Detail / Compare View Preview.

Short module filename:
    tower.owner_note_vc_nav_version_compare_v192

This module sits on top of Pack 191.

Pack 191 creates preview-only edit history timelines, version cards,
field change events, and rollback/restore/compare previews.

Pack 192 creates preview-only version detail and compare-view scaffolding:
- version detail drawers
- compare rows between original and draft preview versions
- changed / unchanged compare rows
- selected version detail drawer preview
- indexes
- blocked reveal/version/save/rollback/restore/edit persistence

Important:
- simulated-only
- version-detail-preview-only
- compare-view-preview-only
- version-preview-only
- edit-history-preview-only
- rollback/restore preview only
- no raw evidence reveal
- no real history/version/rollback/restore/edit writes
- cached
- non-recursive
"""

from __future__ import annotations

import copy
import datetime
import hashlib
import importlib
from functools import lru_cache
from typing import Any, Dict, List, Tuple


PACK_ID = "PACK_192"
VERSION_COMPARE_ENDPOINT = "/tower/owner-note-vc-nav-version-compare-v192.json"
SOURCE_ENDPOINT = "/tower/policy-change-approval-receipt-owner-note-saved-view-preset-detail-edit-history-version-compare-saved-view-filter-preset-detail-edit-history-version-compare-navigation-saved-view-filter-preset-detail-edit-history-version-preview.json"


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
        "version_detail_preview_only": True,
        "compare_view_preview_only": True,
        "version_preview_only": True,
        "edit_history_preview_only": True,
        "rollback_preview_only": True,
        "restore_preview_only": True,
        "compare_preview_only": True,
        "detail_edit_preview_only": True,
        "saved_view_preview_only": True,
        "filter_preset_preview_only": True,
        "navigation_preview_only": True,
        "filter_navigation_preview_only": True,
        "saved_view_preset_detail_preview_only": True,
        "saved_view_preset_edit_preview_only": True,
        "saved_navigation_preview_only": True,
        "saved_filter_preset_preview_only": True,
        "raw_evidence_reveal_allowed": False,
        "raw_evidence_lookup_allowed": False,
        "history_write_allowed_now": False,
        "version_write_allowed_now": False,
        "version_save_allowed_now": False,
        "restore_allowed_now": False,
        "rollback_allowed_now": False,
        "save_allowed_now": False,
        "persist_allowed_now": False,
        "navigation_persistence_allowed_now": False,
        "filter_preference_save_allowed_now": False,
        "drawer_selection_save_allowed_now": False,
        "saved_view_write_allowed_now": False,
        "user_preference_write_allowed_now": False,
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
        "real_raw_evidence_revealed": False,
        "cached_non_recursive": True,
    }


def _load_pack_191_payload(force_refresh: bool = False) -> Dict[str, object]:
    try:
        mod = importlib.import_module("tower.owner_note_vc_nav_detail_history_v191")
        fn = getattr(mod, "build_owner_note_vc_nav_detail_history_v191_payload", None)
        if callable(fn):
            payload = fn(force_refresh=force_refresh)
            if isinstance(payload, dict):
                return payload
    except Exception as exc:
        return {
            "pack_id": "PACK_191",
            "status": "review",
            "endpoint": SOURCE_ENDPOINT,
            "summary": {
                "edit_history_timeline_count": 0,
                "version_card_count": 0,
                "field_change_event_count": 0,
                "readiness_score": 0,
            },
            "edit_history_timelines": [],
            "load_error": str(exc),
            **_base_flags(),
        }

    return {
        "pack_id": "PACK_191",
        "status": "review",
        "endpoint": SOURCE_ENDPOINT,
        "summary": {
            "edit_history_timeline_count": 0,
            "version_card_count": 0,
            "field_change_event_count": 0,
            "readiness_score": 0,
        },
        "edit_history_timelines": [],
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


def _version_cards_by_role(timeline: Dict[str, object]) -> Dict[str, Dict[str, object]]:
    cards = timeline.get("version_cards", [])
    result = {}
    if isinstance(cards, list):
        for card in cards:
            if isinstance(card, dict):
                result[_safe_text(card.get("version_role"))] = card
    return result


def _snapshot(card: Dict[str, object]) -> Dict[str, object]:
    snap = card.get("version_snapshot", {})
    return snap if isinstance(snap, dict) else {}


def _build_compare_row(
    timeline: Dict[str, object],
    field_id: str,
    original_value: Any,
    draft_value: Any,
    sequence: int,
) -> Dict[str, object]:
    timeline_id = _safe_text(timeline.get("edit_history_timeline_id"))
    drawer_id = _safe_text(timeline.get("detail_edit_drawer_id"))
    source_kind = _safe_text(timeline.get("source_kind"))
    source_id = _safe_text(timeline.get("source_id"))
    changed = original_value != draft_value

    identity = {
        "pack": PACK_ID,
        "timeline_id": timeline_id,
        "drawer_id": drawer_id,
        "field_id": field_id,
        "sequence": sequence,
    }

    row = {
        "compare_row_id": f"version_compare_navigation_detail_compare_row_{_stable_hash(identity, 18)}",
        "edit_history_timeline_id": timeline_id,
        "detail_edit_drawer_id": drawer_id,
        "source_kind": source_kind,
        "source_id": source_id,
        "field_id": field_id,
        "field_label": field_id.replace("_", " ").title(),
        "sequence": int(sequence),
        "original_value": original_value,
        "draft_preview_value": draft_value,
        "original_display_value": _display_value(original_value),
        "draft_preview_display_value": _display_value(draft_value),
        "changed": bool(changed),
        "change_status": "changed_preview" if changed else "unchanged_preview",
        "row_status": "version_compare_navigation_version_detail_compare_row_preview_ready",
        "row_result_type": "owner_note_version_compare_navigation_version_detail_compare_row_preview",
        "safe_preview_only": True,
    }
    row.update(_base_flags())
    return row


def _build_version_detail_drawer(timeline: Dict[str, object], sequence: int) -> Dict[str, object]:
    timeline_id = _safe_text(timeline.get("edit_history_timeline_id"))
    drawer_id = _safe_text(timeline.get("detail_edit_drawer_id"))
    source_kind = _safe_text(timeline.get("source_kind"))
    source_id = _safe_text(timeline.get("source_id"))

    by_role = _version_cards_by_role(timeline)
    original_card = by_role.get("original", {})
    draft_card = by_role.get("draft_preview", {})
    compare_card = by_role.get("compare_preview", {})

    original_snapshot = _snapshot(original_card)
    draft_snapshot = _snapshot(draft_card)

    field_ids = sorted(set(original_snapshot.keys()) | set(draft_snapshot.keys()))
    compare_rows = [
        _build_compare_row(
            timeline=timeline,
            field_id=field_id,
            original_value=original_snapshot.get(field_id),
            draft_value=draft_snapshot.get(field_id),
            sequence=idx,
        )
        for idx, field_id in enumerate(field_ids, start=1)
    ]

    changed_rows = [row for row in compare_rows if row.get("changed") is True]
    unchanged_rows = [row for row in compare_rows if row.get("changed") is False]

    identity = {
        "pack": PACK_ID,
        "timeline_id": timeline_id,
        "drawer_id": drawer_id,
        "source_kind": source_kind,
        "source_id": source_id,
        "sequence": sequence,
    }

    version_detail_drawer_id = f"version_compare_navigation_version_detail_drawer_{_stable_hash(identity, 18)}"

    detail = {
        "version_detail_drawer_id": version_detail_drawer_id,
        "edit_history_timeline_id": timeline_id,
        "detail_edit_drawer_id": drawer_id,
        "source_kind": source_kind,
        "source_id": source_id,
        "sequence": int(sequence),
        "original_version_card_id": original_card.get("version_card_id"),
        "draft_preview_version_card_id": draft_card.get("version_card_id"),
        "compare_preview_version_card_id": compare_card.get("version_card_id"),
        "active_version_card_id": timeline.get("active_version_card_id"),
        "original_snapshot": original_snapshot,
        "draft_preview_snapshot": draft_snapshot,
        "compare_rows": compare_rows,
        "comparison_row_count": len(compare_rows),
        "changed_compare_row_count": len(changed_rows),
        "unchanged_compare_row_count": len(unchanged_rows),
        "rollback_preview": timeline.get("rollback_preview", {}),
        "restore_preview": timeline.get("restore_preview", {}),
        "compare_preview": timeline.get("compare_preview", {}),
        "drawer_status": "version_compare_navigation_version_detail_drawer_preview_ready",
        "drawer_result_type": "owner_note_version_compare_navigation_version_detail_drawer_preview",
        "open_allowed_in_preview": True,
        "selection_allowed_in_preview": True,
        "safe_preview_only": True,
    }
    detail.update(_base_flags())
    return detail


def _build_selected_detail_preview(drawers: List[Dict[str, object]]) -> Dict[str, object]:
    selected = drawers[0] if drawers else {}

    payload = {
        "selected_version_detail_preview_id": f"version_compare_navigation_selected_version_detail_{_stable_hash(selected.get('version_detail_drawer_id'), 18)}",
        "selected_version_detail_drawer_id": selected.get("version_detail_drawer_id"),
        "selected_edit_history_timeline_id": selected.get("edit_history_timeline_id"),
        "selected_detail_edit_drawer_id": selected.get("detail_edit_drawer_id"),
        "selected_source_kind": selected.get("source_kind"),
        "selected_source_id": selected.get("source_id"),
        "selected_comparison_row_count": selected.get("comparison_row_count"),
        "selected_changed_compare_row_count": selected.get("changed_compare_row_count"),
        "selected_unchanged_compare_row_count": selected.get("unchanged_compare_row_count"),
        "selection_status": "version_compare_navigation_selected_version_detail_preview_ready",
        "selection_result_type": "owner_note_version_compare_navigation_selected_version_detail_preview",
        "open_allowed_in_preview": True,
        "selection_allowed_in_preview": True,
        "safe_preview_only": True,
    }
    payload.update(_base_flags())
    return payload


def _build_indexes(drawers: List[Dict[str, object]]) -> Dict[str, object]:
    indexes = {
        "version_detail_drawers_by_id": {},
        "version_detail_drawers_by_timeline_id": {},
        "version_detail_drawers_by_detail_edit_drawer_id": {},
        "version_detail_drawers_by_source_kind": {},
        "version_detail_drawers_by_source_id": {},
        "compare_rows_by_id": {},
        "compare_rows_by_version_detail_drawer_id": {},
        "compare_rows_by_timeline_id": {},
        "compare_rows_by_source_kind": {},
        "compare_rows_by_field_id": {},
        "changed_compare_rows_by_drawer_id": {},
        "unchanged_compare_rows_by_drawer_id": {},
    }

    for drawer in drawers:
        detail_id = drawer.get("version_detail_drawer_id")
        timeline_id = drawer.get("edit_history_timeline_id")
        detail_edit_drawer_id = drawer.get("detail_edit_drawer_id")
        source_kind = drawer.get("source_kind")
        source_id = drawer.get("source_id")

        indexes["version_detail_drawers_by_id"][detail_id] = drawer
        indexes["version_detail_drawers_by_timeline_id"][timeline_id] = drawer
        indexes["version_detail_drawers_by_detail_edit_drawer_id"][detail_edit_drawer_id] = drawer
        indexes["version_detail_drawers_by_source_kind"].setdefault(source_kind, []).append(drawer)
        indexes["version_detail_drawers_by_source_id"][source_id] = drawer

        for row in drawer.get("compare_rows", []):
            if not isinstance(row, dict):
                continue
            row_id = row.get("compare_row_id")
            indexes["compare_rows_by_id"][row_id] = row
            indexes["compare_rows_by_version_detail_drawer_id"].setdefault(detail_id, []).append(row)
            indexes["compare_rows_by_timeline_id"].setdefault(timeline_id, []).append(row)
            indexes["compare_rows_by_source_kind"].setdefault(source_kind, []).append(row)
            indexes["compare_rows_by_field_id"].setdefault(row.get("field_id"), []).append(row)
            if row.get("changed") is True:
                indexes["changed_compare_rows_by_drawer_id"].setdefault(detail_id, []).append(row)
            else:
                indexes["unchanged_compare_rows_by_drawer_id"].setdefault(detail_id, []).append(row)

    return indexes


@lru_cache(maxsize=1)
def build_owner_note_vc_nav_version_compare_v192_payload_cached() -> Dict[str, object]:
    pack_191 = _load_pack_191_payload(force_refresh=False)

    timelines = pack_191.get("edit_history_timelines", [])
    if not isinstance(timelines, list):
        timelines = []

    timeline_items = [timeline for timeline in timelines if isinstance(timeline, dict)]

    drawers = [
        _build_version_detail_drawer(timeline, idx)
        for idx, timeline in enumerate(timeline_items, start=1)
    ]

    all_rows = []
    for drawer in drawers:
        all_rows.extend(drawer.get("compare_rows", []))

    saved_view_drawers = [drawer for drawer in drawers if drawer.get("source_kind") == "saved_view_preset"]
    filter_preset_drawers = [drawer for drawer in drawers if drawer.get("source_kind") == "filter_preset"]
    changed_rows = [row for row in all_rows if isinstance(row, dict) and row.get("changed") is True]
    unchanged_rows = [row for row in all_rows if isinstance(row, dict) and row.get("changed") is False]

    selected_preview = _build_selected_detail_preview(drawers)
    indexes = _build_indexes(drawers)

    readiness_checks = {
        "pack_191_ready": pack_191.get("status") == "ready",
        "has_timelines": len(timeline_items) >= 15,
        "has_version_detail_drawers": len(drawers) >= 15,
        "has_saved_view_version_detail_drawers": len(saved_view_drawers) == 6,
        "has_filter_preset_version_detail_drawers": len(filter_preset_drawers) >= 9,
        "version_detail_drawer_count_matches_timelines": len(drawers) == len(timeline_items),
        "all_version_detail_drawers_ready": all(drawer.get("drawer_status") == "version_compare_navigation_version_detail_drawer_preview_ready" for drawer in drawers),
        "all_version_detail_drawers_have_compare_rows": all(int(drawer.get("comparison_row_count") or 0) >= 1 for drawer in drawers),
        "has_compare_rows": len(all_rows) >= 75,
        "has_changed_compare_rows": len(changed_rows) >= 1,
        "has_unchanged_compare_rows": len(unchanged_rows) >= 1,
        "selected_version_detail_preview_ready": selected_preview.get("selection_status") == "version_compare_navigation_selected_version_detail_preview_ready",
        "version_detail_indexes_present": bool(indexes.get("version_detail_drawers_by_id")),
        "compare_row_indexes_present": bool(indexes.get("compare_rows_by_id")),
        "changed_compare_row_indexes_present": bool(indexes.get("changed_compare_rows_by_drawer_id")),
        "all_simulated_only": all(item.get("simulated_only") is True for item in drawers + all_rows),
        "all_version_detail_preview_only": all(item.get("version_detail_preview_only") is True for item in drawers + all_rows),
        "all_compare_view_preview_only": all(item.get("compare_view_preview_only") is True for item in drawers + all_rows),
        "all_version_preview_only": all(item.get("version_preview_only") is True for item in drawers + all_rows),
        "all_edit_history_preview_only": all(item.get("edit_history_preview_only") is True for item in drawers + all_rows),
        "all_detail_edit_preview_only": all(item.get("detail_edit_preview_only") is True for item in drawers + all_rows),
        "no_real_history_written": all(item.get("real_history_written") is False for item in drawers + all_rows),
        "no_real_version_written": all(item.get("real_version_written") is False for item in drawers + all_rows),
        "no_real_version_saved": all(item.get("real_version_saved") is False for item in drawers + all_rows),
        "no_real_rollback_executed": all(item.get("real_rollback_executed") is False for item in drawers + all_rows),
        "no_real_restore_executed": all(item.get("real_restore_executed") is False for item in drawers + all_rows),
        "no_real_edit_persisted": all(item.get("real_edit_persisted") is False for item in drawers + all_rows),
        "no_real_raw_evidence_revealed": all(item.get("real_raw_evidence_revealed") is False for item in drawers + all_rows),
        "all_raw_evidence_reveal_blocked": all(item.get("raw_evidence_reveal_allowed") is False for item in drawers + all_rows),
        "all_raw_evidence_lookup_blocked": all(item.get("raw_evidence_lookup_allowed") is False for item in drawers + all_rows),
        "all_version_writes_blocked": all(item.get("version_write_allowed_now") is False for item in drawers + all_rows),
        "all_version_saves_blocked": all(item.get("version_save_allowed_now") is False for item in drawers + all_rows),
        "all_rollback_actions_blocked": all(item.get("rollback_allowed_now") is False for item in drawers + all_rows),
        "all_restore_actions_blocked": all(item.get("restore_allowed_now") is False for item in drawers + all_rows),
        "all_saves_blocked": all(item.get("save_allowed_now") is False for item in drawers + all_rows),
        "all_persists_blocked": all(item.get("persist_allowed_now") is False for item in drawers + all_rows),
        "cached_non_recursive": True,
    }

    readiness_score = 100 if all(v for v in readiness_checks.values() if isinstance(v, bool)) else 90

    return {
        "pack_id": PACK_ID,
        "pack_number": 192,
        "status": "ready" if readiness_score == 100 else "review",
        "title": "Owner Note Version Compare Navigation Saved View / Filter Preset Detail Edit History Version Detail / Compare View Preview",
        "endpoint": VERSION_COMPARE_ENDPOINT,
        "source_endpoint": SOURCE_ENDPOINT,
        "generated_at": _utc_now(),
        **_base_flags(),
        "source_pack_191": {
            "status": pack_191.get("status"),
            "readiness_score": pack_191.get("summary", {}).get("readiness_score"),
            "edit_history_timeline_count": pack_191.get("summary", {}).get("edit_history_timeline_count"),
            "version_card_count": pack_191.get("summary", {}).get("version_card_count"),
            "field_change_event_count": pack_191.get("summary", {}).get("field_change_event_count"),
        },
        "summary": {
            "version_detail_drawer_count": len(drawers),
            "saved_view_version_detail_drawer_count": len(saved_view_drawers),
            "filter_preset_version_detail_drawer_count": len(filter_preset_drawers),
            "comparison_row_count": len(all_rows),
            "changed_compare_row_count": len(changed_rows),
            "unchanged_compare_row_count": len(unchanged_rows),
            "selected_version_detail_drawer_id": selected_preview.get("selected_version_detail_drawer_id"),
            "readiness_score": readiness_score,
            "readiness_label": "Owner note version compare navigation saved view/filter preset version detail compare view preview ready" if readiness_score == 100 else "Owner note version compare navigation saved view/filter preset version detail compare view preview needs review",
        },
        "readiness_checks": readiness_checks,
        "version_detail_drawers": drawers,
        "selected_version_detail_preview": selected_preview,
        "version_detail_compare_indexes": indexes,
    }


def build_owner_note_vc_nav_version_compare_v192_payload(force_refresh: bool = False) -> Dict[str, object]:
    if force_refresh:
        build_owner_note_vc_nav_version_compare_v192_payload_cached.cache_clear()
    return copy.deepcopy(build_owner_note_vc_nav_version_compare_v192_payload_cached())


def get_owner_note_vc_nav_version_compare_v192_payload(force_refresh: bool = False) -> Dict[str, object]:
    return build_owner_note_vc_nav_version_compare_v192_payload(force_refresh=force_refresh)


def build_owner_note_vc_nav_version_compare_v192_status_bridge(force_refresh: bool = False) -> Dict[str, object]:
    payload = build_owner_note_vc_nav_version_compare_v192_payload(force_refresh=force_refresh)
    summary = payload.get("summary", {})

    return {
        "pack_id": PACK_ID,
        "pack_number": 192,
        "status": payload.get("status"),
        "endpoint": payload.get("endpoint"),
        "source_endpoint": payload.get("source_endpoint"),
        "readiness_score": summary.get("readiness_score"),
        "readiness_label": summary.get("readiness_label"),
        "version_detail_drawer_count": summary.get("version_detail_drawer_count"),
        "saved_view_version_detail_drawer_count": summary.get("saved_view_version_detail_drawer_count"),
        "filter_preset_version_detail_drawer_count": summary.get("filter_preset_version_detail_drawer_count"),
        "comparison_row_count": summary.get("comparison_row_count"),
        "changed_compare_row_count": summary.get("changed_compare_row_count"),
        "unchanged_compare_row_count": summary.get("unchanged_compare_row_count"),
        "selected_version_detail_drawer_id": summary.get("selected_version_detail_drawer_id"),
        **_base_flags(),
    }


def get_owner_note_vc_nav_version_compare_v192_status_bridge(force_refresh: bool = False) -> Dict[str, object]:
    return build_owner_note_vc_nav_version_compare_v192_status_bridge(force_refresh=force_refresh)


def build_owner_note_vc_nav_version_compare_v192_quick_action() -> Dict[str, object]:
    bridge = build_owner_note_vc_nav_version_compare_v192_status_bridge()

    action = {
        "id": "owner_note_vc_nav_version_compare_v192",
        "label": "Owner Note Version Compare Detail View",
        "title": "Owner Note Version Compare Navigation Saved View / Filter Preset Version Detail Compare View Preview",
        "href": VERSION_COMPARE_ENDPOINT,
        "endpoint": VERSION_COMPARE_ENDPOINT,
        "description": "Preview version detail drawers and compare rows for saved view/filter preset detail edit history timelines.",
        "status": bridge.get("status"),
        "pack": "Pack 192",
        "category": "policy",
    }
    action.update(_base_flags())
    return action


def build_owner_note_vc_nav_version_compare_v192_unified_owner_section() -> Dict[str, object]:
    payload = build_owner_note_vc_nav_version_compare_v192_payload()
    summary = payload.get("summary", {})
    checks = payload.get("readiness_checks", {})

    section = {
        "section_id": "owner_note_vc_nav_version_compare_v192",
        "title": "Owner Note Version Compare Detail View",
        "subtitle": "Preview version detail drawers and compare rows for navigation saved view/filter preset detail edit history timelines.",
        "status": payload.get("status"),
        "href": VERSION_COMPARE_ENDPOINT,
        "cards": [
            {"id": "readiness", "title": "Compare readiness", "value": summary.get("readiness_score"), "label": summary.get("readiness_label")},
            {"id": "drawers", "title": "Version detail drawers", "value": summary.get("version_detail_drawer_count"), "label": "Version detail drawers"},
            {"id": "compare_rows", "title": "Compare rows", "value": summary.get("comparison_row_count"), "label": "Original vs draft preview rows"},
            {"id": "changed", "title": "Changed rows", "value": summary.get("changed_compare_row_count"), "label": "Changed compare rows"},
            {"id": "unchanged", "title": "Unchanged rows", "value": summary.get("unchanged_compare_row_count"), "label": "Unchanged compare rows"},
            {"id": "persistence", "title": "Persistence", "value": "Blocked" if checks.get("all_version_writes_blocked") and checks.get("all_raw_evidence_reveal_blocked") else "Review", "label": "No raw evidence/version write"},
        ],
    }
    section.update(_base_flags())
    return section


def build_owner_note_vc_nav_version_compare_v192_html_section() -> str:
    section = build_owner_note_vc_nav_version_compare_v192_unified_owner_section()
    cards = section.get("cards", [])

    card_html = []
    for card in cards:
        card_html.append(
            f"""
            <article class="tower-card owner-note-vc-nav-version-compare-v192-card">
                <div class="tower-card-kicker">{card.get('title', '')}</div>
                <div class="tower-card-value">{card.get('value', '')}</div>
                <p>{card.get('label', '')}</p>
            </article>
            """
        )

    return f"""
    <section class="tower-section owner-note-vc-nav-version-compare-v192-section" id="owner-note-vc-nav-version-compare-v192">
        <div class="tower-section-heading">
            <p class="tower-kicker">Pack 192</p>
            <h2>{section.get('title', 'Owner Note Version Compare Detail View')}</h2>
            <p>{section.get('subtitle', '')}</p>
            <a class="tower-link-pill" href="{VERSION_COMPARE_ENDPOINT}">Open version detail compare JSON</a>
        </div>
        <div class="tower-card-grid">
            {''.join(card_html)}
        </div>
    </section>
    """


__all__ = [
    "PACK_ID",
    "VERSION_COMPARE_ENDPOINT",
    "SOURCE_ENDPOINT",
    "build_owner_note_vc_nav_version_compare_v192_payload",
    "get_owner_note_vc_nav_version_compare_v192_payload",
    "build_owner_note_vc_nav_version_compare_v192_status_bridge",
    "get_owner_note_vc_nav_version_compare_v192_status_bridge",
    "build_owner_note_vc_nav_version_compare_v192_quick_action",
    "build_owner_note_vc_nav_version_compare_v192_unified_owner_section",
    "build_owner_note_vc_nav_version_compare_v192_html_section",
]
