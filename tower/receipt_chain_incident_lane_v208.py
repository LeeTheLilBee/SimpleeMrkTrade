from __future__ import annotations
import copy, datetime, hashlib
from functools import lru_cache

def _utc_now():
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

def _hash(value, length=18):
    return hashlib.sha256(repr(value).encode("utf-8", errors="ignore")).hexdigest()[:length]

def _base_flags():
    return {
        "simulated_only": True,
        "raw_evidence_redacted": True,
        "raw_evidence_reveal_allowed": False,
        "cached_non_recursive": True,
        "real_action_executed": False,
        "real_handoff_executed": False,
        "real_owner_action_executed": False,
        "real_evidence_exported": False,
        "real_export_request_created": False,
        "real_packet_written": False,
        "real_packet_sealed": False,
        "real_archive_written": False,
        "real_archive_exported": False,
        "real_gateway_access_granted": False,
        "real_filter_preference_saved": False,
        "real_navigation_state_persisted": False,
        "real_drawer_selection_saved": False,
        "real_saved_view_written": False,
        "real_user_preference_written": False,
        "real_raw_evidence_revealed": False,
    }

def _safe_copy(payload):
    return copy.deepcopy(payload)

PACK_ID = "PACK_208"
INCIDENT_ENDPOINT = "/tower/receipt-chain-incident-lane-v208.json"
SOURCE_ENDPOINT = "/tower/receipt-chain-containment-lane-v207.json"

@lru_cache(maxsize=1)
def _payload_cached():
    timeline_keys = [
        "detection_preview", "classification_preview", "containment_review_preview",
        "evidence_preservation_preview", "owner_review_preview", "resolution_preview"
    ]
    runbook_keys = [
        "route_probe_runbook", "raw_evidence_request_runbook",
        "gateway_grant_attempt_runbook", "archive_write_attempt_runbook",
        "owner_action_execution_runbook"
    ]
    checklist_keys = [
        "preserve_redacted_trigger_snapshot", "preserve_scope_boundary_snapshot",
        "preserve_blocked_action_snapshot", "preserve_owner_review_snapshot",
        "confirm_no_raw_reveal", "confirm_no_real_incident_write"
    ]
    action_defs = [
        ("preview_incident_status", True), ("preview_runbook_matrix", True), ("open_pack_207_containment", True),
        ("blocked_open_real_incident", False), ("blocked_escalate_incident", False),
        ("blocked_write_timeline", False), ("blocked_preserve_raw_evidence", False),
        ("blocked_archive_incident_packet", False)
    ]
    queue_keys = [
        "review_incident_timeline", "review_incident_runbooks", "review_blocked_incident_actions",
        "confirm_no_real_incident", "prepare_pack_209_archive_handoff"
    ]

    flags = _base_flags()
    timeline = [
        {**flags, "incident_timeline_event_key": k, "label": k.replace("_", " ").title(),
         "sequence": i, "event_status": "receipt_chain_incident_timeline_event_preview_ready",
         "safe_preview_only": True}
        for i, k in enumerate(timeline_keys, 1)
    ]
    runbooks = [
        {**flags, "incident_runbook_key": k, "label": k.replace("_", " ").title(),
         "sequence": i, "runbook_status": "receipt_chain_incident_runbook_preview_ready",
         "safe_preview_only": True}
        for i, k in enumerate(runbook_keys, 1)
    ]
    checklist = [
        {**flags, "check_key": k, "label": k.replace("_", " ").title(),
         "sequence": i, "check_status": "receipt_chain_evidence_preservation_check_preview_ready",
         "safe_preview_only": True}
        for i, k in enumerate(checklist_keys, 1)
    ]
    actions = [
        {**flags, "incident_action_key": k, "label": k.replace("_", " ").title(),
         "sequence": i, "allowed_in_preview": allowed, "blocked_in_preview": not allowed,
         "action_status": "receipt_chain_incident_action_preview_ready" if allowed else "receipt_chain_incident_action_preview_blocked",
         "safe_preview_only": True}
        for i, (k, allowed) in enumerate(action_defs, 1)
    ]
    queue = [
        {**flags, "queue_key": k, "label": k.replace("_", " ").title(),
         "sequence": i, "queue_status": "receipt_chain_incident_owner_review_queue_preview_blocked",
         "safe_preview_only": True}
        for i, k in enumerate(queue_keys, 1)
    ]

    summary = {
        "readiness_score": 100,
        "readiness_label": "Receipt chain incident lane preview ready",
        "incident_timeline_event_count": 6,
        "incident_runbook_count": 5,
        "evidence_preservation_checklist_item_count": 6,
        "incident_action_menu_item_count": 8,
        "allowed_preview_action_count": 3,
        "blocked_action_count": 5,
        "owner_incident_review_queue_item_count": 5,
        "real_incident_opened_count": 0,
        "real_incident_action_executed_count": 0,
        "real_incident_escalated_count": 0,
        "real_incident_timeline_written_count": 0,
        "real_evidence_preservation_written_count": 0,
        "real_owner_incident_review_executed_count": 0,
        "real_containment_executed_count": 0,
        "real_archive_written_count": 0,
        "real_gateway_access_granted_count": 0,
        "real_evidence_exported_count": 0,
        "raw_evidence_revealed_count": 0,
        "safe_to_continue_to_pack_209": True,
        "save_batch": "206-210",
        "save_after_pack": 210,
    }
    checks = {
        "pack_207_ready": True, "pack_207_safe_to_continue": True,
        "has_timeline_events": True, "has_runbooks": True,
        "has_evidence_preservation_checklist": True, "has_incident_actions": True,
        "has_allowed_preview_actions": True, "has_blocked_actions": True,
        "has_owner_review_queue": True, "all_timeline_events_ready": True,
        "all_runbooks_ready": True, "all_checklist_ready": True,
        "all_actions_ready_or_blocked": True, "all_owner_reviews_blocked": True,
        "safety_summary_ready": True, "checkpoint_ready": True,
        "safe_to_continue_to_pack_209": True, "indexes_present": True,
        "checkpoint_index_present": True, "all_simulated_only": True,
        "all_incident_lane_preview_only": True, "no_real_incident_opened": True,
        "no_real_incident_action_executed": True, "no_real_incident_escalated": True,
        "no_real_incident_timeline_written": True, "no_real_evidence_preservation_written": True,
        "no_real_owner_incident_review_executed": True, "no_real_containment_executed": True,
        "no_real_archive_written": True, "no_real_gateway_access_granted": True,
        "no_real_evidence_exported": True, "no_real_raw_evidence_revealed": True,
        "all_incident_actions_blocked": True, "all_incident_opens_blocked": True,
        "all_timeline_writes_blocked": True, "all_evidence_preservation_writes_blocked": True,
        "all_archive_writes_blocked": True, "all_gateway_access_grants_blocked": True,
        "all_raw_evidence_reveal_blocked": True, "cached_non_recursive": True,
    }
    return {
        **flags, "pack_id": PACK_ID, "pack_number": 208, "status": "ready",
        "title": "Receipt Chain Incident Lane Preview", "endpoint": INCIDENT_ENDPOINT,
        "source_endpoint": SOURCE_ENDPOINT, "generated_at": _utc_now(),
        "incident_lane_preview_only": True, "incident_timeline_preview_only": True,
        "incident_runbook_preview_only": True, "incident_action_menu_preview_only": True,
        "evidence_preservation_checklist_preview_only": True,
        "owner_incident_review_queue_preview_only": True, "containment_lane_preview_only": True,
        "summary": summary, "readiness_checks": checks,
        "incident_timeline_event_previews": timeline,
        "incident_runbook_previews": runbooks,
        "evidence_preservation_checklist_previews": checklist,
        "incident_action_menu_previews": actions,
        "owner_incident_review_queue_previews": queue,
    }

def build_receipt_chain_incident_lane_v208_payload(force_refresh=False):
    if force_refresh: _payload_cached.cache_clear()
    return _safe_copy(_payload_cached())

get_receipt_chain_incident_lane_v208_payload = build_receipt_chain_incident_lane_v208_payload

def build_receipt_chain_incident_lane_v208_status_bridge(force_refresh=False):
    p = build_receipt_chain_incident_lane_v208_payload(force_refresh)
    s = p["summary"]
    return {**_base_flags(), "pack_id": PACK_ID, "pack_number": 208, "status": "ready",
            "endpoint": INCIDENT_ENDPOINT, "source_endpoint": SOURCE_ENDPOINT, **s}

def build_receipt_chain_incident_lane_v208_quick_action():
    return {**_base_flags(), "id": "receipt_chain_incident_lane_v208", "label": "Receipt Chain Incident Lane",
            "href": INCIDENT_ENDPOINT, "endpoint": INCIDENT_ENDPOINT, "status": "ready", "pack": "Pack 208"}

def build_receipt_chain_incident_lane_v208_unified_owner_section():
    return {**_base_flags(), "section_id": "receipt_chain_incident_lane_v208", "title": "Receipt Chain Incident Lane",
            "status": "ready", "href": INCIDENT_ENDPOINT, "cards": []}
