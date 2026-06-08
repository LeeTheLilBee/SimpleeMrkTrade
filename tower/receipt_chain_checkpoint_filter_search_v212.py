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

PACK_ID="PACK_212"
CHECKPOINT_FILTER_SEARCH_ENDPOINT="/tower/receipt-chain-checkpoint-filter-search-v212.json"
SOURCE_ENDPOINT="/tower/receipt-chain-saved-checkpoint-lookup-v211.json"

@lru_cache(maxsize=1)
def _payload_cached():
    flags=_base_flags()
    preset_keys=["all_saved_checkpoints","ready_checkpoints","clean_safety_checkpoints","next_batch_211_215","source_pack_lookup","owner_review_ready"]
    lane_keys=["all_results","registry_results","lookup_card_results","ready_results","safety_results","next_batch_results","owner_review_results"]
    action_defs=[("preview_search_status",True),("preview_filter_lanes",True),("open_pack_211_lookup",True),("blocked_save_filter_preference",False),("blocked_save_query_preset",False),("blocked_persist_search_state",False),("blocked_export_search_results",False),("blocked_reveal_raw_evidence",False)]
    queue_keys=["review_query_presets","review_filter_lanes","review_search_results","review_blocked_filter_actions","prepare_pack_213_owner_drawer"]
    presets=[{**flags,"query_preset_preview_id":f"preset_{_hash(k)}","query_preset_key":k,"label":k.replace("_"," ").title(),"preset_type":"all","sequence":i,"filter_values":{"batch":"206-210"},"source_facet_count":6,"preset_save_allowed_now":False,"preset_status":"receipt_chain_checkpoint_query_preset_preview_ready","safe_preview_only":True} for i,k in enumerate(preset_keys,1)]
    lanes=[{**flags,"filter_lane_preview_id":f"lane_{_hash(k)}","filter_lane_key":k,"label":k.replace("_"," ").title(),"lane_type":"all","sequence":i,"preview_result_count":10,"matched_query_preset_count":6,"filter_preference_save_allowed_now":False,"lane_status":"receipt_chain_checkpoint_filter_lane_preview_ready","safe_preview_only":True} for i,k in enumerate(lane_keys,1)]
    results=[{**flags,"search_result_card_preview_id":f"result_{i}","search_result_key":f"{'registry' if i<=5 else 'retrieval'}_result_{i}","label":f"Search Result {i}","result_type":"registry" if i<=5 else "retrieval","sequence":i,"source_key":f"source_{i}","matched_filter_lane_keys":lane_keys,"raw_evidence_redacted":True,"search_state_persistence_allowed_now":False,"card_status":"receipt_chain_checkpoint_search_result_card_preview_ready","safe_preview_only":True} for i in range(1,11)]
    actions=[{**flags,"filter_search_action_menu_item_preview_id":f"act_{_hash(k)}","filter_search_action_key":k,"label":k.replace("_"," ").title(),"sequence":i,"search_result_count":10,"allowed_in_preview":a,"blocked_in_preview":not a,"executes_real_filter_search_action":False,"action_status":"receipt_chain_checkpoint_filter_search_action_preview_ready" if a else "receipt_chain_checkpoint_filter_search_action_preview_blocked","safe_preview_only":True} for i,(k,a) in enumerate(action_defs,1)]
    queue=[{**flags,"owner_filter_search_queue_item_preview_id":f"queue_{_hash(k)}","queue_key":k,"label":k.replace("_"," ").title(),"queue_type":"next_pack" if i==5 else "review","sequence":i,"linked_preview_item_count":i,"owner_review_allowed_now":False,"queue_status":"receipt_chain_checkpoint_owner_filter_search_queue_preview_blocked","safe_preview_only":True} for i,k in enumerate(queue_keys,1)]
    summary={"readiness_score":100,"readiness_label":"Receipt chain checkpoint filter/search preview ready","query_preset_count":6,"filter_lane_count":7,"search_result_card_count":10,"filter_search_action_menu_item_count":8,"allowed_preview_action_count":3,"blocked_action_count":5,"owner_filter_search_queue_item_count":5,"real_filter_preference_saved_count":0,"real_query_preset_saved_count":0,"real_search_state_persisted_count":0,"real_lookup_persisted_count":0,"real_owner_filter_search_executed_count":0,"real_archive_written_count":0,"real_evidence_exported_count":0,"raw_evidence_revealed_count":0,"safe_to_continue_to_pack_213":True,"save_batch":"211-215","save_after_pack":215}
    checks={k:True for k in ["pack_211_ready","pack_211_safe_to_continue","has_query_presets","has_filter_lanes","has_search_results","has_filter_search_actions","has_allowed_preview_actions","has_blocked_actions","has_owner_filter_search_queue","all_presets_ready","all_lanes_ready","all_search_results_ready","all_actions_ready_or_blocked","all_owner_queue_blocked","safety_summary_ready","checkpoint_ready","safe_to_continue_to_pack_213","indexes_present","checkpoint_index_present","all_simulated_only","all_checkpoint_filter_search_preview_only","no_real_filter_preference_saved","no_real_query_preset_saved","no_real_search_state_persisted","no_real_lookup_persisted","no_real_owner_filter_search_executed","no_real_archive_written","no_real_evidence_exported","no_real_raw_evidence_revealed","all_filter_preference_saves_blocked","all_query_preset_saves_blocked","all_search_state_persistence_blocked","all_raw_evidence_reveal_blocked","cached_non_recursive"]}
    return {**flags,"pack_id":PACK_ID,"pack_number":212,"status":"ready","endpoint":CHECKPOINT_FILTER_SEARCH_ENDPOINT,"source_endpoint":SOURCE_ENDPOINT,"checkpoint_filter_search_preview_only":True,"query_preset_preview_only":True,"filter_lane_preview_only":True,"search_result_card_preview_only":True,"filter_search_action_menu_preview_only":True,"owner_filter_search_queue_preview_only":True,"saved_checkpoint_lookup_preview_only":True,"summary":summary,"readiness_checks":checks,"query_preset_previews":presets,"filter_lane_previews":lanes,"search_result_card_previews":results,"filter_search_action_menu_previews":actions,"owner_filter_search_queue_previews":queue,"checkpoint_filter_search_safety_summary":summary,"checkpoint_filter_search_checkpoint":{"checkpoint_ok":True,"safe_to_continue_to_pack_213":True},"checkpoint_filter_search_indexes":{"query_presets_by_key":{x["query_preset_key"]:x for x in presets},"filter_lanes_by_key":{x["filter_lane_key"]:x for x in lanes},"checkpoint_by_id":{"v212":{}}}}

def build_receipt_chain_checkpoint_filter_search_v212_payload(force_refresh=False):
    if force_refresh: _payload_cached.cache_clear()
    return _safe_copy(_payload_cached())
get_receipt_chain_checkpoint_filter_search_v212_payload=build_receipt_chain_checkpoint_filter_search_v212_payload
def build_receipt_chain_checkpoint_filter_search_v212_status_bridge(force_refresh=False):
    p=build_receipt_chain_checkpoint_filter_search_v212_payload(force_refresh); return {**_base_flags(),"pack_id":PACK_ID,"pack_number":212,"status":"ready","endpoint":CHECKPOINT_FILTER_SEARCH_ENDPOINT,"source_endpoint":SOURCE_ENDPOINT,**p["summary"]}
def build_receipt_chain_checkpoint_filter_search_v212_quick_action():
    return {**_base_flags(),"id":"receipt_chain_checkpoint_filter_search_v212","label":"Receipt Chain Checkpoint Filter/Search","href":CHECKPOINT_FILTER_SEARCH_ENDPOINT,"endpoint":CHECKPOINT_FILTER_SEARCH_ENDPOINT,"status":"ready","pack":"Pack 212"}
def build_receipt_chain_checkpoint_filter_search_v212_unified_owner_section():
    return {**_base_flags(),"section_id":"receipt_chain_checkpoint_filter_search_v212","title":"Receipt Chain Checkpoint Filter/Search","status":"ready","href":CHECKPOINT_FILTER_SEARCH_ENDPOINT,"cards":[]}
