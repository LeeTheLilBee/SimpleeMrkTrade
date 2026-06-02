
"""
PACK 195 - Owner Note Version Compare Navigation Selected Drawer
Detail / Compare Row Focus Preview.

Short module filename:
    tower.owner_note_vc_nav_drawer_focus_v195

This module sits on top of Pack 194.

Pack 194 creates preview-only filter navigation and drawer selection.
Pack 195 creates preview-only selected-drawer focus scaffolding:
- selected drawer detail focus preview
- compare row focus cards
- breadcrumb/navigation trail
- changed/unchanged focus groups
- drawer action panel preview
- selected drawer indexes
- blocked filter preference/navigation/drawer selection persistence
- blocked raw evidence reveal

Important:
- simulated-only
- selected-drawer-preview-only
- compare-row-focus-preview-only
- navigation-preview-only
- drawer-selection-preview-only
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


PACK_ID = "PACK_195"
DRAWER_FOCUS_ENDPOINT = "/tower/owner-note-vc-nav-drawer-focus-v195.json"
SOURCE_ENDPOINT = "/tower/owner-note-vc-nav-filter-nav-v194.json"


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
        "selected_drawer_preview_only": True,
        "compare_row_focus_preview_only": True,
        "drawer_action_preview_only": True,
        "breadcrumb_preview_only": True,
        "navigation_preview_only": True,
        "filter_navigation_preview_only": True,
        "drawer_selection_preview_only": True,
        "filter_preview_only": True,
        "search_facet_preview_only": True,
        "version_detail_preview_only": True,
        "compare_view_preview_only": True,
        "version_preview_only": True,
        "edit_history_preview_only": True,
        "detail_edit_preview_only": True,
        "saved_view_preview_only": True,
        "filter_preset_preview_only": True,
        "saved_navigation_preview_only": True,
        "saved_filter_preset_preview_only": True,
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


def _load_pack_194_payload(force_refresh: bool = False) -> Dict[str, object]:
    try:
        mod = importlib.import_module("tower.owner_note_vc_nav_filter_nav_v194")
        fn = getattr(mod, "build_owner_note_vc_nav_filter_nav_v194_payload", None)
        if callable(fn):
            payload = fn(force_refresh=force_refresh)
            if isinstance(payload, dict):
                return payload
    except Exception as exc:
        return {
            "pack_id": "PACK_194",
            "status": "review",
            "endpoint": SOURCE_ENDPOINT,
            "summary": {
                "navigation_item_count": 0,
                "drawer_selection_preview_count": 0,
                "selected_compare_row_count": 0,
                "readiness_score": 0,
            },
            "navigation_items": [],
            "drawer_selection_previews": [],
            "navigation_groups": [],
            "selected_navigation_preview": {},
            "filter_navigation_indexes": {},
            "load_error": str(exc),
            **_base_flags(),
        }

    return {
        "pack_id": "PACK_194",
        "status": "review",
        "endpoint": SOURCE_ENDPOINT,
        "summary": {
            "navigation_item_count": 0,
            "drawer_selection_preview_count": 0,
            "selected_compare_row_count": 0,
            "readiness_score": 0,
        },
        "navigation_items": [],
        "drawer_selection_previews": [],
        "navigation_groups": [],
        "selected_navigation_preview": {},
        "filter_navigation_indexes": {},
        **_base_flags(),
    }


def _first_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _build_breadcrumb_trail(selected: Dict[str, object]) -> Dict[str, object]:
    default_filter_lane_id = _safe_text(selected.get("default_filter_lane_id"))
    nav_item_id = _safe_text(selected.get("selected_navigation_item_id"))
    drawer_id = _safe_text(selected.get("selected_version_detail_drawer_id"))

    crumbs = [
        {
            "breadcrumb_id": f"breadcrumb_pack_193_filter_{_stable_hash(default_filter_lane_id, 10)}",
            "label": "Compare filter",
            "value": default_filter_lane_id,
            "sequence": 1,
        },
        {
            "breadcrumb_id": f"breadcrumb_pack_194_nav_{_stable_hash(nav_item_id, 10)}",
            "label": "Navigation item",
            "value": nav_item_id,
            "sequence": 2,
        },
        {
            "breadcrumb_id": f"breadcrumb_pack_195_drawer_{_stable_hash(drawer_id, 10)}",
            "label": "Selected drawer",
            "value": drawer_id,
            "sequence": 3,
        },
    ]

    payload = {
        "breadcrumb_trail_id": f"version_compare_navigation_drawer_focus_breadcrumb_{_stable_hash((PACK_ID, default_filter_lane_id, nav_item_id, drawer_id), 18)}",
        "breadcrumb_count": len(crumbs),
        "breadcrumbs": crumbs,
        "trail_status": "version_compare_navigation_drawer_focus_breadcrumb_preview_ready",
        "trail_result_type": "owner_note_version_compare_navigation_drawer_focus_breadcrumb_preview",
        "safe_preview_only": True,
    }
    payload.update(_base_flags())
    return payload


def _build_compare_row_focus_card(row_id: str, sequence: int, selected_drawer_id: str) -> Dict[str, object]:
    # Pack 194 only carries row IDs at this layer. This focus card is intentionally
    # preview-only metadata; it does not reveal raw row content or raw evidence.
    normalized_row_id = _safe_text(row_id)

    focus_state = "changed_focus_preview" if sequence % 3 == 1 else "unchanged_focus_preview"
    is_changed = focus_state == "changed_focus_preview"

    card = {
        "compare_row_focus_card_id": f"version_compare_navigation_compare_row_focus_{_stable_hash((PACK_ID, selected_drawer_id, normalized_row_id, sequence), 18)}",
        "selected_version_detail_drawer_id": selected_drawer_id,
        "compare_row_id": normalized_row_id,
        "sequence": int(sequence),
        "focus_state": focus_state,
        "changed": is_changed,
        "row_summary_label": "Changed compare row preview" if is_changed else "Unchanged compare row preview",
        "raw_content_redacted": True,
        "raw_evidence_available_in_preview": False,
        "focus_card_status": "version_compare_navigation_compare_row_focus_card_preview_ready",
        "focus_card_result_type": "owner_note_version_compare_navigation_compare_row_focus_card_preview",
        "open_allowed_in_preview": True,
        "safe_preview_only": True,
    }
    card.update(_base_flags())
    return card


def _build_focus_groups(cards: List[Dict[str, object]]) -> List[Dict[str, object]]:
    changed = [card for card in cards if card.get("changed") is True]
    unchanged = [card for card in cards if card.get("changed") is False]

    groups = []
    for sequence, (group_id, label, items) in enumerate(
        [
            ("changed_rows_focus", "Changed compare rows", changed),
            ("unchanged_rows_focus", "Unchanged compare rows", unchanged),
            ("all_rows_focus", "All compare rows", cards),
        ],
        start=1,
    ):
        group = {
            "focus_group_id": f"version_compare_navigation_focus_group_{_stable_hash((PACK_ID, group_id), 18)}",
            "focus_group_key": group_id,
            "label": label,
            "sequence": sequence,
            "focus_card_count": len(items),
            "focus_card_ids": [item.get("compare_row_focus_card_id") for item in items],
            "focus_group_status": "version_compare_navigation_compare_row_focus_group_preview_ready",
            "focus_group_result_type": "owner_note_version_compare_navigation_compare_row_focus_group_preview",
            "safe_preview_only": True,
        }
        group.update(_base_flags())
        groups.append(group)

    return groups


def _build_drawer_action_panel(selected: Dict[str, object], cards: List[Dict[str, object]]) -> Dict[str, object]:
    selected_drawer_id = _safe_text(selected.get("selected_version_detail_drawer_id"))

    actions = [
        {
            "action_id": "preview_open_drawer",
            "label": "Preview open drawer",
            "allowed_in_preview": True,
            "executes_real_action": False,
        },
        {
            "action_id": "preview_filter_changed_rows",
            "label": "Preview changed rows",
            "allowed_in_preview": True,
            "executes_real_action": False,
        },
        {
            "action_id": "preview_filter_unchanged_rows",
            "label": "Preview unchanged rows",
            "allowed_in_preview": True,
            "executes_real_action": False,
        },
        {
            "action_id": "blocked_save_selection",
            "label": "Save drawer selection",
            "allowed_in_preview": False,
            "executes_real_action": False,
        },
        {
            "action_id": "blocked_reveal_raw_evidence",
            "label": "Reveal raw evidence",
            "allowed_in_preview": False,
            "executes_real_action": False,
        },
    ]

    panel = {
        "drawer_action_panel_id": f"version_compare_navigation_drawer_action_panel_{_stable_hash((PACK_ID, selected_drawer_id), 18)}",
        "selected_version_detail_drawer_id": selected_drawer_id,
        "action_count": len(actions),
        "actions": actions,
        "visible_focus_card_count": len(cards),
        "panel_status": "version_compare_navigation_drawer_action_panel_preview_ready",
        "panel_result_type": "owner_note_version_compare_navigation_drawer_action_panel_preview",
        "safe_preview_only": True,
    }
    panel.update(_base_flags())
    return panel


def _build_selected_drawer_focus(selected: Dict[str, object], breadcrumb: Dict[str, object], cards: List[Dict[str, object]], groups: List[Dict[str, object]], panel: Dict[str, object]) -> Dict[str, object]:
    selected_drawer_id = _safe_text(selected.get("selected_version_detail_drawer_id"))
    selected_row_ids = _first_list(selected.get("selected_compare_row_ids"))

    focus = {
        "selected_drawer_focus_id": f"version_compare_navigation_selected_drawer_focus_{_stable_hash((PACK_ID, selected_drawer_id), 18)}",
        "default_filter_lane_id": selected.get("default_filter_lane_id"),
        "selected_navigation_item_id": selected.get("selected_navigation_item_id"),
        "selected_drawer_selection_preview_id": selected.get("selected_drawer_selection_preview_id"),
        "selected_version_detail_drawer_id": selected_drawer_id,
        "selected_compare_row_count": len(selected_row_ids),
        "selected_compare_row_ids": selected_row_ids,
        "breadcrumb_trail_id": breadcrumb.get("breadcrumb_trail_id"),
        "compare_row_focus_card_count": len(cards),
        "compare_row_focus_card_ids": [card.get("compare_row_focus_card_id") for card in cards],
        "focus_group_count": len(groups),
        "focus_group_ids": [group.get("focus_group_id") for group in groups],
        "drawer_action_panel_id": panel.get("drawer_action_panel_id"),
        "focus_status": "version_compare_navigation_selected_drawer_focus_preview_ready",
        "focus_result_type": "owner_note_version_compare_navigation_selected_drawer_focus_preview",
        "open_allowed_in_preview": True,
        "selection_allowed_in_preview": True,
        "safe_preview_only": True,
    }
    focus.update(_base_flags())
    return focus


def _build_indexes(cards: List[Dict[str, object]], groups: List[Dict[str, object]], focus: Dict[str, object]) -> Dict[str, object]:
    indexes = {
        "compare_row_focus_cards_by_id": {},
        "compare_row_focus_cards_by_row_id": {},
        "compare_row_focus_cards_by_changed_state": {
            "changed": [],
            "unchanged": [],
        },
        "focus_groups_by_id": {},
        "focus_groups_by_key": {},
        "selected_drawer_focus_by_id": {},
        "selected_drawer_focus_by_drawer_id": {},
    }

    for card in cards:
        card_id = card.get("compare_row_focus_card_id")
        row_id = card.get("compare_row_id")
        indexes["compare_row_focus_cards_by_id"][card_id] = card
        indexes["compare_row_focus_cards_by_row_id"][row_id] = card

        if card.get("changed") is True:
            indexes["compare_row_focus_cards_by_changed_state"]["changed"].append(card)
        else:
            indexes["compare_row_focus_cards_by_changed_state"]["unchanged"].append(card)

    for group in groups:
        indexes["focus_groups_by_id"][group.get("focus_group_id")] = group
        indexes["focus_groups_by_key"][group.get("focus_group_key")] = group

    indexes["selected_drawer_focus_by_id"][focus.get("selected_drawer_focus_id")] = focus
    indexes["selected_drawer_focus_by_drawer_id"][focus.get("selected_version_detail_drawer_id")] = focus

    return indexes


@lru_cache(maxsize=1)
def build_owner_note_vc_nav_drawer_focus_v195_payload_cached() -> Dict[str, object]:
    pack_194 = _load_pack_194_payload(force_refresh=False)

    selected_navigation = pack_194.get("selected_navigation_preview", {})
    if not isinstance(selected_navigation, dict):
        selected_navigation = {}

    selected_row_ids = _first_list(selected_navigation.get("selected_compare_row_ids"))
    selected_drawer_id = _safe_text(selected_navigation.get("selected_version_detail_drawer_id"))

    breadcrumb = _build_breadcrumb_trail(selected_navigation)
    cards = [
        _build_compare_row_focus_card(row_id=row_id, sequence=idx, selected_drawer_id=selected_drawer_id)
        for idx, row_id in enumerate(selected_row_ids, start=1)
    ]
    groups = _build_focus_groups(cards)
    panel = _build_drawer_action_panel(selected_navigation, cards)
    focus = _build_selected_drawer_focus(selected_navigation, breadcrumb, cards, groups, panel)
    indexes = _build_indexes(cards, groups, focus)

    changed_cards = [card for card in cards if card.get("changed") is True]
    unchanged_cards = [card for card in cards if card.get("changed") is False]

    readiness_checks = {
        "pack_194_ready": pack_194.get("status") == "ready",
        "has_selected_navigation_preview": bool(selected_navigation),
        "selected_drawer_present": bool(selected_drawer_id),
        "has_selected_compare_rows": len(selected_row_ids) >= 75,
        "breadcrumb_trail_ready": breadcrumb.get("trail_status") == "version_compare_navigation_drawer_focus_breadcrumb_preview_ready",
        "has_compare_row_focus_cards": len(cards) >= 75,
        "has_changed_focus_cards": len(changed_cards) >= 1,
        "has_unchanged_focus_cards": len(unchanged_cards) >= 1,
        "all_focus_cards_ready": all(card.get("focus_card_status") == "version_compare_navigation_compare_row_focus_card_preview_ready" for card in cards),
        "has_focus_groups": len(groups) == 3,
        "all_focus_groups_ready": all(group.get("focus_group_status") == "version_compare_navigation_compare_row_focus_group_preview_ready" for group in groups),
        "drawer_action_panel_ready": panel.get("panel_status") == "version_compare_navigation_drawer_action_panel_preview_ready",
        "selected_drawer_focus_ready": focus.get("focus_status") == "version_compare_navigation_selected_drawer_focus_preview_ready",
        "focus_indexes_present": bool(indexes.get("compare_row_focus_cards_by_id")),
        "focus_group_indexes_present": bool(indexes.get("focus_groups_by_id")),
        "selected_focus_indexes_present": bool(indexes.get("selected_drawer_focus_by_id")),
        "all_simulated_only": all(item.get("simulated_only") is True for item in cards + groups),
        "all_selected_drawer_preview_only": focus.get("selected_drawer_preview_only") is True and all(item.get("selected_drawer_preview_only") is True for item in cards + groups),
        "all_compare_row_focus_preview_only": all(item.get("compare_row_focus_preview_only") is True for item in cards + groups),
        "all_navigation_preview_only": all(item.get("navigation_preview_only") is True for item in cards + groups),
        "all_drawer_selection_preview_only": all(item.get("drawer_selection_preview_only") is True for item in cards + groups),
        "no_real_filter_preference_saved": all(item.get("real_filter_preference_saved") is False for item in cards + groups),
        "no_real_navigation_state_persisted": all(item.get("real_navigation_state_persisted") is False for item in cards + groups),
        "no_real_drawer_selection_saved": all(item.get("real_drawer_selection_saved") is False for item in cards + groups),
        "no_real_raw_evidence_revealed": all(item.get("real_raw_evidence_revealed") is False for item in cards + groups),
        "all_filter_preference_saves_blocked": all(item.get("filter_preference_save_allowed_now") is False for item in cards + groups),
        "all_navigation_persistence_blocked": all(item.get("navigation_persistence_allowed_now") is False for item in cards + groups),
        "all_drawer_selection_saves_blocked": all(item.get("drawer_selection_save_allowed_now") is False for item in cards + groups),
        "all_raw_evidence_reveal_blocked": all(item.get("raw_evidence_reveal_allowed") is False for item in cards + groups),
        "cached_non_recursive": True,
    }

    readiness_score = 100 if all(v for v in readiness_checks.values() if isinstance(v, bool)) else 90

    return {
        "pack_id": PACK_ID,
        "pack_number": 195,
        "status": "ready" if readiness_score == 100 else "review",
        "title": "Owner Note Version Compare Navigation Selected Drawer Detail / Compare Row Focus Preview",
        "endpoint": DRAWER_FOCUS_ENDPOINT,
        "source_endpoint": SOURCE_ENDPOINT,
        "generated_at": _utc_now(),
        **_base_flags(),
        "source_pack_194": {
            "status": pack_194.get("status"),
            "readiness_score": pack_194.get("summary", {}).get("readiness_score"),
            "navigation_item_count": pack_194.get("summary", {}).get("navigation_item_count"),
            "drawer_selection_preview_count": pack_194.get("summary", {}).get("drawer_selection_preview_count"),
            "selected_version_detail_drawer_id": pack_194.get("summary", {}).get("selected_version_detail_drawer_id"),
            "selected_compare_row_count": pack_194.get("summary", {}).get("selected_compare_row_count"),
        },
        "summary": {
            "selected_drawer_focus_count": 1 if focus else 0,
            "breadcrumb_count": breadcrumb.get("breadcrumb_count"),
            "compare_row_focus_card_count": len(cards),
            "changed_focus_card_count": len(changed_cards),
            "unchanged_focus_card_count": len(unchanged_cards),
            "focus_group_count": len(groups),
            "drawer_action_count": panel.get("action_count"),
            "selected_version_detail_drawer_id": selected_drawer_id,
            "selected_compare_row_count": len(selected_row_ids),
            "readiness_score": readiness_score,
            "readiness_label": "Owner note selected drawer detail compare row focus preview ready" if readiness_score == 100 else "Owner note selected drawer detail compare row focus preview needs review",
        },
        "readiness_checks": readiness_checks,
        "breadcrumb_trail": breadcrumb,
        "compare_row_focus_cards": cards,
        "focus_groups": groups,
        "drawer_action_panel": panel,
        "selected_drawer_focus": focus,
        "drawer_focus_indexes": indexes,
    }


def build_owner_note_vc_nav_drawer_focus_v195_payload(force_refresh: bool = False) -> Dict[str, object]:
    if force_refresh:
        build_owner_note_vc_nav_drawer_focus_v195_payload_cached.cache_clear()
    return copy.deepcopy(build_owner_note_vc_nav_drawer_focus_v195_payload_cached())


def get_owner_note_vc_nav_drawer_focus_v195_payload(force_refresh: bool = False) -> Dict[str, object]:
    return build_owner_note_vc_nav_drawer_focus_v195_payload(force_refresh=force_refresh)


def build_owner_note_vc_nav_drawer_focus_v195_status_bridge(force_refresh: bool = False) -> Dict[str, object]:
    payload = build_owner_note_vc_nav_drawer_focus_v195_payload(force_refresh=force_refresh)
    summary = payload.get("summary", {})

    return {
        "pack_id": PACK_ID,
        "pack_number": 195,
        "status": payload.get("status"),
        "endpoint": payload.get("endpoint"),
        "source_endpoint": payload.get("source_endpoint"),
        "readiness_score": summary.get("readiness_score"),
        "readiness_label": summary.get("readiness_label"),
        "selected_drawer_focus_count": summary.get("selected_drawer_focus_count"),
        "breadcrumb_count": summary.get("breadcrumb_count"),
        "compare_row_focus_card_count": summary.get("compare_row_focus_card_count"),
        "changed_focus_card_count": summary.get("changed_focus_card_count"),
        "unchanged_focus_card_count": summary.get("unchanged_focus_card_count"),
        "focus_group_count": summary.get("focus_group_count"),
        "drawer_action_count": summary.get("drawer_action_count"),
        "selected_version_detail_drawer_id": summary.get("selected_version_detail_drawer_id"),
        "selected_compare_row_count": summary.get("selected_compare_row_count"),
        **_base_flags(),
    }


def get_owner_note_vc_nav_drawer_focus_v195_status_bridge(force_refresh: bool = False) -> Dict[str, object]:
    return build_owner_note_vc_nav_drawer_focus_v195_status_bridge(force_refresh=force_refresh)


def build_owner_note_vc_nav_drawer_focus_v195_quick_action() -> Dict[str, object]:
    bridge = build_owner_note_vc_nav_drawer_focus_v195_status_bridge()

    action = {
        "id": "owner_note_vc_nav_drawer_focus_v195",
        "label": "Owner Note Drawer Focus",
        "title": "Owner Note Version Compare Navigation Selected Drawer Detail / Compare Row Focus Preview",
        "href": DRAWER_FOCUS_ENDPOINT,
        "endpoint": DRAWER_FOCUS_ENDPOINT,
        "description": "Preview selected drawer focus, compare row focus cards, breadcrumbs, and blocked action panel.",
        "status": bridge.get("status"),
        "pack": "Pack 195",
        "category": "policy",
    }
    action.update(_base_flags())
    return action


def build_owner_note_vc_nav_drawer_focus_v195_unified_owner_section() -> Dict[str, object]:
    payload = build_owner_note_vc_nav_drawer_focus_v195_payload()
    summary = payload.get("summary", {})
    checks = payload.get("readiness_checks", {})

    section = {
        "section_id": "owner_note_vc_nav_drawer_focus_v195",
        "title": "Owner Note Drawer Focus",
        "subtitle": "Preview selected drawer detail, compare row focus cards, and blocked action panel.",
        "status": payload.get("status"),
        "href": DRAWER_FOCUS_ENDPOINT,
        "cards": [
            {"id": "readiness", "title": "Focus readiness", "value": summary.get("readiness_score"), "label": summary.get("readiness_label")},
            {"id": "breadcrumbs", "title": "Breadcrumbs", "value": summary.get("breadcrumb_count"), "label": "Navigation trail"},
            {"id": "focus_cards", "title": "Focus cards", "value": summary.get("compare_row_focus_card_count"), "label": "Compare row focus cards"},
            {"id": "changed", "title": "Changed focus", "value": summary.get("changed_focus_card_count"), "label": "Changed row previews"},
            {"id": "actions", "title": "Drawer actions", "value": summary.get("drawer_action_count"), "label": "Preview/blocked actions"},
            {"id": "persistence", "title": "Persistence", "value": "Blocked" if checks.get("all_drawer_selection_saves_blocked") and checks.get("all_raw_evidence_reveal_blocked") else "Review", "label": "No drawer selection/raw reveal write"},
        ],
    }
    section.update(_base_flags())
    return section


def build_owner_note_vc_nav_drawer_focus_v195_html_section() -> str:
    section = build_owner_note_vc_nav_drawer_focus_v195_unified_owner_section()
    cards = section.get("cards", [])

    card_html = []
    for card in cards:
        card_html.append(
            f"""
            <article class="tower-card owner-note-vc-nav-drawer-focus-v195-card">
                <div class="tower-card-kicker">{card.get('title', '')}</div>
                <div class="tower-card-value">{card.get('value', '')}</div>
                <p>{card.get('label', '')}</p>
            </article>
            """
        )

    return f"""
    <section class="tower-section owner-note-vc-nav-drawer-focus-v195-section" id="owner-note-vc-nav-drawer-focus-v195">
        <div class="tower-section-heading">
            <p class="tower-kicker">Pack 195</p>
            <h2>{section.get('title', 'Owner Note Drawer Focus')}</h2>
            <p>{section.get('subtitle', '')}</p>
            <a class="tower-link-pill" href="{DRAWER_FOCUS_ENDPOINT}">Open selected drawer focus JSON</a>
        </div>
        <div class="tower-card-grid">
            {''.join(card_html)}
        </div>
    </section>
    """


__all__ = [
    "PACK_ID",
    "DRAWER_FOCUS_ENDPOINT",
    "SOURCE_ENDPOINT",
    "build_owner_note_vc_nav_drawer_focus_v195_payload",
    "get_owner_note_vc_nav_drawer_focus_v195_payload",
    "build_owner_note_vc_nav_drawer_focus_v195_status_bridge",
    "get_owner_note_vc_nav_drawer_focus_v195_status_bridge",
    "build_owner_note_vc_nav_drawer_focus_v195_quick_action",
    "build_owner_note_vc_nav_drawer_focus_v195_unified_owner_section",
    "build_owner_note_vc_nav_drawer_focus_v195_html_section",
]
