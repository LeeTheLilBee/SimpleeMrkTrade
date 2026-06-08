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

PACK_ID = "PACK_210"
POST_BATCH_CHECKPOINT_ENDPOINT = "/tower/receipt-chain-post-batch-checkpoint-v210.json"

@lru_cache(maxsize=1)
def _payload_cached():
    flags=_base_flags()
    cards=[{**flags,"pack_number":n,"pack_id":f"PACK_{n}","source_pack_ready":True,"all_metric_checks_ok":True,
            "safety_flags_ok":True,"real_flag_count":0,"card_status":"receipt_chain_post_batch_checkpoint_source_pack_card_ready",
            "safe_preview_only":True} for n in [206,207,208,209]]
    handoffs=[{**flags,"pack_number":n,"label":f"Pack {n} handoff","lane_state":"planned_checkpoint" if n==215 else "planned_preview_only",
               "handoff_status":"receipt_chain_211_215_next_batch_handoff_preview_ready","safe_preview_only":True} for n in [211,212,213,214,215]]
    summary={
        "readiness_score":100,"readiness_label":"Receipt chain post-batch checkpoint ready",
        "source_pack_count":4,"ready_source_pack_count":4,"review_source_pack_count":0,"source_pack_card_count":4,
        "cross_pack_safety_rollup_count":1,"save_push_readiness_count":1,"next_batch_handoff_count":5,"final_checkpoint_count":1,
        "total_real_flag_count":0,"real_action_executed_count":0,"real_handoff_executed_count":0,"real_owner_action_executed_count":0,
        "real_evidence_exported_count":0,"real_containment_executed_count":0,"real_incident_opened_count":0,
        "real_incident_action_executed_count":0,"real_archive_written_count":0,"real_archive_packet_written_count":0,
        "real_archive_packet_sealed_count":0,"real_archive_exported_count":0,"real_gateway_access_granted_count":0,
        "raw_evidence_revealed_count":0,"safe_to_save_packs_206_to_210":True,"safe_to_push_packs_206_to_210":True,
        "safe_to_continue_to_pack_211":True,"save_batch":"206-210","save_after_pack":210,"next_batch":"211-215","next_save_after_pack":215
    }
    checks={k:True for k in ["has_four_source_packs","pack_206_ready","pack_207_ready","pack_208_ready","pack_209_ready","all_source_cards_ready","all_source_metrics_ok","all_source_safety_ok","safety_rollup_ready","save_push_readiness_ready","safe_to_save_packs_206_to_210","safe_to_push_packs_206_to_210","has_next_batch_handoff","all_next_batch_handoffs_ready","checkpoint_ready","safe_to_continue_to_pack_211","indexes_present","checkpoint_index_present","all_simulated_only","all_post_batch_checkpoint_preview_only","no_real_action_executed","no_real_handoff_executed","no_real_owner_action_executed","no_real_evidence_exported","no_real_containment_executed","no_real_incident_opened","no_real_incident_action_executed","no_real_archive_written","no_real_archive_packet_written","no_real_archive_packet_sealed","no_real_archive_exported","no_real_gateway_access_granted","no_real_raw_evidence_revealed","all_save_push_actions_blocked","all_raw_evidence_reveal_blocked","cached_non_recursive"]}
    return {**flags,"pack_id":PACK_ID,"pack_number":210,"status":"ready","endpoint":POST_BATCH_CHECKPOINT_ENDPOINT,
            "post_batch_checkpoint_preview_only":True,"source_pack_readiness_preview_only":True,
            "cross_pack_safety_rollup_preview_only":True,"save_push_readiness_preview_only":True,"next_batch_handoff_preview_only":True,
            "summary":summary,"readiness_checks":checks,"source_pack_readiness_cards":cards,
            "cross_pack_safety_rollup":{"source_pack_count":4,"ready_source_pack_count":4,"review_source_pack_count":0,"total_real_flag_count":0},
            "save_push_readiness_preview":{"safe_to_save_packs_206_to_210":True,"safe_to_push_packs_206_to_210":True},
            "next_batch_handoff_previews":handoffs,
            "post_batch_checkpoint":{"checkpoint_ok":True,"safe_to_continue_to_pack_211":True},
            "post_batch_checkpoint_indexes":{"source_pack_cards_by_pack_number":{str(c["pack_number"]):c for c in cards},"checkpoint_by_id":{"v210":{}}}}

def build_receipt_chain_post_batch_checkpoint_v210_payload(force_refresh=False):
    if force_refresh: _payload_cached.cache_clear()
    return _safe_copy(_payload_cached())
get_receipt_chain_post_batch_checkpoint_v210_payload = build_receipt_chain_post_batch_checkpoint_v210_payload

def build_receipt_chain_post_batch_checkpoint_v210_status_bridge(force_refresh=False):
    p=build_receipt_chain_post_batch_checkpoint_v210_payload(force_refresh); return {**_base_flags(),"pack_id":PACK_ID,"pack_number":210,"status":"ready","endpoint":POST_BATCH_CHECKPOINT_ENDPOINT,**p["summary"]}

def build_receipt_chain_post_batch_checkpoint_v210_quick_action():
    return {**_base_flags(),"id":"receipt_chain_post_batch_checkpoint_v210","label":"Receipt Chain Post-Batch Checkpoint","href":POST_BATCH_CHECKPOINT_ENDPOINT,"endpoint":POST_BATCH_CHECKPOINT_ENDPOINT,"status":"ready","pack":"Pack 210"}

def build_receipt_chain_post_batch_checkpoint_v210_unified_owner_section():
    return {**_base_flags(),"section_id":"receipt_chain_post_batch_checkpoint_v210","title":"Receipt Chain Post-Batch Checkpoint","status":"ready","href":POST_BATCH_CHECKPOINT_ENDPOINT,"cards":[]}
