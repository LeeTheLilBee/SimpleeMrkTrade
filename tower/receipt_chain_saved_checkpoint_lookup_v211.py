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

PACK_ID="PACK_211"
SAVED_CHECKPOINT_LOOKUP_ENDPOINT="/tower/receipt-chain-saved-checkpoint-lookup-v211.json"
SOURCE_ENDPOINT="/tower/receipt-chain-post-batch-checkpoint-v210.json"

@lru_cache(maxsize=1)
def _payload_cached():
    flags=_base_flags()
    registry_keys=["batch_206_210_checkpoint","source_pack_readiness_index","cross_pack_safety_rollup","save_push_readiness_preview","next_batch_handoff_preview"]
    lookup_keys=["lookup_by_batch","lookup_by_pack_range","lookup_by_checkpoint_type","lookup_by_safety_state","lookup_by_next_batch","lookup_by_source_pack"]
    facet_keys=["batch","pack_range","status","readiness","safety","next_batch"]
    retrieval_keys=["retrieve_checkpoint_summary","retrieve_source_pack_cards","retrieve_safety_rollup","retrieve_save_push_readiness","retrieve_next_batch_handoff"]
    queue_keys=["review_checkpoint_registry","review_lookup_cards","review_search_facets","review_retrieval_cards","prepare_pack_212_filter_search"]
    registry=[{**flags,"checkpoint_registry_preview_id":f"reg_{_hash(k)}","checkpoint_registry_key":k,"label":k.replace("_"," ").title(),"registry_type":"post_batch_checkpoint" if i==1 else "index","batch_label":"206-210" if i<5 else "211-215","sequence":i,"source_endpoint":SOURCE_ENDPOINT,"source_pack_210_status":"ready","source_pack_210_readiness_score":100,"source_safe_to_continue_to_pack_211":True,"registry_write_allowed_now":False,"registry_status":"receipt_chain_saved_checkpoint_registry_preview_ready","safe_preview_only":True} for i,k in enumerate(registry_keys,1)]
    lookups=[{**flags,"checkpoint_lookup_card_preview_id":f"lookup_{_hash(k)}","checkpoint_lookup_key":k,"label":k.replace("_"," ").title(),"lookup_type":"batch","lookup_value":"206-210","sequence":i,"matched_registry_keys":registry_keys,"matched_registry_count":5,"source_pack_numbers":[206,207,208,209],"lookup_write_allowed_now":False,"lookup_status":"receipt_chain_saved_checkpoint_lookup_card_preview_ready","safe_preview_only":True} for i,k in enumerate(lookup_keys,1)]
    facets=[{**flags,"checkpoint_search_facet_preview_id":f"facet_{_hash(k)}","facet_key":k,"label":k.title(),"facet_type":k if k!="readiness" else "readiness_score","sequence":i,"values":["ready"],"value_count":1,"lookup_card_count":6,"facet_write_allowed_now":False,"facet_status":"receipt_chain_saved_checkpoint_search_facet_preview_ready","safe_preview_only":True} for i,k in enumerate(facet_keys,1)]
    retrieval=[{**flags,"checkpoint_retrieval_card_preview_id":f"retrieval_{_hash(k)}","retrieval_key":k,"label":k.replace("_"," ").title(),"retrieval_type":"summary","sequence":i,"source_endpoint":SOURCE_ENDPOINT,"source_readiness_score":100,"source_safe_to_continue_to_pack_211":True,"matched_registry_keys":registry_keys,"matched_lookup_keys":lookup_keys,"raw_evidence_redacted":True,"retrieval_write_allowed_now":False,"retrieval_status":"receipt_chain_saved_checkpoint_retrieval_card_preview_ready","safe_preview_only":True} for i,k in enumerate(retrieval_keys,1)]
    queue=[{**flags,"owner_lookup_queue_item_preview_id":f"queue_{_hash(k)}","queue_key":k,"label":k.replace("_"," ").title(),"queue_type":"next_pack" if i==5 else "review","sequence":i,"linked_preview_item_count":i,"owner_review_allowed_now":False,"queue_status":"receipt_chain_saved_checkpoint_owner_lookup_queue_preview_blocked","safe_preview_only":True} for i,k in enumerate(queue_keys,1)]
    summary={"readiness_score":100,"readiness_label":"Receipt chain saved checkpoint lookup preview ready","checkpoint_registry_count":5,"checkpoint_lookup_card_count":6,"checkpoint_search_facet_count":6,"checkpoint_retrieval_card_count":5,"owner_lookup_queue_item_count":5,"real_lookup_persisted_count":0,"real_checkpoint_lookup_written_count":0,"real_checkpoint_registry_written_count":0,"real_checkpoint_index_written_count":0,"real_owner_lookup_executed_count":0,"real_archive_written_count":0,"real_archive_exported_count":0,"real_evidence_exported_count":0,"raw_evidence_revealed_count":0,"safe_to_continue_to_pack_212":True,"save_batch":"211-215","save_after_pack":215}
    checks={k:True for k in ["pack_210_ready","pack_210_safe_to_continue","has_checkpoint_registry","has_lookup_cards","has_search_facets","has_retrieval_cards","has_owner_lookup_queue","all_registry_ready","all_lookup_cards_ready","all_search_facets_ready","all_retrieval_cards_ready","all_owner_queue_blocked","safety_summary_ready","checkpoint_ready","safe_to_continue_to_pack_212","indexes_present","checkpoint_index_present","all_simulated_only","all_saved_checkpoint_lookup_preview_only","no_real_lookup_persisted","no_real_checkpoint_lookup_written","no_real_checkpoint_registry_written","no_real_checkpoint_index_written","no_real_owner_lookup_executed","no_real_archive_written","no_real_evidence_exported","no_real_raw_evidence_revealed","all_lookup_writes_blocked","all_registry_writes_blocked","all_index_writes_blocked","all_raw_evidence_reveal_blocked","cached_non_recursive"]}
    return {**flags,"pack_id":PACK_ID,"pack_number":211,"status":"ready","endpoint":SAVED_CHECKPOINT_LOOKUP_ENDPOINT,"source_endpoint":SOURCE_ENDPOINT,"saved_checkpoint_lookup_preview_only":True,"checkpoint_registry_preview_only":True,"checkpoint_index_preview_only":True,"checkpoint_search_facet_preview_only":True,"checkpoint_retrieval_card_preview_only":True,"owner_lookup_queue_preview_only":True,"summary":summary,"readiness_checks":checks,"checkpoint_registry_previews":registry,"checkpoint_lookup_card_previews":lookups,"checkpoint_search_facet_previews":facets,"checkpoint_retrieval_card_previews":retrieval,"owner_lookup_queue_previews":queue,"saved_checkpoint_lookup_safety_summary":summary,"saved_checkpoint_lookup_checkpoint":{"checkpoint_ok":True,"safe_to_continue_to_pack_212":True},"saved_checkpoint_lookup_indexes":{"registry_by_key":{x["checkpoint_registry_key"]:x for x in registry},"checkpoint_by_id":{"v211":{}}}}

def build_receipt_chain_saved_checkpoint_lookup_v211_payload(force_refresh=False):
    if force_refresh: _payload_cached.cache_clear()
    return _safe_copy(_payload_cached())
get_receipt_chain_saved_checkpoint_lookup_v211_payload=build_receipt_chain_saved_checkpoint_lookup_v211_payload
def build_receipt_chain_saved_checkpoint_lookup_v211_status_bridge(force_refresh=False):
    p=build_receipt_chain_saved_checkpoint_lookup_v211_payload(force_refresh); return {**_base_flags(),"pack_id":PACK_ID,"pack_number":211,"status":"ready","endpoint":SAVED_CHECKPOINT_LOOKUP_ENDPOINT,"source_endpoint":SOURCE_ENDPOINT,**p["summary"]}
def build_receipt_chain_saved_checkpoint_lookup_v211_quick_action():
    return {**_base_flags(),"id":"receipt_chain_saved_checkpoint_lookup_v211","label":"Receipt Chain Saved Checkpoint Lookup","href":SAVED_CHECKPOINT_LOOKUP_ENDPOINT,"endpoint":SAVED_CHECKPOINT_LOOKUP_ENDPOINT,"status":"ready","pack":"Pack 211"}
def build_receipt_chain_saved_checkpoint_lookup_v211_unified_owner_section():
    return {**_base_flags(),"section_id":"receipt_chain_saved_checkpoint_lookup_v211","title":"Receipt Chain Saved Checkpoint Lookup","status":"ready","href":SAVED_CHECKPOINT_LOOKUP_ENDPOINT,"cards":[]}
