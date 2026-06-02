
"""
PACK 203 - Receipt Chain Evidence Bundle Packet Preview.

Short module filename:
    tower.receipt_chain_evidence_packet_v203

This module sits on top of Pack 202.

Pack 202 created saved-view/filter-preset previews for the operational handoff.
Pack 203 creates preview-only evidence packet structure:
- evidence bundle packet previews
- redacted packet sections
- export request preview, blocked
- owner review checklist preview
- packet integrity summary
- no real export
- no raw evidence reveal
- no saved view/preference writes

Important:
- simulated-only
- evidence-packet-preview-only
- export-preview-only, export-blocked
- raw evidence redacted
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


PACK_ID = "PACK_203"
EVIDENCE_PACKET_ENDPOINT = "/tower/receipt-chain-evidence-packet-v203.json"
SOURCE_ENDPOINT = "/tower/receipt-chain-handoff-saved-views-v202.json"


def _utc_now() -> str:
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def _stable_hash(value: Any, length: int = 18) -> str:
    raw = repr(value).encode("utf-8", errors="ignore")
    return hashlib.sha256(raw).hexdigest()[:length]


def _base_flags() -> Dict[str, object]:
    return {
        "simulated_only": True,
        "evidence_packet_preview_only": True,
        "evidence_bundle_preview_only": True,
        "packet_section_preview_only": True,
        "export_request_preview_only": True,
        "export_blocked": True,
        "raw_evidence_redacted": True,
        "saved_view_preview_only": True,
        "filter_preset_preview_only": True,
        "selected_saved_view_preview_only": True,
        "operational_handoff_preview_only": True,
        "receipt_chain_handoff_preview_only": True,
        "owner_action_menu_preview_only": True,
        "evidence_map_preview_only": True,
        "routing_preview_only": True,
        "raw_evidence_reveal_allowed": False,
        "raw_evidence_lookup_allowed": False,
        "filter_preference_save_allowed_now": False,
        "navigation_persistence_allowed_now": False,
        "drawer_selection_save_allowed_now": False,
        "owner_action_execution_allowed_now": False,
        "handoff_execution_allowed_now": False,
        "evidence_export_allowed_now": False,
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
        "real_handoff_executed": False,
        "real_owner_action_executed": False,
        "real_evidence_exported": False,
        "real_export_request_created": False,
        "real_packet_written": False,
        "real_packet_sealed": False,
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


def _load_pack_202_payload(force_refresh: bool = False) -> Dict[str, object]:
    try:
        mod = importlib.import_module("tower.receipt_chain_handoff_saved_views_v202")
        fn = getattr(mod, "build_receipt_chain_handoff_saved_views_v202_payload", None)
        if callable(fn):
            payload = fn(force_refresh=force_refresh)
            if isinstance(payload, dict):
                return payload
    except Exception as exc:
        return {
            "pack_id": "PACK_202",
            "status": "review",
            "endpoint": SOURCE_ENDPOINT,
            "summary": {"readiness_score": 0},
            "handoff_saved_view_previews": [],
            "handoff_filter_preset_previews": [],
            "selected_handoff_saved_view_preview": {},
            "load_error": str(exc),
            **_base_flags(),
        }

    return {
        "pack_id": "PACK_202",
        "status": "review",
        "endpoint": SOURCE_ENDPOINT,
        "summary": {"readiness_score": 0},
        "handoff_saved_view_previews": [],
        "handoff_filter_preset_previews": [],
        "selected_handoff_saved_view_preview": {},
        **_base_flags(),
    }


def _list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _build_packet_sections(pack_202: Dict[str, object]) -> List[Dict[str, object]]:
    summary = pack_202.get("summary", {}) if isinstance(pack_202.get("summary"), dict) else {}
    selected = pack_202.get("selected_handoff_saved_view_preview", {}) if isinstance(pack_202.get("selected_handoff_saved_view_preview"), dict) else {}

    section_defs = [
        ("handoff_overview", "Handoff overview", "Summary of the selected operational handoff view.", summary.get("selected_handoff_route_count", 0)),
        ("route_packet", "Route packet", "Redacted handoff route evidence.", summary.get("selected_handoff_route_count", 0)),
        ("owner_action_packet", "Owner action packet", "Preview and blocked owner action evidence.", summary.get("selected_owner_action_count", 0)),
        ("evidence_map_packet", "Evidence map packet", "Mapped Packs 196-199 evidence with raw details redacted.", summary.get("selected_evidence_map_item_count", 0)),
        ("next_batch_packet", "Next batch packet", "Preview board for Packs 201-205.", summary.get("selected_next_batch_card_count", 0)),
        ("safety_packet", "Safety packet", "Proof that writes, exports, and raw evidence reveal remain blocked.", 8),
    ]

    sections = []
    for sequence, (section_key, label, description, item_count) in enumerate(section_defs, start=1):
        section = {
            "evidence_packet_section_id": f"receipt_chain_evidence_packet_section_{_stable_hash((PACK_ID, section_key), 18)}",
            "section_key": section_key,
            "label": label,
            "description": description,
            "sequence": sequence,
            "source_saved_view_id": selected.get("selected_saved_view_id"),
            "source_filter_preset_id": selected.get("selected_filter_preset_id"),
            "redacted_item_count": int(item_count or 0),
            "raw_item_count": 0,
            "raw_evidence_redacted": True,
            "section_status": "receipt_chain_evidence_packet_section_preview_ready",
            "section_result_type": "tower_receipt_chain_evidence_packet_section_preview",
            "safe_preview_only": True,
        }
        section.update(_base_flags())
        sections.append(section)

    return sections


def _build_evidence_packets(sections: List[Dict[str, object]]) -> List[Dict[str, object]]:
    packet_defs = [
        ("owner_review_packet", "Owner review packet", ["handoff_overview", "owner_action_packet", "safety_packet"]),
        ("audit_preview_packet", "Audit preview packet", ["handoff_overview", "route_packet", "evidence_map_packet", "safety_packet"]),
        ("next_batch_packet", "Next batch packet", ["next_batch_packet", "safety_packet"]),
    ]

    section_by_key = {section.get("section_key"): section for section in sections}
    packets = []

    for sequence, (packet_key, label, section_keys) in enumerate(packet_defs, start=1):
        matched_sections = [section_by_key[key] for key in section_keys if key in section_by_key]
        packet = {
            "evidence_bundle_packet_preview_id": f"receipt_chain_evidence_bundle_packet_{_stable_hash((PACK_ID, packet_key), 18)}",
            "packet_key": packet_key,
            "label": label,
            "sequence": sequence,
            "section_count": len(matched_sections),
            "section_keys": section_keys,
            "evidence_packet_section_ids": [section.get("evidence_packet_section_id") for section in matched_sections],
            "redacted_item_count": sum(int(section.get("redacted_item_count") or 0) for section in matched_sections),
            "raw_item_count": 0,
            "raw_evidence_redacted": True,
            "export_allowed_now": False,
            "packet_status": "receipt_chain_evidence_bundle_packet_preview_ready",
            "packet_result_type": "tower_receipt_chain_evidence_bundle_packet_preview",
            "safe_preview_only": True,
        }
        packet.update(_base_flags())
        packets.append(packet)

    return packets


def _build_export_requests(packets: List[Dict[str, object]]) -> List[Dict[str, object]]:
    requests = []
    for sequence, packet in enumerate(packets, start=1):
        request = {
            "evidence_export_request_preview_id": f"receipt_chain_evidence_export_request_{_stable_hash((PACK_ID, packet.get('packet_key')), 18)}",
            "packet_key": packet.get("packet_key"),
            "evidence_bundle_packet_preview_id": packet.get("evidence_bundle_packet_preview_id"),
            "label": f"Export {packet.get('label')}",
            "sequence": sequence,
            "requested_format": "redacted_json_preview",
            "export_allowed_now": False,
            "blocked_reason": "Evidence export is preview-only in Pack 203.",
            "raw_evidence_redacted": True,
            "export_status": "receipt_chain_evidence_export_request_preview_blocked",
            "export_result_type": "tower_receipt_chain_evidence_export_request_preview",
            "safe_preview_only": True,
        }
        request.update(_base_flags())
        requests.append(request)

    return requests


def _build_owner_review_checklist(sections: List[Dict[str, object]], packets: List[Dict[str, object]], exports: List[Dict[str, object]]) -> List[Dict[str, object]]:
    checklist_defs = [
        ("confirm_packet_sections", "Confirm packet sections", len(sections) == 6),
        ("confirm_bundle_packets", "Confirm bundle packets", len(packets) == 3),
        ("confirm_exports_blocked", "Confirm exports blocked", all(item.get("export_allowed_now") is False for item in exports)),
        ("confirm_raw_evidence_redacted", "Confirm raw evidence redacted", all(item.get("raw_evidence_redacted") is True for item in sections + packets + exports)),
        ("confirm_no_real_writes", "Confirm no real writes", True),
    ]

    checklist = []
    for sequence, (key, label, complete) in enumerate(checklist_defs, start=1):
        item = {
            "owner_review_checklist_item_id": f"receipt_chain_evidence_packet_checklist_{_stable_hash((PACK_ID, key), 18)}",
            "check_key": key,
            "label": label,
            "sequence": sequence,
            "preview_complete": bool(complete),
            "requires_owner_review_later": key in {"confirm_bundle_packets", "confirm_exports_blocked"},
            "check_status": "receipt_chain_evidence_packet_checklist_item_preview_ready",
            "check_result_type": "tower_receipt_chain_evidence_packet_checklist_preview",
            "safe_preview_only": True,
        }
        item.update(_base_flags())
        checklist.append(item)

    return checklist


def _build_integrity_summary(sections: List[Dict[str, object]], packets: List[Dict[str, object]], exports: List[Dict[str, object]], checklist: List[Dict[str, object]]) -> Dict[str, object]:
    summary = {
        "evidence_packet_integrity_summary_id": f"receipt_chain_evidence_packet_integrity_{_stable_hash((PACK_ID, len(sections), len(packets), len(exports)), 18)}",
        "packet_section_count": len(sections),
        "evidence_bundle_packet_count": len(packets),
        "export_request_preview_count": len(exports),
        "owner_review_checklist_item_count": len(checklist),
        "redacted_item_count": sum(int(section.get("redacted_item_count") or 0) for section in sections),
        "raw_item_count": 0,
        "real_export_request_created_count": 0,
        "real_evidence_exported_count": 0,
        "real_packet_written_count": 0,
        "real_packet_sealed_count": 0,
        "raw_evidence_revealed_count": 0,
        "all_sections_ready": all(section.get("section_status") == "receipt_chain_evidence_packet_section_preview_ready" for section in sections),
        "all_packets_ready": all(packet.get("packet_status") == "receipt_chain_evidence_bundle_packet_preview_ready" for packet in packets),
        "all_exports_blocked": all(export.get("export_status") == "receipt_chain_evidence_export_request_preview_blocked" for export in exports),
        "all_checklist_items_ready": all(item.get("check_status") == "receipt_chain_evidence_packet_checklist_item_preview_ready" for item in checklist),
        "integrity_status": "receipt_chain_evidence_packet_integrity_summary_preview_ready",
        "integrity_result_type": "tower_receipt_chain_evidence_packet_integrity_summary_preview",
        "safe_preview_only": True,
    }
    summary.update(_base_flags())
    return summary


def _build_indexes(sections: List[Dict[str, object]], packets: List[Dict[str, object]], exports: List[Dict[str, object]], checklist: List[Dict[str, object]]) -> Dict[str, object]:
    indexes = {
        "packet_sections_by_id": {},
        "packet_sections_by_key": {},
        "evidence_packets_by_id": {},
        "evidence_packets_by_key": {},
        "export_requests_by_id": {},
        "export_requests_by_packet_key": {},
        "owner_review_checklist_by_id": {},
        "owner_review_checklist_by_key": {},
    }

    for section in sections:
        indexes["packet_sections_by_id"][section.get("evidence_packet_section_id")] = section
        indexes["packet_sections_by_key"][section.get("section_key")] = section

    for packet in packets:
        indexes["evidence_packets_by_id"][packet.get("evidence_bundle_packet_preview_id")] = packet
        indexes["evidence_packets_by_key"][packet.get("packet_key")] = packet

    for export in exports:
        indexes["export_requests_by_id"][export.get("evidence_export_request_preview_id")] = export
        indexes["export_requests_by_packet_key"][export.get("packet_key")] = export

    for item in checklist:
        indexes["owner_review_checklist_by_id"][item.get("owner_review_checklist_item_id")] = item
        indexes["owner_review_checklist_by_key"][item.get("check_key")] = item

    return indexes


@lru_cache(maxsize=1)
def build_receipt_chain_evidence_packet_v203_payload_cached() -> Dict[str, object]:
    pack_202 = _load_pack_202_payload(force_refresh=True)

    sections = _build_packet_sections(pack_202)
    packets = _build_evidence_packets(sections)
    exports = _build_export_requests(packets)
    checklist = _build_owner_review_checklist(sections, packets, exports)
    integrity = _build_integrity_summary(sections, packets, exports, checklist)
    indexes = _build_indexes(sections, packets, exports, checklist)

    readiness_checks = {
        "pack_202_ready": pack_202.get("status") == "ready",
        "has_packet_sections": len(sections) == 6,
        "has_evidence_bundle_packets": len(packets) == 3,
        "has_export_request_previews": len(exports) == 3,
        "has_owner_review_checklist": len(checklist) == 5,
        "all_packet_sections_ready": integrity.get("all_sections_ready") is True,
        "all_packets_ready": integrity.get("all_packets_ready") is True,
        "all_exports_blocked": integrity.get("all_exports_blocked") is True,
        "all_checklist_items_ready": integrity.get("all_checklist_items_ready") is True,
        "integrity_summary_ready": integrity.get("integrity_status") == "receipt_chain_evidence_packet_integrity_summary_preview_ready",
        "indexes_present": bool(indexes.get("packet_sections_by_id")),
        "packet_indexes_present": bool(indexes.get("evidence_packets_by_id")),
        "export_indexes_present": bool(indexes.get("export_requests_by_id")),
        "all_simulated_only": all(item.get("simulated_only") is True for item in sections + packets + exports + checklist),
        "all_evidence_packet_preview_only": all(item.get("evidence_packet_preview_only") is True for item in sections + packets + exports + checklist),
        "all_exports_preview_only": all(item.get("export_request_preview_only") is True for item in exports),
        "all_exports_blocked": all(item.get("export_blocked") is True and item.get("evidence_export_allowed_now") is False for item in exports),
        "all_raw_evidence_redacted": all(item.get("raw_evidence_redacted") is True for item in sections + packets + exports),
        "no_real_export_request_created": all(item.get("real_export_request_created") is False for item in sections + packets + exports + checklist),
        "no_real_evidence_exported": all(item.get("real_evidence_exported") is False for item in sections + packets + exports + checklist),
        "no_real_packet_written": all(item.get("real_packet_written") is False for item in sections + packets + exports + checklist),
        "no_real_packet_sealed": all(item.get("real_packet_sealed") is False for item in sections + packets + exports + checklist),
        "no_real_saved_view_written": all(item.get("real_saved_view_written") is False for item in sections + packets + exports + checklist),
        "no_real_user_preference_written": all(item.get("real_user_preference_written") is False for item in sections + packets + exports + checklist),
        "no_real_action_executed": all(item.get("real_action_executed") is False for item in sections + packets + exports + checklist),
        "no_real_raw_evidence_revealed": all(item.get("real_raw_evidence_revealed") is False for item in sections + packets + exports + checklist),
        "all_evidence_export_blocked": all(item.get("evidence_export_allowed_now") is False for item in sections + packets + exports + checklist),
        "all_raw_evidence_reveal_blocked": all(item.get("raw_evidence_reveal_allowed") is False for item in sections + packets + exports + checklist),
        "cached_non_recursive": True,
    }

    readiness_score = 100 if all(v for v in readiness_checks.values() if isinstance(v, bool)) else 90

    return {
        "pack_id": PACK_ID,
        "pack_number": 203,
        "status": "ready" if readiness_score == 100 else "review",
        "title": "Receipt Chain Evidence Bundle Packet Preview",
        "endpoint": EVIDENCE_PACKET_ENDPOINT,
        "source_endpoint": SOURCE_ENDPOINT,
        "generated_at": _utc_now(),
        **_base_flags(),
        "source_pack_202": {
            "status": pack_202.get("status"),
            "readiness_score": pack_202.get("summary", {}).get("readiness_score"),
            "selected_saved_view_id": pack_202.get("summary", {}).get("selected_saved_view_id"),
            "selected_filter_preset_id": pack_202.get("summary", {}).get("selected_filter_preset_id"),
        },
        "summary": {
            "packet_section_count": len(sections),
            "evidence_bundle_packet_count": len(packets),
            "export_request_preview_count": len(exports),
            "owner_review_checklist_item_count": len(checklist),
            "redacted_item_count": integrity.get("redacted_item_count"),
            "raw_item_count": integrity.get("raw_item_count"),
            "real_export_request_created_count": integrity.get("real_export_request_created_count"),
            "real_evidence_exported_count": integrity.get("real_evidence_exported_count"),
            "real_packet_written_count": integrity.get("real_packet_written_count"),
            "real_packet_sealed_count": integrity.get("real_packet_sealed_count"),
            "raw_evidence_revealed_count": integrity.get("raw_evidence_revealed_count"),
            "save_batch": "201-205",
            "save_after_pack": 205,
            "readiness_score": readiness_score,
            "readiness_label": "Receipt chain evidence packet preview ready" if readiness_score == 100 else "Receipt chain evidence packet preview needs review",
        },
        "readiness_checks": readiness_checks,
        "evidence_packet_sections": sections,
        "evidence_bundle_packet_previews": packets,
        "evidence_export_request_previews": exports,
        "owner_review_checklist": checklist,
        "evidence_packet_integrity_summary": integrity,
        "evidence_packet_indexes": indexes,
    }


def build_receipt_chain_evidence_packet_v203_payload(force_refresh: bool = False) -> Dict[str, object]:
    if force_refresh:
        build_receipt_chain_evidence_packet_v203_payload_cached.cache_clear()
    return copy.deepcopy(build_receipt_chain_evidence_packet_v203_payload_cached())


def get_receipt_chain_evidence_packet_v203_payload(force_refresh: bool = False) -> Dict[str, object]:
    return build_receipt_chain_evidence_packet_v203_payload(force_refresh=force_refresh)


def build_receipt_chain_evidence_packet_v203_status_bridge(force_refresh: bool = False) -> Dict[str, object]:
    payload = build_receipt_chain_evidence_packet_v203_payload(force_refresh=force_refresh)
    summary = payload.get("summary", {})
    return {
        "pack_id": PACK_ID,
        "pack_number": 203,
        "status": payload.get("status"),
        "endpoint": payload.get("endpoint"),
        "source_endpoint": payload.get("source_endpoint"),
        "readiness_score": summary.get("readiness_score"),
        "readiness_label": summary.get("readiness_label"),
        "packet_section_count": summary.get("packet_section_count"),
        "evidence_bundle_packet_count": summary.get("evidence_bundle_packet_count"),
        "export_request_preview_count": summary.get("export_request_preview_count"),
        "owner_review_checklist_item_count": summary.get("owner_review_checklist_item_count"),
        "redacted_item_count": summary.get("redacted_item_count"),
        "raw_item_count": summary.get("raw_item_count"),
        "real_export_request_created_count": summary.get("real_export_request_created_count"),
        "real_evidence_exported_count": summary.get("real_evidence_exported_count"),
        "real_packet_written_count": summary.get("real_packet_written_count"),
        "real_packet_sealed_count": summary.get("real_packet_sealed_count"),
        "raw_evidence_revealed_count": summary.get("raw_evidence_revealed_count"),
        "save_batch": summary.get("save_batch"),
        "save_after_pack": summary.get("save_after_pack"),
        **_base_flags(),
    }


def get_receipt_chain_evidence_packet_v203_status_bridge(force_refresh: bool = False) -> Dict[str, object]:
    return build_receipt_chain_evidence_packet_v203_status_bridge(force_refresh=force_refresh)


def build_receipt_chain_evidence_packet_v203_quick_action() -> Dict[str, object]:
    bridge = build_receipt_chain_evidence_packet_v203_status_bridge()
    action = {
        "id": "receipt_chain_evidence_packet_v203",
        "label": "Receipt Chain Evidence Packet",
        "title": "Receipt Chain Evidence Bundle Packet Preview",
        "href": EVIDENCE_PACKET_ENDPOINT,
        "endpoint": EVIDENCE_PACKET_ENDPOINT,
        "description": "Preview redacted evidence packets and blocked export requests for the handoff chain.",
        "status": bridge.get("status"),
        "pack": "Pack 203",
        "category": "policy",
    }
    action.update(_base_flags())
    return action


def build_receipt_chain_evidence_packet_v203_unified_owner_section() -> Dict[str, object]:
    payload = build_receipt_chain_evidence_packet_v203_payload()
    summary = payload.get("summary", {})
    checks = payload.get("readiness_checks", {})
    section = {
        "section_id": "receipt_chain_evidence_packet_v203",
        "title": "Receipt Chain Evidence Packet",
        "subtitle": "Preview redacted evidence packets and blocked export requests.",
        "status": payload.get("status"),
        "href": EVIDENCE_PACKET_ENDPOINT,
        "cards": [
            {"id": "readiness", "title": "Packet readiness", "value": summary.get("readiness_score"), "label": summary.get("readiness_label")},
            {"id": "sections", "title": "Packet sections", "value": summary.get("packet_section_count"), "label": "Redacted packet sections"},
            {"id": "packets", "title": "Bundle packets", "value": summary.get("evidence_bundle_packet_count"), "label": "Evidence bundle previews"},
            {"id": "exports", "title": "Export requests", "value": summary.get("export_request_preview_count"), "label": "All blocked"},
            {"id": "redacted", "title": "Redacted items", "value": summary.get("redacted_item_count"), "label": "Raw evidence remains hidden"},
            {"id": "safety", "title": "Export safety", "value": "Blocked" if checks.get("all_exports_blocked") and checks.get("all_raw_evidence_redacted") else "Review", "label": "No export/raw reveal"},
        ],
    }
    section.update(_base_flags())
    return section


__all__ = [
    "PACK_ID",
    "EVIDENCE_PACKET_ENDPOINT",
    "SOURCE_ENDPOINT",
    "build_receipt_chain_evidence_packet_v203_payload",
    "get_receipt_chain_evidence_packet_v203_payload",
    "build_receipt_chain_evidence_packet_v203_status_bridge",
    "get_receipt_chain_evidence_packet_v203_status_bridge",
    "build_receipt_chain_evidence_packet_v203_quick_action",
    "build_receipt_chain_evidence_packet_v203_unified_owner_section",
]
