
"""
PACK 199 - Owner Note Version Compare Navigation Selected Action Receipt
Detail Focus Preview.

Short module filename:
    tower.owner_note_vc_nav_receipt_detail_focus_v199

This module sits on top of Pack 198.

Pack 198 creates preview-only action receipt filter navigation and receipt selection.
Pack 199 creates preview-only selected action receipt detail focus scaffolding:
- selected action receipt detail focus preview
- receipt breadcrumb/navigation trail
- receipt safety detail cards
- receipt blocked/preview state focus groups
- receipt action detail panel preview
- selected receipt focus indexes
- blocked action execution/preference/navigation/drawer persistence
- blocked raw evidence reveal

Important:
- simulated-only
- receipt-detail-focus-preview-only
- receipt-safety-detail-preview-only
- action-receipt-navigation-preview-only
- receipt-selection-preview-only
- no real action executed
- no real filter preference saved
- no real navigation state persisted
- no real drawer selection saved
- no raw evidence reveal
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


PACK_ID = "PACK_199"
RECEIPT_DETAIL_FOCUS_ENDPOINT = "/tower/owner-note-vc-nav-receipt-detail-focus-v199.json"
SOURCE_ENDPOINT = "/tower/owner-note-vc-nav-action-receipt-filter-nav-v198.json"


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
        "receipt_detail_focus_preview_only": True,
        "receipt_safety_detail_preview_only": True,
        "receipt_action_panel_preview_only": True,
        "receipt_breadcrumb_preview_only": True,
        "action_receipt_navigation_preview_only": True,
        "receipt_selection_preview_only": True,
        "action_receipt_filter_preview_only": True,
        "search_facet_preview_only": True,
        "filter_preview_only": True,
        "filter_navigation_preview_only": True,
        "action_receipt_preview_only": True,
        "blocked_action_receipt_preview_only": True,
        "preview_action_receipt_preview_only": True,
        "drawer_action_preview_only": True,
        "selected_drawer_preview_only": True,
        "compare_row_focus_preview_only": True,
        "navigation_preview_only": True,
        "drawer_selection_preview_only": True,
        "version_detail_preview_only": True,
        "compare_view_preview_only": True,
        "raw_evidence_reveal_allowed": False,
        "raw_evidence_lookup_allowed": False,
        "filter_preference_save_allowed_now": False,
        "navigation_persistence_allowed_now": False,
        "drawer_selection_save_allowed_now": False,
        "saved_view_write_allowed_now": False,
        "user_preference_write_allowed_now": False,
        "history_write_allowed_now": False,
        "version_write_allowed_now": False,
        "version_save_allowed_now": False,
        "restore_allowed_now": False,
        "rollback_allowed_now": False,
        "save_allowed_now": False,
        "persist_allowed_now": False,
        "action_execution_allowed_now": False,
        "real_action_executed": False,
        "real_filter_preference_saved": False,
        "real_navigation_state_persisted": False,
        "real_drawer_selection_saved": False,
        "real_saved_view_written": False,
        "real_user_preference_written": False,
        "real_history_written": False,
        "real_version_written": False,
        "real_version_saved": False,
        "real_rollback_executed": False,
        "real_restore_executed": False,
        "real_edit_persisted": False,
        "real_raw_evidence_revealed": False,
        "cached_non_recursive": True,
    }


def _load_pack_198_payload(force_refresh: bool = False) -> Dict[str, object]:
    try:
        mod = importlib.import_module("tower.owner_note_vc_nav_action_receipt_filter_nav_v198")
        fn = getattr(mod, "build_owner_note_vc_nav_action_receipt_filter_nav_v198_payload", None)
        if callable(fn):
            payload = fn(force_refresh=force_refresh)
            if isinstance(payload, dict):
                return payload
    except Exception as exc:
        return {
            "pack_id": "PACK_198",
            "status": "review",
            "endpoint": SOURCE_ENDPOINT,
            "summary": {
                "action_receipt_navigation_item_count": 0,
                "selected_action_receipt_id": "",
                "selected_action_receipt_count": 0,
                "readiness_score": 0,
            },
            "selected_action_receipt_navigation_preview": {},
            "action_receipt_navigation_items": [],
            "action_receipt_selection_previews": [],
            "action_receipt_navigation_groups": [],
            "load_error": str(exc),
            **_base_flags(),
        }

    return {
        "pack_id": "PACK_198",
        "status": "review",
        "endpoint": SOURCE_ENDPOINT,
        "summary": {
            "action_receipt_navigation_item_count": 0,
            "selected_action_receipt_id": "",
            "selected_action_receipt_count": 0,
            "readiness_score": 0,
        },
        "selected_action_receipt_navigation_preview": {},
        "action_receipt_navigation_items": [],
        "action_receipt_selection_previews": [],
        "action_receipt_navigation_groups": [],
        **_base_flags(),
    }


def _list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _build_breadcrumb_trail(selected: Dict[str, object]) -> Dict[str, object]:
    lane_id = _safe_text(selected.get("default_action_receipt_filter_lane_id"))
    nav_id = _safe_text(selected.get("selected_action_receipt_navigation_item_id"))
    selection_id = _safe_text(selected.get("selected_action_receipt_selection_preview_id"))
    receipt_id = _safe_text(selected.get("selected_action_receipt_id"))

    crumbs = [
        {"breadcrumb_id": f"receipt_breadcrumb_filter_{_stable_hash(lane_id, 10)}", "label": "Receipt filter", "value": lane_id, "sequence": 1},
        {"breadcrumb_id": f"receipt_breadcrumb_nav_{_stable_hash(nav_id, 10)}", "label": "Receipt navigation", "value": nav_id, "sequence": 2},
        {"breadcrumb_id": f"receipt_breadcrumb_selection_{_stable_hash(selection_id, 10)}", "label": "Receipt selection", "value": selection_id, "sequence": 3},
        {"breadcrumb_id": f"receipt_breadcrumb_detail_{_stable_hash(receipt_id, 10)}", "label": "Selected receipt", "value": receipt_id, "sequence": 4},
    ]

    trail = {
        "receipt_breadcrumb_trail_id": f"version_compare_navigation_receipt_detail_breadcrumb_{_stable_hash((PACK_ID, lane_id, nav_id, selection_id, receipt_id), 18)}",
        "breadcrumb_count": len(crumbs),
        "breadcrumbs": crumbs,
        "trail_status": "version_compare_navigation_receipt_detail_breadcrumb_preview_ready",
        "trail_result_type": "owner_note_version_compare_navigation_receipt_detail_breadcrumb_preview",
        "safe_preview_only": True,
    }
    trail.update(_base_flags())
    return trail


def _build_safety_detail_cards(selected: Dict[str, object]) -> List[Dict[str, object]]:
    receipt_id = _safe_text(selected.get("selected_action_receipt_id"))

    card_defs = [
        ("execution_block", "Real action execution", "Blocked", "No action executes from this preview surface."),
        ("raw_evidence_block", "Raw evidence reveal", "Blocked", "Raw evidence remains redacted and unavailable."),
        ("preference_write_block", "Filter preference save", "Blocked", "No filter preference is written."),
        ("navigation_write_block", "Navigation persistence", "Blocked", "No navigation state is persisted."),
        ("drawer_selection_write_block", "Drawer selection save", "Blocked", "No drawer or receipt selection is saved."),
        ("receipt_preview_scope", "Receipt scope", "Preview only", "Receipt detail remains a preview-only detail focus."),
    ]

    cards = []
    for sequence, (key, title, state, description) in enumerate(card_defs, start=1):
        card = {
            "receipt_safety_detail_card_id": f"version_compare_navigation_receipt_safety_card_{_stable_hash((PACK_ID, receipt_id, key), 18)}",
            "safety_key": key,
            "title": title,
            "state": state,
            "description": description,
            "sequence": int(sequence),
            "selected_action_receipt_id": receipt_id,
            "card_status": "version_compare_navigation_receipt_safety_detail_card_preview_ready",
            "card_result_type": "owner_note_version_compare_navigation_receipt_safety_detail_card_preview",
            "safe_preview_only": True,
        }
        card.update(_base_flags())
        cards.append(card)

    return cards


def _build_focus_groups(cards: List[Dict[str, object]]) -> List[Dict[str, object]]:
    blocked = [card for card in cards if _safe_text(card.get("state")).lower() == "blocked"]
    preview = [card for card in cards if _safe_text(card.get("state")).lower() == "preview only"]

    group_defs = [
        ("blocked_safety_details", "Blocked safety details", blocked),
        ("preview_scope_details", "Preview scope details", preview),
        ("all_receipt_detail_cards", "All receipt detail cards", cards),
    ]

    groups = []
    for sequence, (key, label, items) in enumerate(group_defs, start=1):
        group = {
            "receipt_detail_focus_group_id": f"version_compare_navigation_receipt_detail_group_{_stable_hash((PACK_ID, key), 18)}",
            "receipt_detail_focus_group_key": key,
            "label": label,
            "sequence": int(sequence),
            "receipt_safety_detail_card_count": len(items),
            "receipt_safety_detail_card_ids": [item.get("receipt_safety_detail_card_id") for item in items],
            "group_status": "version_compare_navigation_receipt_detail_focus_group_preview_ready",
            "group_result_type": "owner_note_version_compare_navigation_receipt_detail_focus_group_preview",
            "safe_preview_only": True,
        }
        group.update(_base_flags())
        groups.append(group)

    return groups


def _build_receipt_action_panel(selected: Dict[str, object], cards: List[Dict[str, object]]) -> Dict[str, object]:
    receipt_id = _safe_text(selected.get("selected_action_receipt_id"))

    actions = [
        {"action_id": "preview_open_receipt_detail", "label": "Preview open receipt detail", "allowed_in_preview": True, "executes_real_action": False},
        {"action_id": "preview_show_safety_cards", "label": "Preview safety cards", "allowed_in_preview": True, "executes_real_action": False},
        {"action_id": "preview_show_breadcrumbs", "label": "Preview breadcrumbs", "allowed_in_preview": True, "executes_real_action": False},
        {"action_id": "blocked_save_receipt_selection", "label": "Save receipt selection", "allowed_in_preview": False, "executes_real_action": False},
        {"action_id": "blocked_reveal_receipt_raw_evidence", "label": "Reveal receipt raw evidence", "allowed_in_preview": False, "executes_real_action": False},
        {"action_id": "blocked_execute_receipt_action", "label": "Execute receipt action", "allowed_in_preview": False, "executes_real_action": False},
    ]

    panel = {
        "receipt_action_detail_panel_id": f"version_compare_navigation_receipt_action_panel_{_stable_hash((PACK_ID, receipt_id), 18)}",
        "selected_action_receipt_id": receipt_id,
        "action_count": len(actions),
        "actions": actions,
        "visible_safety_detail_card_count": len(cards),
        "panel_status": "version_compare_navigation_receipt_action_detail_panel_preview_ready",
        "panel_result_type": "owner_note_version_compare_navigation_receipt_action_detail_panel_preview",
        "safe_preview_only": True,
    }
    panel.update(_base_flags())
    return panel


def _build_selected_receipt_focus(selected: Dict[str, object], breadcrumb: Dict[str, object], cards: List[Dict[str, object]], groups: List[Dict[str, object]], panel: Dict[str, object]) -> Dict[str, object]:
    receipt_id = _safe_text(selected.get("selected_action_receipt_id"))

    focus = {
        "selected_receipt_detail_focus_id": f"version_compare_navigation_selected_receipt_focus_{_stable_hash((PACK_ID, receipt_id), 18)}",
        "default_action_receipt_filter_lane_id": selected.get("default_action_receipt_filter_lane_id"),
        "selected_action_receipt_navigation_item_id": selected.get("selected_action_receipt_navigation_item_id"),
        "selected_action_receipt_selection_preview_id": selected.get("selected_action_receipt_selection_preview_id"),
        "selected_action_receipt_id": receipt_id,
        "selected_action_receipt_count": selected.get("selected_action_receipt_count"),
        "receipt_breadcrumb_trail_id": breadcrumb.get("receipt_breadcrumb_trail_id"),
        "receipt_safety_detail_card_count": len(cards),
        "receipt_safety_detail_card_ids": [card.get("receipt_safety_detail_card_id") for card in cards],
        "receipt_detail_focus_group_count": len(groups),
        "receipt_detail_focus_group_ids": [group.get("receipt_detail_focus_group_id") for group in groups],
        "receipt_action_detail_panel_id": panel.get("receipt_action_detail_panel_id"),
        "focus_status": "version_compare_navigation_selected_receipt_detail_focus_preview_ready",
        "focus_result_type": "owner_note_version_compare_navigation_selected_receipt_detail_focus_preview",
        "open_allowed_in_preview": True,
        "selection_allowed_in_preview": True,
        "safe_preview_only": True,
    }
    focus.update(_base_flags())
    return focus


def _build_indexes(cards: List[Dict[str, object]], groups: List[Dict[str, object]], focus: Dict[str, object]) -> Dict[str, object]:
    indexes = {
        "receipt_safety_detail_cards_by_id": {},
        "receipt_safety_detail_cards_by_key": {},
        "receipt_safety_detail_cards_by_state": {},
        "receipt_detail_focus_groups_by_id": {},
        "receipt_detail_focus_groups_by_key": {},
        "selected_receipt_detail_focus_by_id": {},
        "selected_receipt_detail_focus_by_receipt_id": {},
    }

    for card in cards:
        indexes["receipt_safety_detail_cards_by_id"][card.get("receipt_safety_detail_card_id")] = card
        indexes["receipt_safety_detail_cards_by_key"][card.get("safety_key")] = card
        indexes["receipt_safety_detail_cards_by_state"].setdefault(card.get("state"), []).append(card)

    for group in groups:
        indexes["receipt_detail_focus_groups_by_id"][group.get("receipt_detail_focus_group_id")] = group
        indexes["receipt_detail_focus_groups_by_key"][group.get("receipt_detail_focus_group_key")] = group

    indexes["selected_receipt_detail_focus_by_id"][focus.get("selected_receipt_detail_focus_id")] = focus
    indexes["selected_receipt_detail_focus_by_receipt_id"][focus.get("selected_action_receipt_id")] = focus

    return indexes


@lru_cache(maxsize=1)
def build_owner_note_vc_nav_receipt_detail_focus_v199_payload_cached() -> Dict[str, object]:
    pack_198 = _load_pack_198_payload(force_refresh=False)

    selected = pack_198.get("selected_action_receipt_navigation_preview", {})
    if not isinstance(selected, dict):
        selected = {}

    breadcrumb = _build_breadcrumb_trail(selected)
    cards = _build_safety_detail_cards(selected)
    groups = _build_focus_groups(cards)
    panel = _build_receipt_action_panel(selected, cards)
    focus = _build_selected_receipt_focus(selected, breadcrumb, cards, groups, panel)
    indexes = _build_indexes(cards, groups, focus)

    blocked_cards = [card for card in cards if card.get("state") == "Blocked"]
    preview_cards = [card for card in cards if card.get("state") == "Preview only"]

    readiness_checks = {
        "pack_198_ready": pack_198.get("status") == "ready",
        "has_selected_action_receipt_navigation_preview": bool(selected),
        "selected_receipt_present": bool(selected.get("selected_action_receipt_id")),
        "breadcrumb_trail_ready": breadcrumb.get("trail_status") == "version_compare_navigation_receipt_detail_breadcrumb_preview_ready",
        "has_safety_detail_cards": len(cards) == 6,
        "has_blocked_safety_cards": len(blocked_cards) == 5,
        "has_preview_scope_cards": len(preview_cards) == 1,
        "all_safety_cards_ready": all(card.get("card_status") == "version_compare_navigation_receipt_safety_detail_card_preview_ready" for card in cards),
        "has_focus_groups": len(groups) == 3,
        "all_focus_groups_ready": all(group.get("group_status") == "version_compare_navigation_receipt_detail_focus_group_preview_ready" for group in groups),
        "receipt_action_panel_ready": panel.get("panel_status") == "version_compare_navigation_receipt_action_detail_panel_preview_ready",
        "selected_receipt_focus_ready": focus.get("focus_status") == "version_compare_navigation_selected_receipt_detail_focus_preview_ready",
        "focus_indexes_present": bool(indexes.get("receipt_safety_detail_cards_by_id")),
        "focus_group_indexes_present": bool(indexes.get("receipt_detail_focus_groups_by_id")),
        "selected_focus_indexes_present": bool(indexes.get("selected_receipt_detail_focus_by_id")),
        "all_simulated_only": all(item.get("simulated_only") is True for item in cards + groups),
        "all_receipt_detail_focus_preview_only": focus.get("receipt_detail_focus_preview_only") is True and all(item.get("receipt_detail_focus_preview_only") is True for item in cards + groups),
        "all_receipt_safety_detail_preview_only": all(item.get("receipt_safety_detail_preview_only") is True for item in cards + groups),
        "all_action_receipt_navigation_preview_only": all(item.get("action_receipt_navigation_preview_only") is True for item in cards + groups),
        "all_receipt_selection_preview_only": all(item.get("receipt_selection_preview_only") is True for item in cards + groups),
        "no_real_action_executed": all(item.get("real_action_executed") is False for item in cards + groups),
        "no_real_filter_preference_saved": all(item.get("real_filter_preference_saved") is False for item in cards + groups),
        "no_real_navigation_state_persisted": all(item.get("real_navigation_state_persisted") is False for item in cards + groups),
        "no_real_drawer_selection_saved": all(item.get("real_drawer_selection_saved") is False for item in cards + groups),
        "no_real_raw_evidence_revealed": all(item.get("real_raw_evidence_revealed") is False for item in cards + groups),
        "all_action_execution_blocked": all(item.get("action_execution_allowed_now") is False for item in cards + groups),
        "all_filter_preference_saves_blocked": all(item.get("filter_preference_save_allowed_now") is False for item in cards + groups),
        "all_navigation_persistence_blocked": all(item.get("navigation_persistence_allowed_now") is False for item in cards + groups),
        "all_drawer_selection_saves_blocked": all(item.get("drawer_selection_save_allowed_now") is False for item in cards + groups),
        "all_raw_evidence_reveal_blocked": all(item.get("raw_evidence_reveal_allowed") is False for item in cards + groups),
        "cached_non_recursive": True,
    }

    readiness_score = 100 if all(v for v in readiness_checks.values() if isinstance(v, bool)) else 90

    return {
        "pack_id": PACK_ID,
        "pack_number": 199,
        "status": "ready" if readiness_score == 100 else "review",
        "title": "Owner Note Version Compare Navigation Selected Action Receipt Detail Focus Preview",
        "endpoint": RECEIPT_DETAIL_FOCUS_ENDPOINT,
        "source_endpoint": SOURCE_ENDPOINT,
        "generated_at": _utc_now(),
        **_base_flags(),
        "source_pack_198": {
            "status": pack_198.get("status"),
            "readiness_score": pack_198.get("summary", {}).get("readiness_score"),
            "selected_action_receipt_id": pack_198.get("summary", {}).get("selected_action_receipt_id"),
            "selected_action_receipt_count": pack_198.get("summary", {}).get("selected_action_receipt_count"),
        },
        "summary": {
            "selected_receipt_detail_focus_count": 1 if focus else 0,
            "breadcrumb_count": breadcrumb.get("breadcrumb_count"),
            "receipt_safety_detail_card_count": len(cards),
            "blocked_safety_detail_card_count": len(blocked_cards),
            "preview_scope_detail_card_count": len(preview_cards),
            "receipt_detail_focus_group_count": len(groups),
            "receipt_action_count": panel.get("action_count"),
            "selected_action_receipt_id": selected.get("selected_action_receipt_id"),
            "selected_action_receipt_count": selected.get("selected_action_receipt_count"),
            "readiness_score": readiness_score,
            "readiness_label": "Owner note selected action receipt detail focus preview ready" if readiness_score == 100 else "Owner note selected action receipt detail focus preview needs review",
        },
        "readiness_checks": readiness_checks,
        "receipt_breadcrumb_trail": breadcrumb,
        "receipt_safety_detail_cards": cards,
        "receipt_detail_focus_groups": groups,
        "receipt_action_detail_panel": panel,
        "selected_receipt_detail_focus": focus,
        "receipt_detail_focus_indexes": indexes,
    }


def build_owner_note_vc_nav_receipt_detail_focus_v199_payload(force_refresh: bool = False) -> Dict[str, object]:
    if force_refresh:
        build_owner_note_vc_nav_receipt_detail_focus_v199_payload_cached.cache_clear()
    return copy.deepcopy(build_owner_note_vc_nav_receipt_detail_focus_v199_payload_cached())


def get_owner_note_vc_nav_receipt_detail_focus_v199_payload(force_refresh: bool = False) -> Dict[str, object]:
    return build_owner_note_vc_nav_receipt_detail_focus_v199_payload(force_refresh=force_refresh)


def build_owner_note_vc_nav_receipt_detail_focus_v199_status_bridge(force_refresh: bool = False) -> Dict[str, object]:
    payload = build_owner_note_vc_nav_receipt_detail_focus_v199_payload(force_refresh=force_refresh)
    summary = payload.get("summary", {})

    return {
        "pack_id": PACK_ID,
        "pack_number": 199,
        "status": payload.get("status"),
        "endpoint": payload.get("endpoint"),
        "source_endpoint": payload.get("source_endpoint"),
        "readiness_score": summary.get("readiness_score"),
        "readiness_label": summary.get("readiness_label"),
        "selected_receipt_detail_focus_count": summary.get("selected_receipt_detail_focus_count"),
        "breadcrumb_count": summary.get("breadcrumb_count"),
        "receipt_safety_detail_card_count": summary.get("receipt_safety_detail_card_count"),
        "blocked_safety_detail_card_count": summary.get("blocked_safety_detail_card_count"),
        "preview_scope_detail_card_count": summary.get("preview_scope_detail_card_count"),
        "receipt_detail_focus_group_count": summary.get("receipt_detail_focus_group_count"),
        "receipt_action_count": summary.get("receipt_action_count"),
        "selected_action_receipt_id": summary.get("selected_action_receipt_id"),
        "selected_action_receipt_count": summary.get("selected_action_receipt_count"),
        **_base_flags(),
    }


def get_owner_note_vc_nav_receipt_detail_focus_v199_status_bridge(force_refresh: bool = False) -> Dict[str, object]:
    return build_owner_note_vc_nav_receipt_detail_focus_v199_status_bridge(force_refresh=force_refresh)


def build_owner_note_vc_nav_receipt_detail_focus_v199_quick_action() -> Dict[str, object]:
    bridge = build_owner_note_vc_nav_receipt_detail_focus_v199_status_bridge()

    action = {
        "id": "owner_note_vc_nav_receipt_detail_focus_v199",
        "label": "Owner Note Receipt Detail Focus",
        "title": "Owner Note Version Compare Navigation Selected Action Receipt Detail Focus Preview",
        "href": RECEIPT_DETAIL_FOCUS_ENDPOINT,
        "endpoint": RECEIPT_DETAIL_FOCUS_ENDPOINT,
        "description": "Preview selected action receipt detail, safety cards, breadcrumbs, and blocked action panel.",
        "status": bridge.get("status"),
        "pack": "Pack 199",
        "category": "policy",
    }
    action.update(_base_flags())
    return action


def build_owner_note_vc_nav_receipt_detail_focus_v199_unified_owner_section() -> Dict[str, object]:
    payload = build_owner_note_vc_nav_receipt_detail_focus_v199_payload()
    summary = payload.get("summary", {})
    checks = payload.get("readiness_checks", {})

    section = {
        "section_id": "owner_note_vc_nav_receipt_detail_focus_v199",
        "title": "Owner Note Receipt Detail Focus",
        "subtitle": "Preview selected receipt detail focus, safety cards, and blocked action panel.",
        "status": payload.get("status"),
        "href": RECEIPT_DETAIL_FOCUS_ENDPOINT,
        "cards": [
            {"id": "readiness", "title": "Focus readiness", "value": summary.get("readiness_score"), "label": summary.get("readiness_label")},
            {"id": "breadcrumbs", "title": "Breadcrumbs", "value": summary.get("breadcrumb_count"), "label": "Receipt navigation trail"},
            {"id": "safety_cards", "title": "Safety cards", "value": summary.get("receipt_safety_detail_card_count"), "label": "Receipt safety details"},
            {"id": "blocked", "title": "Blocked details", "value": summary.get("blocked_safety_detail_card_count"), "label": "Blocked safety cards"},
            {"id": "actions", "title": "Receipt actions", "value": summary.get("receipt_action_count"), "label": "Preview/blocked receipt actions"},
            {"id": "persistence", "title": "Persistence", "value": "Blocked" if checks.get("no_real_action_executed") and checks.get("all_raw_evidence_reveal_blocked") else "Review", "label": "No real execution/raw reveal"},
        ],
    }
    section.update(_base_flags())
    return section


__all__ = [
    "PACK_ID",
    "RECEIPT_DETAIL_FOCUS_ENDPOINT",
    "SOURCE_ENDPOINT",
    "build_owner_note_vc_nav_receipt_detail_focus_v199_payload",
    "get_owner_note_vc_nav_receipt_detail_focus_v199_payload",
    "build_owner_note_vc_nav_receipt_detail_focus_v199_status_bridge",
    "get_owner_note_vc_nav_receipt_detail_focus_v199_status_bridge",
    "build_owner_note_vc_nav_receipt_detail_focus_v199_quick_action",
    "build_owner_note_vc_nav_receipt_detail_focus_v199_unified_owner_section",
]
