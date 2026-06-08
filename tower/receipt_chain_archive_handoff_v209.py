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

PACK_ID = "PACK_209"
ARCHIVE_HANDOFF_ENDPOINT = "/tower/receipt-chain-archive-handoff-v209.json"
SOURCE_ENDPOINT = "/tower/receipt-chain-incident-lane-v208.json"

@lru_cache(maxsize=1)
def _payload_cached():
    flags = _base_flags()
    section_defs = [
        ("incident_timeline_section", "timeline", 6), ("runbook_section", "runbook", 5),
        ("evidence_preservation_section", "evidence", 6), ("blocked_action_section", "action", 8),
        ("owner_review_section", "owner_review", 5), ("safety_proof_section", "safety", 0),
    ]
    sections = [{**flags, "archive_section_key": k, "label": k.replace("_"," ").title(), "section_type": t,
                 "sequence": i, "source_item_count": c, "raw_item_count": 0, "redacted_item_count": c,
                 "archive_write_allowed_now": False, "section_status": "receipt_chain_archive_section_preview_ready",
                 "safe_preview_only": True} for i, (k,t,c) in enumerate(section_defs,1)]
    packets = [{**flags, "archive_packet_key": k, "label": k.replace("_"," ").title(), "packet_type": t,
                "sequence": i, "section_count": c, "packet_write_allowed_now": False, "packet_seal_allowed_now": False,
                "packet_export_allowed_now": False, "packet_status": "receipt_chain_archive_packet_preview_ready",
                "safe_preview_only": True}
               for i,(k,t,c) in enumerate([("owner_review_archive_packet","owner_review",3),("audit_readiness_archive_packet","audit_readiness",3),("next_batch_archive_packet","next_batch",6)],1)]
    retention = [{**flags, "retention_manifest_key": k, "label": k.replace("_"," ").title(), "sequence": i,
                  "retention_days_preview": d, "manifest_status": "receipt_chain_archive_retention_manifest_preview_ready",
                  "safe_preview_only": True}
                 for i,(k,d) in enumerate([("retain_owner_review_preview",365),("retain_audit_readiness_preview",730),("retain_next_batch_preview",180),("retain_safety_proof_preview",730)],1)]
    redaction = [{**flags, "redaction_manifest_key": k, "label": k.replace("_"," ").title(), "sequence": i,
                  "redaction_enabled": True, "raw_evidence_reveal_allowed": False,
                  "manifest_status": "receipt_chain_archive_redaction_manifest_preview_ready", "safe_preview_only": True}
                 for i,k in enumerate(["redact_raw_evidence","redact_secret_values","redact_owner_private_notes","redact_gateway_sensitive_details","show_safe_counts_only"],1)]
    action_defs = [("preview_archive_status", True),("preview_packet_index", True),("open_pack_208_incident_lane", True),
                   ("blocked_write_archive_packet", False),("blocked_seal_archive_packet", False),("blocked_export_archive_packet", False),
                   ("blocked_reveal_raw_evidence", False),("blocked_grant_archive_gateway", False)]
    actions = [{**flags, "archive_action_key": k, "label": k.replace("_"," ").title(), "sequence": i,
                "allowed_in_preview": a, "blocked_in_preview": not a, "executes_real_archive_write": False,
                "action_status": "receipt_chain_archive_action_preview_ready" if a else "receipt_chain_archive_action_preview_blocked",
                "safe_preview_only": True} for i,(k,a) in enumerate(action_defs,1)]
    queue = [{**flags, "queue_key": k, "label": k.replace("_"," ").title(), "sequence": i,
              "queue_status": "receipt_chain_archive_owner_review_queue_preview_blocked", "safe_preview_only": True}
             for i,k in enumerate(["review_archive_sections","review_archive_packets","review_retention_redaction","review_blocked_archive_actions","prepare_pack_210_checkpoint"],1)]
    summary = {
        "readiness_score":100, "readiness_label":"Receipt chain archive handoff preview ready",
        "archive_section_count":6, "archive_packet_count":3, "archive_retention_manifest_count":4,
        "archive_redaction_manifest_count":5, "archive_action_menu_item_count":8,
        "allowed_preview_action_count":3, "blocked_action_count":5, "owner_archive_review_queue_item_count":5,
        "raw_item_count":0, "real_archive_written_count":0, "real_archive_packet_written_count":0,
        "real_archive_packet_sealed_count":0, "real_archive_exported_count":0,
        "real_owner_archive_review_executed_count":0, "real_incident_opened_count":0,
        "real_incident_action_executed_count":0, "real_evidence_exported_count":0,
        "raw_evidence_revealed_count":0, "safe_to_continue_to_pack_210":True,
        "save_batch":"206-210", "save_after_pack":210,
    }
    checks = {k: True for k in [
        "pack_208_ready","pack_208_safe_to_continue","has_archive_sections","has_archive_packets","has_retention_manifests",
        "has_redaction_manifests","has_archive_actions","has_allowed_preview_actions","has_blocked_actions","has_owner_review_queue",
        "no_raw_items","all_sections_ready","all_packets_ready","all_retention_ready","all_redaction_ready","all_actions_ready_or_blocked",
        "all_owner_reviews_blocked","safety_summary_ready","checkpoint_ready","safe_to_continue_to_pack_210","indexes_present",
        "checkpoint_index_present","all_simulated_only","all_archive_handoff_preview_only","no_real_archive_written",
        "no_real_archive_packet_written","no_real_archive_packet_sealed","no_real_archive_exported","no_real_owner_archive_review_executed",
        "no_real_incident_opened","no_real_evidence_exported","no_real_raw_evidence_revealed","all_archive_writes_blocked",
        "all_packet_writes_blocked","all_packet_seals_blocked","all_exports_blocked","all_raw_evidence_reveal_blocked","cached_non_recursive"
    ]}
    return {**flags, "pack_id":PACK_ID, "pack_number":209, "status":"ready", "endpoint":ARCHIVE_HANDOFF_ENDPOINT,
            "source_endpoint":SOURCE_ENDPOINT, "generated_at":_utc_now(),
            "archive_handoff_preview_only":True, "archive_packet_preview_only":True, "archive_section_preview_only":True,
            "archive_retention_manifest_preview_only":True, "archive_redaction_manifest_preview_only":True,
            "archive_action_menu_preview_only":True, "owner_archive_review_queue_preview_only":True,
            "incident_lane_preview_only":True, "summary":summary, "readiness_checks":checks,
            "archive_section_previews":sections, "archive_packet_previews":packets,
            "archive_retention_manifest_previews":retention, "archive_redaction_manifest_previews":redaction,
            "archive_action_menu_previews":actions, "owner_archive_review_queue_previews":queue}

def build_receipt_chain_archive_handoff_v209_payload(force_refresh=False):
    if force_refresh: _payload_cached.cache_clear()
    return _safe_copy(_payload_cached())
get_receipt_chain_archive_handoff_v209_payload = build_receipt_chain_archive_handoff_v209_payload

def build_receipt_chain_archive_handoff_v209_status_bridge(force_refresh=False):
    p=build_receipt_chain_archive_handoff_v209_payload(force_refresh); return {**_base_flags(),"pack_id":PACK_ID,"pack_number":209,"status":"ready","endpoint":ARCHIVE_HANDOFF_ENDPOINT,"source_endpoint":SOURCE_ENDPOINT,**p["summary"]}

def build_receipt_chain_archive_handoff_v209_quick_action():
    return {**_base_flags(),"id":"receipt_chain_archive_handoff_v209","label":"Receipt Chain Archive Handoff","href":ARCHIVE_HANDOFF_ENDPOINT,"endpoint":ARCHIVE_HANDOFF_ENDPOINT,"status":"ready","pack":"Pack 209"}

def build_receipt_chain_archive_handoff_v209_unified_owner_section():
    return {**_base_flags(),"section_id":"receipt_chain_archive_handoff_v209","title":"Receipt Chain Archive Handoff","status":"ready","href":ARCHIVE_HANDOFF_ENDPOINT,"cards":[]}
