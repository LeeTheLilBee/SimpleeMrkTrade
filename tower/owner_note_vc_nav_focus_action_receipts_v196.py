
"""
PACK 196 - Owner Note Version Compare Navigation Focus Action
Result / Blocked Action Receipt Preview.

Short module filename:
    tower.owner_note_vc_nav_focus_action_receipts_v196

This module sits on top of Pack 195.

Pack 195 creates preview-only selected drawer focus scaffolding.
Pack 196 creates preview-only action receipts:
- action result preview receipts
- blocked-action receipts
- preview-action receipts
- action safety summary
- receipt indexes
- blocked filter preference/navigation/drawer selection persistence
- blocked raw evidence reveal

Important:
- simulated-only
- action-receipt-preview-only
- blocked-action-receipt-preview-only
- selected-drawer-preview-only
- compare-row-focus-preview-only
- no real filter preference saved
- no real navigation state persisted
- no real drawer selection saved
- no raw evidence reveal
- no real action executed
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


PACK_ID = "PACK_196"
ACTION_RECEIPTS_ENDPOINT = "/tower/owner-note-vc-nav-focus-action-receipts-v196.json"
SOURCE_ENDPOINT = "/tower/owner-note-vc-nav-drawer-focus-v195.json"


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
        "action_receipt_preview_only": True,
        "blocked_action_receipt_preview_only": True,
        "preview_action_receipt_preview_only": True,
        "drawer_action_preview_only": True,
        "selected_drawer_preview_only": True,
        "compare_row_focus_preview_only": True,
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


def _load_pack_195_payload(force_refresh: bool = False) -> Dict[str, object]:
    try:
        mod = importlib.import_module("tower.owner_note_vc_nav_drawer_focus_v195")
        fn = getattr(mod, "build_owner_note_vc_nav_drawer_focus_v195_payload", None)
        if callable(fn):
            payload = fn(force_refresh=force_refresh)
            if isinstance(payload, dict):
                return payload
    except Exception as exc:
        return {
            "pack_id": "PACK_195",
            "status": "review",
            "endpoint": SOURCE_ENDPOINT,
            "summary": {
                "selected_drawer_focus_count": 0,
                "drawer_action_count": 0,
                "selected_compare_row_count": 0,
                "readiness_score": 0,
            },
            "selected_drawer_focus": {},
            "drawer_action_panel": {"actions": []},
            "compare_row_focus_cards": [],
            "focus_groups": [],
            "load_error": str(exc),
            **_base_flags(),
        }

    return {
        "pack_id": "PACK_195",
        "status": "review",
        "endpoint": SOURCE_ENDPOINT,
        "summary": {
            "selected_drawer_focus_count": 0,
            "drawer_action_count": 0,
            "selected_compare_row_count": 0,
            "readiness_score": 0,
        },
        "selected_drawer_focus": {},
        "drawer_action_panel": {"actions": []},
        "compare_row_focus_cards": [],
        "focus_groups": [],
        **_base_flags(),
    }


def _list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _action_outcome(action: Dict[str, object]) -> str:
    action_id = _safe_text(action.get("action_id"))
    allowed = action.get("allowed_in_preview") is True

    if action_id.startswith("blocked_"):
        return "blocked_preview_only"
    if allowed:
        return "preview_ready_no_real_execution"
    return "blocked_preview_only"


def _build_action_receipt(action: Dict[str, object], focus: Dict[str, object], sequence: int) -> Dict[str, object]:
    action_id = _safe_text(action.get("action_id"))
    allowed = action.get("allowed_in_preview") is True
    blocked = not allowed or action_id.startswith("blocked_")
    receipt_kind = "blocked_action_receipt" if blocked else "preview_action_receipt"

    selected_drawer_id = _safe_text(focus.get("selected_version_detail_drawer_id"))
    selected_row_count = int(focus.get("selected_compare_row_count") or 0)

    receipt = {
        "action_receipt_id": f"version_compare_navigation_focus_action_receipt_{_stable_hash((PACK_ID, action_id, selected_drawer_id, sequence), 18)}",
        "action_id": action_id,
        "action_label": action.get("label"),
        "receipt_kind": receipt_kind,
        "sequence": int(sequence),
        "selected_version_detail_drawer_id": selected_drawer_id,
        "selected_navigation_item_id": focus.get("selected_navigation_item_id"),
        "selected_drawer_selection_preview_id": focus.get("selected_drawer_selection_preview_id"),
        "selected_compare_row_count": selected_row_count,
        "allowed_in_preview": allowed,
        "blocked_in_preview": blocked,
        "executes_real_action": False,
        "outcome": _action_outcome(action),
        "reason": "Preview-only action; no persistence or raw evidence reveal." if not blocked else "Blocked by Tower preview safety policy.",
        "receipt_status": "version_compare_navigation_focus_action_receipt_preview_ready",
        "receipt_result_type": "owner_note_version_compare_navigation_focus_action_receipt_preview",
        "safe_preview_only": True,
    }
    receipt.update(_base_flags())

    if blocked:
        receipt["blocked_action_receipt_preview_only"] = True
        receipt["preview_action_receipt_preview_only"] = False
    else:
        receipt["blocked_action_receipt_preview_only"] = False
        receipt["preview_action_receipt_preview_only"] = True

    return receipt


def _build_safety_summary(receipts: List[Dict[str, object]]) -> Dict[str, object]:
    blocked = [item for item in receipts if item.get("blocked_in_preview") is True]
    preview = [item for item in receipts if item.get("blocked_in_preview") is False]

    summary = {
        "action_safety_summary_id": f"version_compare_navigation_focus_action_safety_summary_{_stable_hash((PACK_ID, len(receipts), len(blocked)), 18)}",
        "action_receipt_count": len(receipts),
        "preview_action_receipt_count": len(preview),
        "blocked_action_receipt_count": len(blocked),
        "real_action_executed_count": 0,
        "raw_evidence_revealed_count": 0,
        "persistence_write_count": 0,
        "all_actions_preview_only": True,
        "all_blocked_actions_blocked": all(item.get("blocked_in_preview") is True for item in blocked),
        "all_real_execution_blocked": all(item.get("executes_real_action") is False for item in receipts),
        "summary_status": "version_compare_navigation_focus_action_safety_summary_preview_ready",
        "summary_result_type": "owner_note_version_compare_navigation_focus_action_safety_summary_preview",
        "safe_preview_only": True,
    }
    summary.update(_base_flags())
    return summary


def _build_receipt_groups(receipts: List[Dict[str, object]]) -> List[Dict[str, object]]:
    preview = [item for item in receipts if item.get("blocked_in_preview") is False]
    blocked = [item for item in receipts if item.get("blocked_in_preview") is True]

    group_defs = [
        ("preview_actions", "Preview actions", preview),
        ("blocked_actions", "Blocked actions", blocked),
        ("all_action_receipts", "All action receipts", receipts),
    ]

    groups = []
    for sequence, (group_key, label, items) in enumerate(group_defs, start=1):
        group = {
            "action_receipt_group_id": f"version_compare_navigation_focus_action_receipt_group_{_stable_hash((PACK_ID, group_key), 18)}",
            "action_receipt_group_key": group_key,
            "label": label,
            "sequence": int(sequence),
            "action_receipt_count": len(items),
            "action_receipt_ids": [item.get("action_receipt_id") for item in items],
            "group_status": "version_compare_navigation_focus_action_receipt_group_preview_ready",
            "group_result_type": "owner_note_version_compare_navigation_focus_action_receipt_group_preview",
            "safe_preview_only": True,
        }
        group.update(_base_flags())
        groups.append(group)

    return groups


def _build_selected_action_receipt_preview(receipts: List[Dict[str, object]], focus: Dict[str, object]) -> Dict[str, object]:
    selected = receipts[0] if receipts else {}

    preview = {
        "selected_action_receipt_preview_id": f"version_compare_navigation_selected_action_receipt_{_stable_hash(selected.get('action_receipt_id'), 18)}",
        "selected_action_receipt_id": selected.get("action_receipt_id"),
        "selected_action_id": selected.get("action_id"),
        "selected_receipt_kind": selected.get("receipt_kind"),
        "selected_version_detail_drawer_id": focus.get("selected_version_detail_drawer_id"),
        "selected_compare_row_count": focus.get("selected_compare_row_count"),
        "selection_status": "version_compare_navigation_selected_action_receipt_preview_ready",
        "selection_result_type": "owner_note_version_compare_navigation_selected_action_receipt_preview",
        "safe_preview_only": True,
    }
    preview.update(_base_flags())
    return preview


def _build_indexes(receipts: List[Dict[str, object]], groups: List[Dict[str, object]], selected: Dict[str, object]) -> Dict[str, object]:
    indexes = {
        "action_receipts_by_id": {},
        "action_receipts_by_action_id": {},
        "action_receipts_by_kind": {},
        "action_receipts_by_blocked_state": {"blocked": [], "preview": []},
        "action_receipt_groups_by_id": {},
        "action_receipt_groups_by_key": {},
        "selected_action_receipt_preview_by_id": {},
    }

    for receipt in receipts:
        receipt_id = receipt.get("action_receipt_id")
        action_id = receipt.get("action_id")
        kind = receipt.get("receipt_kind")
        indexes["action_receipts_by_id"][receipt_id] = receipt
        indexes["action_receipts_by_action_id"][action_id] = receipt
        indexes["action_receipts_by_kind"].setdefault(kind, []).append(receipt)
        if receipt.get("blocked_in_preview") is True:
            indexes["action_receipts_by_blocked_state"]["blocked"].append(receipt)
        else:
            indexes["action_receipts_by_blocked_state"]["preview"].append(receipt)

    for group in groups:
        indexes["action_receipt_groups_by_id"][group.get("action_receipt_group_id")] = group
        indexes["action_receipt_groups_by_key"][group.get("action_receipt_group_key")] = group

    indexes["selected_action_receipt_preview_by_id"][selected.get("selected_action_receipt_preview_id")] = selected
    return indexes


@lru_cache(maxsize=1)
def build_owner_note_vc_nav_focus_action_receipts_v196_payload_cached() -> Dict[str, object]:
    pack_195 = _load_pack_195_payload(force_refresh=False)

    focus = pack_195.get("selected_drawer_focus", {})
    if not isinstance(focus, dict):
        focus = {}

    panel = pack_195.get("drawer_action_panel", {})
    if not isinstance(panel, dict):
        panel = {}

    actions = _list(panel.get("actions"))

    receipts = [
        _build_action_receipt(action=action, focus=focus, sequence=idx)
        for idx, action in enumerate(actions, start=1)
        if isinstance(action, dict)
    ]

    blocked_receipts = [item for item in receipts if item.get("blocked_in_preview") is True]
    preview_receipts = [item for item in receipts if item.get("blocked_in_preview") is False]

    safety_summary = _build_safety_summary(receipts)
    groups = _build_receipt_groups(receipts)
    selected_preview = _build_selected_action_receipt_preview(receipts, focus)
    indexes = _build_indexes(receipts, groups, selected_preview)

    readiness_checks = {
        "pack_195_ready": pack_195.get("status") == "ready",
        "has_selected_drawer_focus": bool(focus),
        "has_drawer_action_panel": bool(panel),
        "has_action_receipts": len(receipts) == 5,
        "has_preview_action_receipts": len(preview_receipts) == 3,
        "has_blocked_action_receipts": len(blocked_receipts) == 2,
        "all_action_receipts_ready": all(item.get("receipt_status") == "version_compare_navigation_focus_action_receipt_preview_ready" for item in receipts),
        "blocked_receipts_are_blocked": all(item.get("blocked_in_preview") is True for item in blocked_receipts),
        "preview_receipts_do_not_execute_real_actions": all(item.get("executes_real_action") is False for item in preview_receipts),
        "safety_summary_ready": safety_summary.get("summary_status") == "version_compare_navigation_focus_action_safety_summary_preview_ready",
        "has_receipt_groups": len(groups) == 3,
        "all_receipt_groups_ready": all(group.get("group_status") == "version_compare_navigation_focus_action_receipt_group_preview_ready" for group in groups),
        "selected_action_receipt_preview_ready": selected_preview.get("selection_status") == "version_compare_navigation_selected_action_receipt_preview_ready",
        "receipt_indexes_present": bool(indexes.get("action_receipts_by_id")),
        "receipt_group_indexes_present": bool(indexes.get("action_receipt_groups_by_id")),
        "selected_receipt_index_present": bool(indexes.get("selected_action_receipt_preview_by_id")),
        "all_simulated_only": all(item.get("simulated_only") is True for item in receipts + groups),
        "all_action_receipt_preview_only": all(item.get("action_receipt_preview_only") is True for item in receipts + groups),
        "all_drawer_action_preview_only": all(item.get("drawer_action_preview_only") is True for item in receipts + groups),
        "all_selected_drawer_preview_only": all(item.get("selected_drawer_preview_only") is True for item in receipts + groups),
        "no_real_action_executed": all(item.get("real_action_executed") is False for item in receipts + groups),
        "no_real_filter_preference_saved": all(item.get("real_filter_preference_saved") is False for item in receipts + groups),
        "no_real_navigation_state_persisted": all(item.get("real_navigation_state_persisted") is False for item in receipts + groups),
        "no_real_drawer_selection_saved": all(item.get("real_drawer_selection_saved") is False for item in receipts + groups),
        "no_real_raw_evidence_revealed": all(item.get("real_raw_evidence_revealed") is False for item in receipts + groups),
        "all_action_execution_blocked": all(item.get("action_execution_allowed_now") is False for item in receipts + groups),
        "all_filter_preference_saves_blocked": all(item.get("filter_preference_save_allowed_now") is False for item in receipts + groups),
        "all_navigation_persistence_blocked": all(item.get("navigation_persistence_allowed_now") is False for item in receipts + groups),
        "all_drawer_selection_saves_blocked": all(item.get("drawer_selection_save_allowed_now") is False for item in receipts + groups),
        "all_raw_evidence_reveal_blocked": all(item.get("raw_evidence_reveal_allowed") is False for item in receipts + groups),
        "cached_non_recursive": True,
    }

    readiness_score = 100 if all(v for v in readiness_checks.values() if isinstance(v, bool)) else 90

    return {
        "pack_id": PACK_ID,
        "pack_number": 196,
        "status": "ready" if readiness_score == 100 else "review",
        "title": "Owner Note Version Compare Navigation Focus Action Result / Blocked Action Receipt Preview",
        "endpoint": ACTION_RECEIPTS_ENDPOINT,
        "source_endpoint": SOURCE_ENDPOINT,
        "generated_at": _utc_now(),
        **_base_flags(),
        "source_pack_195": {
            "status": pack_195.get("status"),
            "readiness_score": pack_195.get("summary", {}).get("readiness_score"),
            "selected_drawer_focus_count": pack_195.get("summary", {}).get("selected_drawer_focus_count"),
            "drawer_action_count": pack_195.get("summary", {}).get("drawer_action_count"),
            "selected_version_detail_drawer_id": pack_195.get("summary", {}).get("selected_version_detail_drawer_id"),
            "selected_compare_row_count": pack_195.get("summary", {}).get("selected_compare_row_count"),
        },
        "summary": {
            "action_receipt_count": len(receipts),
            "preview_action_receipt_count": len(preview_receipts),
            "blocked_action_receipt_count": len(blocked_receipts),
            "action_receipt_group_count": len(groups),
            "selected_action_receipt_preview_count": 1 if selected_preview else 0,
            "real_action_executed_count": safety_summary.get("real_action_executed_count"),
            "raw_evidence_revealed_count": safety_summary.get("raw_evidence_revealed_count"),
            "persistence_write_count": safety_summary.get("persistence_write_count"),
            "selected_action_receipt_id": selected_preview.get("selected_action_receipt_id"),
            "selected_version_detail_drawer_id": focus.get("selected_version_detail_drawer_id"),
            "readiness_score": readiness_score,
            "readiness_label": "Owner note focus action receipt preview ready" if readiness_score == 100 else "Owner note focus action receipt preview needs review",
        },
        "readiness_checks": readiness_checks,
        "action_receipts": receipts,
        "action_receipt_groups": groups,
        "action_safety_summary": safety_summary,
        "selected_action_receipt_preview": selected_preview,
        "action_receipt_indexes": indexes,
    }


def build_owner_note_vc_nav_focus_action_receipts_v196_payload(force_refresh: bool = False) -> Dict[str, object]:
    if force_refresh:
        build_owner_note_vc_nav_focus_action_receipts_v196_payload_cached.cache_clear()
    return copy.deepcopy(build_owner_note_vc_nav_focus_action_receipts_v196_payload_cached())


def get_owner_note_vc_nav_focus_action_receipts_v196_payload(force_refresh: bool = False) -> Dict[str, object]:
    return build_owner_note_vc_nav_focus_action_receipts_v196_payload(force_refresh=force_refresh)


def build_owner_note_vc_nav_focus_action_receipts_v196_status_bridge(force_refresh: bool = False) -> Dict[str, object]:
    payload = build_owner_note_vc_nav_focus_action_receipts_v196_payload(force_refresh=force_refresh)
    summary = payload.get("summary", {})

    return {
        "pack_id": PACK_ID,
        "pack_number": 196,
        "status": payload.get("status"),
        "endpoint": payload.get("endpoint"),
        "source_endpoint": payload.get("source_endpoint"),
        "readiness_score": summary.get("readiness_score"),
        "readiness_label": summary.get("readiness_label"),
        "action_receipt_count": summary.get("action_receipt_count"),
        "preview_action_receipt_count": summary.get("preview_action_receipt_count"),
        "blocked_action_receipt_count": summary.get("blocked_action_receipt_count"),
        "action_receipt_group_count": summary.get("action_receipt_group_count"),
        "selected_action_receipt_preview_count": summary.get("selected_action_receipt_preview_count"),
        "real_action_executed_count": summary.get("real_action_executed_count"),
        "raw_evidence_revealed_count": summary.get("raw_evidence_revealed_count"),
        "persistence_write_count": summary.get("persistence_write_count"),
        "selected_action_receipt_id": summary.get("selected_action_receipt_id"),
        "selected_version_detail_drawer_id": summary.get("selected_version_detail_drawer_id"),
        **_base_flags(),
    }


def get_owner_note_vc_nav_focus_action_receipts_v196_status_bridge(force_refresh: bool = False) -> Dict[str, object]:
    return build_owner_note_vc_nav_focus_action_receipts_v196_status_bridge(force_refresh=force_refresh)


def build_owner_note_vc_nav_focus_action_receipts_v196_quick_action() -> Dict[str, object]:
    bridge = build_owner_note_vc_nav_focus_action_receipts_v196_status_bridge()

    action = {
        "id": "owner_note_vc_nav_focus_action_receipts_v196",
        "label": "Owner Note Focus Action Receipts",
        "title": "Owner Note Version Compare Navigation Focus Action Result / Blocked Action Receipt Preview",
        "href": ACTION_RECEIPTS_ENDPOINT,
        "endpoint": ACTION_RECEIPTS_ENDPOINT,
        "description": "Preview action receipts for selected drawer focus actions, including blocked save/reveal receipts.",
        "status": bridge.get("status"),
        "pack": "Pack 196",
        "category": "policy",
    }
    action.update(_base_flags())
    return action


def build_owner_note_vc_nav_focus_action_receipts_v196_unified_owner_section() -> Dict[str, object]:
    payload = build_owner_note_vc_nav_focus_action_receipts_v196_payload()
    summary = payload.get("summary", {})
    checks = payload.get("readiness_checks", {})

    section = {
        "section_id": "owner_note_vc_nav_focus_action_receipts_v196",
        "title": "Owner Note Focus Action Receipts",
        "subtitle": "Preview action receipts for selected drawer focus actions and blocked safety actions.",
        "status": payload.get("status"),
        "href": ACTION_RECEIPTS_ENDPOINT,
        "cards": [
            {"id": "readiness", "title": "Receipt readiness", "value": summary.get("readiness_score"), "label": summary.get("readiness_label")},
            {"id": "receipts", "title": "Action receipts", "value": summary.get("action_receipt_count"), "label": "Total action receipts"},
            {"id": "preview", "title": "Preview receipts", "value": summary.get("preview_action_receipt_count"), "label": "Preview-only action receipts"},
            {"id": "blocked", "title": "Blocked receipts", "value": summary.get("blocked_action_receipt_count"), "label": "Blocked action receipts"},
            {"id": "real_actions", "title": "Real actions", "value": summary.get("real_action_executed_count"), "label": "Real executions"},
            {"id": "persistence", "title": "Persistence", "value": "Blocked" if checks.get("no_real_action_executed") and checks.get("all_raw_evidence_reveal_blocked") else "Review", "label": "No real execution/raw reveal"},
        ],
    }
    section.update(_base_flags())
    return section


def build_owner_note_vc_nav_focus_action_receipts_v196_html_section() -> str:
    section = build_owner_note_vc_nav_focus_action_receipts_v196_unified_owner_section()
    cards = section.get("cards", [])

    card_html = []
    for card in cards:
        card_html.append(
            f"""
            <article class="tower-card owner-note-vc-nav-focus-action-receipts-v196-card">
                <div class="tower-card-kicker">{card.get('title', '')}</div>
                <div class="tower-card-value">{card.get('value', '')}</div>
                <p>{card.get('label', '')}</p>
            </article>
            """
        )

    return f"""
    <section class="tower-section owner-note-vc-nav-focus-action-receipts-v196-section" id="owner-note-vc-nav-focus-action-receipts-v196">
        <div class="tower-section-heading">
            <p class="tower-kicker">Pack 196</p>
            <h2>{section.get('title', 'Owner Note Focus Action Receipts')}</h2>
            <p>{section.get('subtitle', '')}</p>
            <a class="tower-link-pill" href="{ACTION_RECEIPTS_ENDPOINT}">Open focus action receipts JSON</a>
        </div>
        <div class="tower-card-grid">
            {''.join(card_html)}
        </div>
    </section>
    """


__all__ = [
    "PACK_ID",
    "ACTION_RECEIPTS_ENDPOINT",
    "SOURCE_ENDPOINT",
    "build_owner_note_vc_nav_focus_action_receipts_v196_payload",
    "get_owner_note_vc_nav_focus_action_receipts_v196_payload",
    "build_owner_note_vc_nav_focus_action_receipts_v196_status_bridge",
    "get_owner_note_vc_nav_focus_action_receipts_v196_status_bridge",
    "build_owner_note_vc_nav_focus_action_receipts_v196_quick_action",
    "build_owner_note_vc_nav_focus_action_receipts_v196_unified_owner_section",
    "build_owner_note_vc_nav_focus_action_receipts_v196_html_section",
]
